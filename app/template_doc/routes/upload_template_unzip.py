import zipfile
import shutil
import io, os, json, base64
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException, Body
from fastapi.responses import StreamingResponse
from typing import List
from exceptions.error import ErrorCode
from exceptions.command_exception import APIException
import unicodedata
import uuid

# 导入创建模板的函数与模型以便在解压后直接创建
from app.template_doc.routes.create_template_view import create_template, create_python_setting_file
from app.template_doc.model.template_doc import TemplateDoc
from constants.template_constant import TemplateType, ExperimentType, TemplateOriginType

router = APIRouter()
UPLOAD_DIR = Path("output/templates")
EXTRACT_DIR = Path("output/extracted_templates")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
EXTRACT_DIR.mkdir(parents=True, exist_ok=True)


@router.post('/upload_template_unzip')
async def upload_template_unzip(file: UploadFile = File(...), save_zip: bool = False):
    if not file.filename or not file.filename.lower().endswith('.zip'):
        raise APIException(ErrorCode.ONLY_ZIP_FILES_SUPPORTED)

    # 1. 基础路径准备
    # 为本次上传生成随机目录，避免不同上传之间目录冲突
    random_dir = f"{uuid.uuid4().hex}"
    extract_to = EXTRACT_DIR / random_dir

    try:
        extract_to.mkdir(parents=True, exist_ok=True)
        file_bytes = await file.read()

        # 解压实现：对文件名尝试修正编码（优先 GBK，再 UTF-8），同时做基本安全检查
        with zipfile.ZipFile(io.BytesIO(file_bytes), 'r') as zip_ref:
            for member in zip_ref.infolist():
                orig_name = member.filename
                # 尝试修复可能的编码问题
                try:
                    if member.flag_bits & 0x800:
                        # UTF-8 标志已设置，直接使用
                        name = orig_name
                    else:
                        # zipfile 在 Python 中默认把文件名按 cp437 解码，恢复原始字节再尝试常见编码
                        raw = orig_name.encode('cp437', errors='replace')
                        try:
                            name = raw.decode('gbk')
                        except Exception:
                            try:
                                name = raw.decode('utf-8')
                            except Exception:
                                name = orig_name
                except Exception:
                    name = orig_name

                # 统一分隔符并去掉前导斜杠
                name = name.replace('\\', '/').lstrip('/')

                # 跳过 macOS 元数据和资源 fork（会产生 ._ 文件或 __MACOSX 目录）以及常见无用文件
                if name.startswith('__MACOSX/'):
                    continue

                # 跳过空名、绝对路径或包含上级引用的条目
                if not name:
                    continue
                if '..' in Path(name).parts:
                    continue
                # 只使用文件名的 basename，把所有文件放到同一临时目录下，避免产生多余子目录
                base_name = Path(name).name
                # 跳过 macOS 产生的资源文件或无用文件，如 ._xxx 或 .DS_Store
                if not base_name or base_name.startswith('._') or base_name == '.DS_Store':
                    continue
                if not base_name:
                    continue

                target_path = extract_to / base_name

                # 若发现冲突（同名文件已存在），通过追加序号避免覆盖
                if target_path.exists():
                    stem = Path(base_name).stem
                    suf = Path(base_name).suffix
                    i = 1
                    while True:
                        candidate = extract_to / f"{stem}_{i}{suf}"
                        if not candidate.exists():
                            target_path = candidate
                            break
                        i += 1

                # 写出文件（保持原始二进制内容不做任何编码转换）
                target_path.parent.mkdir(parents=True, exist_ok=True)
                with zip_ref.open(member) as src, target_path.open('wb') as dst:
                    shutil.copyfileobj(src, dst)

        # 5. 收集文件列表 (增强稳定性)
        docx_files = []
        py_files = []
        json_info = None
        
        # 重新扫描磁盘，并确保返回的是 utf-8 字符串
        for p in extract_to.rglob('*'):
            if not p.is_file():
                continue
            
            # 使用 relative_to 获取相对路径，并强制转换为字符串
            # 在某些 Linux 环境下，可能需要 p.as_posix() 统一斜杠方向
            raw_rel = p.relative_to(extract_to).as_posix()
            rel = unicodedata.normalize('NFC', raw_rel)
            suffix = p.suffix.lower()
            if suffix == '.docx':
                docx_files.append(rel)
            elif suffix == '.py':
                py_files.append(rel)
            elif suffix == '.json':
                json_info = rel # 这里现在拿到的就是修复后的路径了

        # 如果存在 config.json，尝试按配置自动调用 create_template 并替换 python 文件
        processed = []
        if json_info:
            config_path = extract_to / json_info
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            except Exception:
                try:
                    with open(config_path, 'r', encoding='gbk', errors='ignore') as f:
                        config = json.load(f)
                except Exception:
                    config = None

            if isinstance(config, dict):
                # helper to resolve enum values from config (支持 decs 文本或 name 或直接数字)
                def _resolve_enum(enum_cls, val):
                    if val is None:
                        return 0
                    if isinstance(val, int):
                        return val
                    if isinstance(val, str):
                        # 尝试按描述匹配
                        decs_map = enum_cls.generate_decs_value_map()
                        if val in decs_map:
                            return decs_map[val]
                        # 按 name 匹配
                        name_map = enum_cls.generate_name_value_map()
                        if val in name_map:
                            return name_map[val]
                        # 直接尝试去除空白后匹配
                        v2 = val.strip()
                        if v2 in decs_map:
                            return decs_map[v2]
                        if v2 in name_map:
                            return name_map[v2]
                    return 0

                for rel in docx_files:
                    stem = Path(rel).stem
                    cfg = config.get(stem)
                    if not cfg:
                        continue
                    template_type_cfg = cfg.get('template_type')
                    experiment_type_cfg = cfg.get('experiment_type')
                    industry_type_cfg = cfg.get('industry_type', '')

                    template_type_val = _resolve_enum(TemplateType, template_type_cfg)
                    experiment_type_val = _resolve_enum(ExperimentType, experiment_type_cfg)

                    # 读取 docx 内容并调用 create_template
                    try:
                        docx_path = extract_to / rel
                        with open(docx_path, 'rb') as df:
                            doc_bytes = df.read()
                        content_b64 = base64.b64encode(doc_bytes).decode('utf-8')

                        # 先检查数据库是否已存在同名模板，若存在则更新，否则创建新模板
                        existing = await TemplateDoc.get_or_none(name=stem, is_del=0)
                        if existing:
                            try:
                                existing.template_content = content_b64
                                existing.type = template_type_val
                                existing.experiment_type = experiment_type_val
                                existing.industry_type = industry_type_cfg
                                existing.origin_type = TemplateOriginType.user_change.value
                                await existing.save()
                                # 重新生成 python 配置并保存（create_python_setting_file 内会更新数据库）
                                try:
                                    await create_python_setting_file(template_id=existing.id, name=stem, template_file_steam=io.BytesIO(doc_bytes), connection=None, title_mapping=None, old_template_name=None)
                                except Exception:
                                    pass
                                processed.append({'name': stem, 'template_id': existing.id, 'action': 'updated'})
                            except Exception:
                                # 更新失败则继续尝试创建新模板
                                template_id = await create_template(name=stem, content_base64=content_b64, content=doc_bytes,
                                                                    template_type=template_type_val,
                                                                    industry_type=industry_type_cfg,
                                                                    experiment_type=experiment_type_val)
                                processed.append({'name': stem, 'template_id': template_id, 'action': 'created'})
                        else:
                            template_id = await create_template(name=stem, content_base64=content_b64, content=doc_bytes,
                                                                template_type=template_type_val,
                                                                industry_type=industry_type_cfg,
                                                                experiment_type=experiment_type_val)
                            processed.append({'name': stem, 'template_id': template_id, 'action': 'created'})

                        # 如果 ZIP 中包含与 docx 同名的 .py 文件，则覆盖生成的 template_structure/<name>.py 并更新数据库
                        candidate_py = extract_to / f"{stem}.py"
                        if candidate_py.exists():
                            dest_py_folder = Path('template_structure')
                            dest_py_folder.mkdir(parents=True, exist_ok=True)
                            dest_py = dest_py_folder / f"{stem}.py"
                            shutil.copy2(candidate_py, dest_py)
                            # 读取新的 python 配置内容（尝试 utf-8，回退到 gbk）
                            try:
                                with open(dest_py, 'r', encoding='utf-8') as pf:
                                    new_py_content = pf.read()
                            except Exception:
                                with open(dest_py, 'r', encoding='gbk', errors='ignore') as pf:
                                    new_py_content = pf.read()
                            try:
                                template_doc = await TemplateDoc.get_or_none(id=template_id)
                                if template_doc:
                                    template_doc.python_config = new_py_content
                                    await template_doc.save()
                            except Exception:
                                # 忽略数据库更新错误，但文件已替换
                                pass
                    except Exception:
                        # 单个模板创建失败时继续处理下一个
                        continue
        # 上传处理完成：删除刚才创建的临时解压目录，避免占用磁盘空间
        try:
            if extract_to.exists():
                shutil.rmtree(extract_to)
        except Exception:
            pass

        return {
            "code": 200,
            "message": "Template unzipped successfully",
            "data": {
                "extracted_dir": str(extract_to),
                "docx": docx_files,
                "py": py_files,
                "json_info": json_info,
                "processed": processed
            }
        }
    except Exception as e:
        # 出错时也尝试删除临时目录
        try:
            if extract_to.exists():
                shutil.rmtree(extract_to)
        except Exception:
            pass
        return {"code": 500, "message": f"Error: {str(e)}"}


@router.post('/download_template_zip')
async def download_template_zip(payload: dict = Body(...)):
    """
    接收多个 template_id，打包对应的 .docx、.py（若存在）和 config.json 返回 zip 流。
    返回的 config.json 内容格式为 {"template_name": {"template_type": "desc", "experiment_type": "desc", "industry_type": "..."}}
    """
    try:
        # 兼容前端多种传参方式：单 id、list 或 包含 template_id/template_ids 的对象
        template_ids = []
        if isinstance(payload, dict):
            if 'template_ids' in payload:
                template_ids = payload.get('template_ids') or []
            elif 'template_id' in payload:
                template_ids = payload.get('template_id')
            else:
                # 也可能带有其他字段（responseType 等），尝试读取常见字段名
                template_ids = payload.get('ids') or payload.get('ids[]') or []
        elif isinstance(payload, list):
            template_ids = payload
        else:
            template_ids = payload

        # 规范为整数列表
        if isinstance(template_ids, int):
            template_ids = [template_ids]
        if isinstance(template_ids, str):
            template_ids = [int(x) for x in template_ids.split(',') if x.strip().isdigit()]
        if not isinstance(template_ids, list):
            try:
                template_ids = list(template_ids)
            except Exception:
                template_ids = []

        if not template_ids:
            raise APIException(ErrorCode.AT_LEAST_ONE_TEMPLATE_ID)

        files_to_add = []  # list of tuples (arcname, bytes)
        config = {}
        missing = []
        for tid in template_ids:
            tpl = await TemplateDoc.get_or_none(id=tid, is_del=0)
            if not tpl:
                missing.append(tid)
                continue

            name = tpl.name
            # decode base64 content
            try:
                doc_bytes = base64.b64decode(tpl.template_content)
            except Exception:
                # 如果不是 base64 或出错，尝试直接使用 bytes
                doc_bytes = tpl.template_content.encode('utf-8') if isinstance(tpl.template_content, str) else bytes(tpl.template_content)

            docx_name = f"{name}.docx"
            files_to_add.append((docx_name, doc_bytes))

            # 尝试获取 .py: 优先使用磁盘上的 template_structure/<name>.py，其次使用 tpl.python_config
            py_path = Path('template_structure') / f"{name}.py"
            py_bytes = None
            if py_path.exists():
                try:
                    with open(py_path, 'rb') as pf:
                        py_bytes = pf.read()
                except Exception:
                    py_bytes = None
            elif tpl.python_config:
                try:
                    py_bytes = tpl.python_config.encode('utf-8')
                except Exception:
                    py_bytes = str(tpl.python_config).encode('utf-8', errors='ignore')

            if py_bytes:
                files_to_add.append((f"{name}.py", py_bytes))

            # 准备 config 映射（使用 desc 文本以便人可读）
            try:
                t_desc = TemplateType.get_name_desc_by_value(int(tpl.type)) if tpl.type is not None else ''
            except Exception:
                t_desc = ''
            try:
                e_desc = ExperimentType.get_name_desc_by_value(int(tpl.experiment_type)) if tpl.experiment_type is not None else ''
            except Exception:
                e_desc = ''
            config[name] = {
                'template_type': t_desc,
                'experiment_type': e_desc,
                'industry_type': tpl.industry_type or ''
            }

        # 生成 config.json
        config_bytes = json.dumps(config, ensure_ascii=False, indent=4).encode('utf-8')
        files_to_add.append(('config.json', config_bytes))

        # 创建 zip 到内存
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
            for arcname, bts in files_to_add:
                zf.writestr(arcname, bts)
        zip_buffer.seek(0)

        # 返回流
        headers = {'Content-Disposition': 'attachment; filename="templates.zip"'}
        return StreamingResponse(zip_buffer, media_type='application/zip', headers=headers)
    except Exception as e:
        raise APIException(ErrorCode.SAVE_TEMPLATE_FAILED)
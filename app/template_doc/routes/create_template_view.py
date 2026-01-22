import base64, os, json, shutil
from io import BytesIO
from zipfile import BadZipFile
from typing import Dict, Optional

import jinja2
from docxtpl import DocxTemplate
from docx import Document
from fastapi import APIRouter, UploadFile, File, Form
from tortoise.transactions import in_transaction
from app.template_doc.model.template_doc import TemplateDoc
from app.template_doc.model.template_doc_base import TemplateDocBase
from app.template_doc.model.template_bookmark import TemplateBookmark
from app.template_doc.model.template_extra_info import TemplateExtraInfo
from utils.LoadAndDelete import AnalysisBookMark
from utils.doc_converter import convert_doc_to_docx, detect_file_format
from exceptions.error import ErrorCode
from exceptions.command_exception import APIException
from constants.template_constant import TemplateBookMarkType, TemplateOriginType, TemplateType, ExperimentType
from app.db import execute_safe_sql
from utils.log_decorator import log_response
import importlib

router = APIRouter()

# class InputSchema(BaseModel):
#     name: str = Field(None, description='模板名称')

@router.post('/upload_template')
@log_response
async def create_template_view(
    name: str = Form(None, description='模板名称'),
    template_type: int = Form(0, description=f"""模板类型 \n
                     {TemplateType.original_records.decs}: {TemplateType.original_records.value} \n
                     {TemplateType.report_template.decs}:{TemplateType.report_template.value} \n
                     {TemplateType.calibration_template.decs}:{TemplateType.calibration_template.value} \n
                     {TemplateType.installation_acceptance_template.decs}:{TemplateType.installation_acceptance_template.value}"""),
    experiment_type: int = Form(0, description=f"""实验类型 \n
                     {ExperimentType.spectral_scanning.decs}: {ExperimentType.spectral_scanning.value} \n
                     {ExperimentType.time_scanning.decs}:{ExperimentType.time_scanning.value} \n
                     {ExperimentType.quantitative_determination.decs}:{ExperimentType.quantitative_determination.value} \n
                     {ExperimentType.photometric_measurement.decs}:{ExperimentType.photometric_measurement.value}"""),
    industry_type: str = Form(None, description='行业类型'),
    file: UploadFile = File(..., description='模板文件')
    ):
    try:
        original_file_name = file.filename
        if '.docx' in original_file_name:
            docx_name = original_file_name.split('.docx')[0]
        elif '.doc' in original_file_name:
            docx_name = original_file_name.split('.doc')[0] 
        else:
            raise APIException(ErrorCode.INVALID_DOCX_FORMAT)
        if name:
            if await TemplateDocBase.get_or_none(name=name, is_del=0):
                raise APIException(ErrorCode.TEMPLATE_NAME_EXIST)
        else:
            if await TemplateDocBase.get_or_none(name=docx_name, is_del=0):
                raise APIException(ErrorCode.TEMPLATE_NAME_EXIST)
            name = docx_name
        content = await file.read()

        # 检测文件格式并自动转换DOC到DOCX
        file_format = detect_file_format(content)
        if file_format == 'doc':
            print(f"检测到DOC文件，正在转换为DOCX: {file.filename}")
            try:
                docx_stream = convert_doc_to_docx(content)
                content = docx_stream.read()  # 获取转换后的字节内容
                print(f" DOC文件转换成功: {file.filename}")
            except Exception as e:
                print(f" DOC文件转换失败: {e}")
                raise APIException(ErrorCode.INVALID_DOCX_FORMAT)
        elif file_format == 'docx':
            print(f"检测到DOCX文件: {file.filename}")
        else:
            print(f" 不支持的文件格式: {file.filename}")
            raise APIException(ErrorCode.INVALID_DOCX_FORMAT)

        content_base64 = base64.b64encode(content).decode('utf-8')
        # 存入数据库
        try:
            template_id = await create_template(name, content_base64, content, 
            template_type=template_type, industry_type=industry_type, experiment_type=experiment_type)
        except BadZipFile:
            raise APIException(ErrorCode.INVALID_DOCX_FORMAT) 
    except APIException as e:
        raise e
    except Exception as e:
        import traceback
        traceback.print_exc()
        # 返回统一错误
        raise APIException(ErrorCode.SAVE_TEMPLATE_FAILED)
    return {'code': 200, 'message': '模板保存成功', 'data': {'id': template_id}}


async def create_template(name: str, content_base64: str, content: bytes, template_type: int = 0, 
    industry_type: str = '', experiment_type: int = 0, title_mapping: Optional[Dict[str, Dict]] = None, old_template_name: Optional[str] = None) -> int:
    if template_type in [TemplateType.report_template.value, TemplateType.original_records.value]:
        async with in_transaction('default') as connection:
            create_info = {
                'name': name,
                'template_content': content_base64,
                'experiment_type': experiment_type,
                'type': template_type, # 模版类型
                'industry_type': industry_type,
            }
            if old_template_name:
                create_info['origin_type'] = TemplateOriginType.user_change.value
            # 先创建base模型，方便以后回滚
            template_base_instance = await TemplateDocBase.create(**create_info)
            # 创建模版
            create_info['base_template_id'] = template_base_instance.id
            template =  await TemplateDoc.create(**create_info)
            # 创建标签
            analysis_bookmark = AnalysisBookMark(BytesIO(content))
            book_markets = analysis_bookmark.get_word_bookmarks()
            # 创建json文件
            for book_mark in book_markets:
                await recursion_create_bookmark(book_mark, template.id)     
            await create_python_setting_file(template_id = template.id, name=name, template_file_steam=BytesIO(content), 
            connection=connection, title_mapping=title_mapping, old_template_name=old_template_name)
            return template.id
    else:
        return 0


async def recursion_create_bookmark(bookmark, template_id, parent_id=None):
    if bookmark.get('name') and bookmark.get('id') and bookmark.get('type') is not None:
        create_info = {
            'name': bookmark['name'],
            'type': bookmark['type'],
            'description': bookmark['description'] if bookmark.get('description') else None,
            'sort_order': bookmark['sort_order'] if bookmark.get('sort_order') else 0,
            'parent_id': parent_id,
            'template_doc_id': template_id,
            'font': bookmark['font'] if bookmark.get('font') else None,
            'font_size': bookmark['font_size'] if bookmark.get('font_size') else None,
            'image_size': bookmark['image_size'] if bookmark.get('image_size') else None
        }
        new_bookmark = await TemplateBookmark.create(**create_info)
        # 如果是表格 并且有表格结构
        # if new_bookmark.type == TemplateBookMarkType.sheet.value and bookmark.get('table_structure'):
        #     bookmark_id= new_bookmark.id
        #     structure_type = bookmark.get('table_structure').get('structure_type')
        #     if structure_type is not None:  # 可能是0 0也是正确的
        #         table_structure = bookmark.get('table_structure')
        #         bookmark_data = await BookmarkData.create(bookmark_id=bookmark_id, structure_type=structure_type, table_structure=table_structure)
        #         bookmark_name = bookmark.get('name')
        #         book_mark_tpl_name = bookmark_name + '_tpl' # 这个代表这个表格有tpl横向表格
        #         for child in bookmark.get("children"):
        #             if child.get('name') == book_mark_tpl_name:
        #                 # 反过来更新BookmarkData的table_structure字段，添加has_tr标识
        #                 updated_table_structure = bookmark_data.table_structure
        #                 updated_table_structure['has_tr'] = 1
        #                 # 更新BookmarkData记录
        #                 bookmark_data.table_structure = updated_table_structure
        #                 await bookmark_data.save()

            
                
        for child in bookmark['children']:
            if child.get('name') and child.get('id'):
                await recursion_create_bookmark(child, template_id, new_bookmark.id)

async def create_python_setting_file(template_id: int, name: str, template_file_steam: BytesIO, connection=None, title_mapping: Optional[Dict[str, Dict]] = None, old_template_name: Optional[str] = None) -> str:
    """
    创建模板的 Python 设置文件，包含字段定义和 title_mapping
    
    Args:
        template_id: 模板 ID
        name: 新文件名称
        template_file_steam: 模板文件流
        connection: 数据库连接
        title_mapping: 传入的 title_mapping 字典（可选）
        old_template_name: 原始模板名称（可选），如果提供则复制该文件并替换 title_mapping
    """
    py_folders = 'template_structure'
    os.makedirs(py_folders, exist_ok=True)

    # 如果传入了 old_template_name 和 title_mapping，复制旧文件并替换 title_mapping
    if old_template_name and title_mapping:
        old_py_path = os.path.join(py_folders, f"{old_template_name}.py")
        
        # 检查旧文件是否存在
        if os.path.exists(old_py_path):
            print(f"DEBUG: 找到旧模板文件: {old_py_path}，复制并更新 title_mapping")
            
            # 读取旧文件内容
            with open(old_py_path, "r", encoding="utf-8") as f:
                old_content = f.read()
            
            # 替换 title_mapping 部分
            # 找到 title_mapping = { 和下一个 } 之间的内容
            import re
            
            # 构建新的 title_mapping 内容
            new_title_mapping_lines = ["title_mapping = {\n"]
            title_vars = list(title_mapping.keys())
            for i, var in enumerate(title_vars):
                mapping_info = title_mapping[var]
                title_text = mapping_info.get('name', var.replace('_t', ''))
                font = mapping_info.get('font', '宋体')
                font_size = mapping_info.get('font_size', 12)
                
                comma = "," if i < len(title_vars) - 1 else ""
                new_title_mapping_lines.append(f"    '{var}': {{'name': '{title_text}', 'font': '{font}', 'font_size': {font_size}}}{comma}\n")
            new_title_mapping_lines.append("}\n")
            
            new_title_mapping_str = "".join(new_title_mapping_lines)
            
            # 使用正则表达式替换 title_mapping 部分
            pattern = r'title_mapping = \{[\s\S]*?\n\}\n'
            new_content = re.sub(pattern, new_title_mapping_str, old_content)
            
            # 保存为新文件
            new_py_path = os.path.join(py_folders, f"{name}.py")
            backup_path = os.path.join(py_folders, f"{name}_back.py")
            
            # 如果新文件已存在，先备份
            if os.path.exists(new_py_path):
                shutil.copy2(new_py_path, backup_path)
            
            # 写入新文件
            with open(new_py_path, "w", encoding="utf-8", newline='\n') as f:
                f.write(new_content)
            
            # 同步存入数据库
            template_doc = await TemplateDoc.get_or_none(id=template_id)
            if template_doc:
                template_doc.python_config = new_content
                await template_doc.save()
                print(f"DEBUG: Python配置已存入数据库（复制模式），template_id={template_id}")
            
            print(f"DEBUG: 新模板文件已创建: {new_py_path}")
            return new_py_path
        else:
            print(f"DEBUG: 旧模板文件不存在: {old_py_path}，使用标准流程生成")
    
    # 标准流程：从模板中提取信息并生成文件
    # 提取模板中的变量和字体信息
    doc = DocxTemplate(template_file_steam)
    try:
        context_vars = doc.get_undeclared_template_variables()
        # 分离：_t 结尾的（标题）和非 _t 结尾的（值）
        title_vars = [var for var in context_vars if var.endswith('_t')]
        value_vars = [var for var in context_vars if not var.endswith('_t')]
    except jinja2.exceptions.TemplateSyntaxError as e:
        print(e)
        raise APIException(ErrorCode.INVALID_TEMPLATE_FIELD)

    # 如果没有传入 title_mapping，则从模板和 common_data 中提取
    if not title_mapping:
        # 加载 common_data 的 title_mapping（用于查询已有的标题描述）
        try:
            common_mod = importlib.import_module('template_structure.common_data')
            common_title_mapping = common_mod.title_mapping if hasattr(common_mod, 'title_mapping') else {}
        except Exception as e:
            print(f"加载 common_data title_mapping 失败: {e}")
            common_title_mapping = {}

        # 使用 python-docx 读取字体信息
        template_file_steam.seek(0)
        docx_doc = Document(template_file_steam)
        
        # 建立占位符到字体信息的映射
        var_font_info = {}
        for para in docx_doc.paragraphs:
            text = para.text
            for var in context_vars:
                if var in text:
                    # 从该段落的 run 中获取字体信息
                    for run in para.runs:
                        if var in run.text:
                            font_name = run.font.name or '宋体'  # 默认宋体
                            font_size = run.font.size
                            if font_size:
                                font_size_pt = font_size / 20  # 转换为磅
                            else:
                                # 从样式继承
                                style_font_size = para.style.font.size
                                font_size_pt = style_font_size / 20 if style_font_size else 12
                            
                            var_font_info[var] = {
                                'font': font_name,
                                'font_size': int(font_size_pt)
                            }
                            break
        
        # 构建 title_mapping 用于生成文件
        title_mapping = {}
        for var in title_vars:
            # 从 common_data 中查找对应的文字描述
            common_entry = common_title_mapping.get(var)
            
            # 如果 common_entry 是字典，从中提取 'name'；否则当字符串使用
            if isinstance(common_entry, dict):
                title_text = common_entry.get('name', var.replace('_t', ''))
                # 如果字典中已有字体信息，优先使用
                if 'font' in common_entry:
                    font_info = {
                        'font': common_entry['font'],
                        'font_size': common_entry.get('font_size', 12)
                    }
                else:
                    font_info = var_font_info.get(var, {'font': '宋体', 'font_size': 12})
            else:
                title_text = common_entry or var.replace('_t', '')  # 如果没找到，就用变量名
                font_info = var_font_info.get(var, {'font': '宋体', 'font_size': 12})
            
            title_mapping[var] = {
                'name': title_text,
                'font': font_info['font'],
                'font_size': font_info['font_size']
            }
    
    # 生成 Python 文件内容
    py_lines = [
        "# 模板字段定义\n",
        "# fill_type: 0 表示从模板中提取的字段, fill_type: 1 表示表格截取的字段\n\n",
        "# get_type: 0: 表示从通用数据中取, 1: 表示从接口中取 2: 表从数据库中取\n\n",
        "from .common_data import BaseTableDataHandler, checkbox\n",
        "python_template_var = {\n"
    ]

    # 写入值变量
    for i, var in enumerate(value_vars):
        comma = "," if i < len(value_vars) - 1 else ""
        py_lines.append(f'    "{var}": {{"fill_type": 0}}{comma}\n')

    py_lines.append("}\n")

    # 生成 title_mapping（带字体信息）
    py_lines.append("\n# 标题映射（包含字体和字号信息）\n")
    py_lines.append("title_mapping = {\n")

    for i, var in enumerate(title_vars):
        if var in title_mapping:
            mapping_info = title_mapping[var]
            title_text = mapping_info.get('name', var.replace('_t', ''))
            font = mapping_info.get('font', '宋体')
            font_size = mapping_info.get('font_size', 12)
        else:
            # 备用：如果没有在 title_mapping 中找到，使用默认值
            title_text = var.replace('_t', '')
            font = '宋体'
            font_size = 12
    
        # 构建字典（单行格式）
        comma = "," if i < len(title_vars) - 1 else ""
        py_lines.append(f"    '{var}': {{'name': '{title_text}', 'font': '{font}', 'font_size': {font_size}}}{comma}\n")

    py_lines.append("}\n")

    # 获取表格结构
    table_list = []
    tables = await get_table_structure_by_template_name(template_id=template_id, template_name=name, connection=connection)
    if tables:
        for table in tables:
            table_structure = json.loads(table.get('table_structure'))
            table_list.append(table_structure)

    # 自定义书签
    extra_info = {
        'remark': {'value': '', 'font_size': 12, 'font': '宋体'},  # 备注
        'page_num_type': 0
    }

    # 添加 custom_bookmark 到生成的文件中
    py_lines.append("\n# 字段渲染表格\n")
    py_lines.append("extra_info = {\n")
    for key, values in extra_info.items():
        # 根据值的类型决定如何格式化
        if isinstance(values, dict):
            # 字典类型，使用 repr() 保持字典格式
            py_lines.append(f"    '{key}': {values},  # 备注\n")
        elif isinstance(values, (int, float)):
            # 数字类型，不加引号
            py_lines.append(f"    '{key}': {values}\n")
        else:
            # 字符串类型，加引号
            py_lines.append(f"    '{key}': '{values}'\n")
    py_lines.append("}\n\n")

    py_lines.append("table_fields = ")
    table_fields_str = json.dumps(table_list, indent=4, ensure_ascii=False, separators=(',', ': '))
    table_fields_str = table_fields_str.replace("null", "None")
    py_lines.append(f"{table_fields_str}\n")

    # 创建文件
    py_path = os.path.join(py_folders, f"{name}.py")
    backup_path = os.path.join(py_folders, f"{name}_back.py")

    # 如果原文件存在，先备份
    if os.path.exists(py_path):
        shutil.copy2(py_path, backup_path)

    # 合并所有行为完整内容
    python_config_content = "".join(py_lines)

    # 写入文件
    with open(py_path, "w", encoding="utf-8", newline='\n') as f:
        f.write(python_config_content)
    
    # 同步存入数据库
    template_doc = await TemplateDoc.get_or_none(id=template_id)
    if template_doc:
        template_doc.python_config = python_config_content
        await template_doc.save()
        print(f"DEBUG: Python配置已存入数据库，template_id={template_id}")
 
    return py_path

async def get_table_structure_by_template_name(template_id, template_name, connection):
    sql_text = """
    select bookmark_data.table_structure from template_doc 
    inner join template_bookmark on template_doc.id = template_bookmark.template_doc_id 
    inner join bookmark_data on template_bookmark.id = bookmark_data.bookmark_id 
    where template_doc.name = %s and template_doc.id = %s and template_bookmark.type = %s and template_doc.is_del = %s
    and bookmark_data.table_structure is not null
    """
    sql_result = await execute_safe_sql(sql_text, [template_name, template_id,TemplateBookMarkType.sheet.value, 0], return_dict=True, connection=connection)
    
    print(f"Debug: Found {len(sql_result)} table_structure records")
    return sql_result

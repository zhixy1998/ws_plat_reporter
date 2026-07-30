# 标准库导入
import io
import os
import time
import base64
import tempfile
import subprocess
from io import BytesIO
from typing import List, Optional, Union

# 第三方库导入
from docx import Document
from fastapi import APIRouter
from urllib.parse import quote
from tortoise import connections
from pydantic import BaseModel, Field
from fastapi.responses import StreamingResponse

# 本地应用导入
from exceptions.error import ErrorCode
from utils.log_decorator import log_response
from ..model.template_doc import TemplateDoc
from ..model.template_bookmark import TemplateBookmark
from app.classic_template_doc.routes.classic_create_template_view import create_template as classic_create_template
from .create_template_view import create_template
from utils.fille_template_utils import FillDataUtils
from exceptions.command_exception import APIException
from utils.handle_header_footer import set_header_footer
from utils.template_utils import get_doc_obj_by_template_id, get_title_mapping
from utils.doc_converter import get_libreoffice_command, get_libreoffice_subprocess_kwargs, explain_libreoffice_returncode, get_libreoffice_timeout_seconds
from constants.template_constant import TemplatePageNumType, MeasureMode, TemplateFootAndHeaderType
from config import config
from utils.EditDocxXML import fill_word_bookmark
from utils.classic_html_builder import ClassicHtmlBuilder

router = APIRouter()

class BookmarkItem(BaseModel):
    bm_id: Optional[int] = Field(None, description="书签id，更新时传入")
    desc_t: str = Field(None, description="time_mapping 的key")
    font: Optional[str] = Field(None, description="字体")
    font_size: Optional[Union[int, float]] = Field(None, description="字号")
    value: Optional[str] = Field(None, description="书签内容")


class InputSchema(BaseModel):
    template_id: int = Field(..., description='模板id')
    bookmark_list: List[BookmarkItem] = Field(None, description='标签名称列表')
    title_list: List[BookmarkItem] = Field(None, description='报告名称')
    header: Optional[BookmarkItem] = Field(None, description='页眉')
    footer: Optional[BookmarkItem] = Field(None, description='页脚')
    operation_type: int = Field(None, description='操作类型 0: 预览 1:另存为 2: 保存')
    name: str = Field(None, description='模板名称 当另存为的时候传入')
    remark: Optional[BookmarkItem]= Field(None, description='备注')
    project_name: Optional[BookmarkItem] = Field(None, description='动态项目名称')
    page_num_type: str = Field(TemplatePageNumType.no_page.value, description='页码类型')
    header_position: Optional[str] = Field(None, description='页眉位置: 左边展示/居中展示/右边展示')
    footer_position: Optional[str] = Field(None, description='页脚位置: 左边展示/居中展示/右边展示')
    measure_mode: int = Field(None, description='测量模式 1:默认 2:仅测量标签位置不修改标签字体大小')
    margin: Optional[str] = Field(None, description='动态边距(mm)')
    orientation: Optional[int] = Field(None, description='横向/纵向 0=纵向 1=横向')
    line_height: Optional[str] = Field(None, description='行边距')



class DataSchema(BaseModel):
    file_base64: str = Field(..., description='文件base64')


def _desc_to_position(desc: Optional[str]) -> str:
    """将 TemplateFootAndHeaderType 描述文本映射为 CSS position 值（'left'/'center'/'right'）。"""
    if not desc:
        return 'center'
    _VALUE_TO_POS = {
        TemplateFootAndHeaderType.left.value: 'left',
        TemplateFootAndHeaderType.center.value: 'center',
        TemplateFootAndHeaderType.right.value: 'right',
    }
    decs_value_map = TemplateFootAndHeaderType.generate_decs_value_map()
    value = decs_value_map.get(desc)
    return _VALUE_TO_POS.get(value, 'center')


@router.post('/update_bookmark')
@log_response
async def update_bookmark(data: InputSchema):
    if data.measure_mode == MeasureMode.classic.value:
        class_db_con = connections.get('classic_db')
        template = await TemplateDoc.get_or_none(id=data.template_id).using_db(class_db_con)
    else:
        template = await TemplateDoc.get_or_none(id=data.template_id)
    if not template:
        raise APIException(ErrorCode.TEMPLATE_NOT_FOUND)
    template_name = template.name
    origin_title_mapping = get_title_mapping(template_name, measure_mode=data.measure_mode)
    operation_type = data.operation_type
    input_title_mapping = data.bookmark_list
    title_list = data.title_list
    new_title_mapping = {}
    for item in input_title_mapping:
        new_title_mapping[item.desc_t] = {
            'name': item.value,
            'font': item.font,
            'font_size': item.font_size
        }
    if operation_type == 1:  # 另存为
        new_name = data.name
        if not new_name:
            raise APIException(ErrorCode.TEMPLATE_NAME_EMPTY)
        # 合并标题映射
        merged_title_mapping = {k: new_title_mapping[k] for k in origin_title_mapping if k in new_title_mapping}
        content_base64 = template.template_content
        content = base64.b64decode(content_base64)
        thumbnail_base64 = template.thumbnail_base64

        is_classic_save = data.measure_mode == MeasureMode.classic.value
        if not is_classic_save and (data.header or data.footer):
            # 非经典模式：DOCX 里插入页眉页脚
            doc_stream = BytesIO(content)
            doc = Document(doc_stream)
            if data.header:
                set_header_footer(doc, header_text=data.header.value, header_font_name=data.header.font, header_font_size=data.header.font_size)
            if data.footer:
                set_header_footer(doc, footer_text=data.footer.value, footer_font_name=data.footer.font, footer_font_size=data.footer.font_size)

            if title_list:
                doc_stream = await insert_title(title_list, doc, data.template_id, data.measure_mode)

            doc = Document(doc_stream)
            content_stream = BytesIO()
            doc.save(content_stream)
            content = content_stream.getvalue()
            content_base64 = base64.b64encode(content)

        if data.measure_mode == MeasureMode.classic.value:
            await classic_create_template(new_name, content_base64, template_type=template.type, thumbnail_base64=thumbnail_base64, experiment_type=template.experiment_type)
            # 创建 .py 配置文件（从原模板复制，更新 title_mapping、标题、页眉页脚、页码）
            page_num = None
            if data.page_num_type:
                _VALUE_TO_POS = {
                    TemplatePageNumType.left_page.value: 'left',
                    TemplatePageNumType.center_page.value: 'center',
                    TemplatePageNumType.right_page.value: 'right',
                }
                decs_value_map = TemplatePageNumType.generate_decs_value_map()
                value = decs_value_map.get(data.page_num_type)
                if value is not None and value != TemplatePageNumType.no_page.value:
                    pos = _VALUE_TO_POS.get(value)
                    page_num = {'position': pos, 'font': '宋体', 'font_size': 9}
                elif value == TemplatePageNumType.no_page.value:
                    page_num = {}  # 空 dict 表示删除页码配置
            _save_classic_config_file(template_name, new_name, merged_title_mapping, data.header, data.footer, title_list, page_num, data.margin, data.orientation, data.line_height,
                header_position=_desc_to_position(data.header_position) if data.header_position else None,
                footer_position=_desc_to_position(data.footer_position) if data.footer_position else None)
        else:
            await create_template(data.name, content_base64, content=content, template_type=template.type, 
        industry_type=template.industry_type, experiment_type=template.experiment_type, 
        title_mapping=merged_title_mapping, old_template_name=template_name)
        return {'code': 200, 'message': '模板另存为成功', 'data': {'file_base64': ''}}

    else:  # 预览

        # ---- 经典模式：从 DB 取 HTML 模板，Playwright 渲染 PDF ----
        if data.measure_mode == MeasureMode.classic.value:

            # 从 title_mapping 构建 contexts（_t = 标签名，值留空，_fs/_font = 字号/字体）
            contexts = {}
            for key, info in new_title_mapping.items():
                if key.endswith('_t'):
                    base = key[:-2]
                    contexts[key] = info.get('name', '')           # 标签
                    contexts[base] = ''                             # 值留空
                    if info.get('font_size'):
                        contexts[base + '_fs'] = info['font_size']
                    if info.get('font'):
                        contexts[base + '_font'] = info['font']

            if data.remark and data.remark.value:
                contexts['备注'] = data.remark.value

            # 标题列表（前端传过来的修改后名称）
            if title_list:
                contexts['__title_list__'] = [
                    {'name': getattr(t, 'desc_t', ''), 'value': t.value, 'font': t.font, 'font_size': t.font_size}
                    for t in title_list
                ]

            # 从配置文件读取标题、页码、页眉页脚（前端传的会覆盖）
            try:
                from utils.template_utils import import_template_module
                mod = import_template_module(config.classic_structure_module, template_name)
                if hasattr(mod, 'extra_info'):
                    ei = mod.extra_info
                    # 页码：前端 page_num_type 优先，否则用配置文件
                    if 'page_num' in ei:
                        contexts['__page_num__'] = dict(ei['page_num'])
                    # 配置文件默认值（会被前端覆盖）
                    contexts.setdefault('__title_list__', ei.get('title_list', []))
                    contexts.setdefault('__header__', ei.get('header', {}))
                    contexts.setdefault('__footer__', ei.get('footer', {}))
            except Exception:
                pass

            # 前端传的覆盖配置文件（使用 TemplatePageNumType 常量映射）
            if data.page_num_type:
                _VALUE_TO_POS = {
                    TemplatePageNumType.left_page.value: 'left',
                    TemplatePageNumType.center_page.value: 'center',
                    TemplatePageNumType.right_page.value: 'right',
                }
                decs_value_map = TemplatePageNumType.generate_decs_value_map()
                value = decs_value_map.get(data.page_num_type)
                if value is not None and value != TemplatePageNumType.no_page.value:
                    pos = _VALUE_TO_POS.get(value, 'center')
                    contexts.setdefault('__page_num__', {})['position'] = pos
                else:
                    # 不展示页码：清除配置文件中的默认值
                    contexts.pop('__page_num__', None)
            if data.header and data.header.value:
                contexts['__header__'] = {
                    'value': data.header.value,
                    'font': data.header.font or '宋体',
                    'font_size': data.header.font_size or 10,
                    'position': _desc_to_position(data.header_position),
                }
            if data.footer and data.footer.value:
                contexts['__footer__'] = {
                    'value': data.footer.value,
                    'font': data.footer.font or '宋体',
                    'font_size': data.footer.font_size or 9,
                    'position': _desc_to_position(data.footer_position),
                }
            # 边距 / 横向纵向 / 行边距（前端传的覆盖配置文件）
            if data.margin is not None:
                contexts['__margin__'] = {'value': data.margin}
            if data.orientation is not None:
                contexts['__orientation__'] = {'value': data.orientation}
            if data.line_height is not None:
                contexts['__line_height__'] = {'value': data.line_height}

            # 从 DB 获取 HTML 模板字符串
            html_template_str = _get_html_from_template(template)
            builder = ClassicHtmlBuilder(template_html=html_template_str)
            try:
                pdf_bytes = builder.build_pdf(contexts)
            except Exception as e:
                print(f"ERROR: ClassicHtmlBuilder 渲染失败: {e}")
                import traceback
                traceback.print_exc()
                raise APIException(ErrorCode.CONVERT_PDF_FAILED)

            filename = f"{template_name}_filled.pdf"
            safe_name = quote(filename)
            return StreamingResponse(
                BytesIO(pdf_bytes),
                media_type="application/pdf",
                headers={
                    "Content-Disposition": f"attachment; filename*=UTF-8''{safe_name}",
                    "Content-Length": str(len(pdf_bytes)),
                },
            )

        # ---- 新模式：沿用原有 DOCX + LibreOffice 流程 ----
        # doc = await get_doc_obj_by_template_id(template_id=data.template_id)

        content_bytes = base64.b64decode(template.template_content)
        doc_stream = BytesIO(content_bytes)
        doc = Document(doc_stream)

        # 处理页眉页脚
        header_info = data.header
        if header_info:
            set_header_footer(doc, header_text=header_info.value, header_font_name=header_info.font, header_font_size=header_info.font_size)
        footer_info = data.footer
        if footer_info:
            set_header_footer(doc, footer_text=footer_info.value, footer_font_name=footer_info.font, footer_font_size=footer_info.font_size)
        if title_list:
            doc_stream = await insert_title(title_list, doc, data.template_id, data.measure_mode)
            doc = Document(doc_stream)
        
        print(f"Section 0 Header Paragraphs: {len(doc.sections[0].header.paragraphs)}") 
        output_stream = BytesIO()
        doc.save(output_stream)
        output_stream.seek(0)

        # 先获取原始字节数据
        doc_raw_bytes = output_stream.getvalue()
    
        # 为显示创建流（处理docxtpl标识）
        show_output_stream = BytesIO(doc_raw_bytes)
        if data.measure_mode == MeasureMode.classic.value:
            fill_data_utils = FillDataUtils(template_name, fake=True, new_title_mapping=new_title_mapping, template=template, structure_path=config.classic_structure_module)
        else:
            fill_data_utils = FillDataUtils(template_name, fake=True, new_title_mapping=new_title_mapping, template=template, structure_path=config.structure_module)
        # DEBUG: inspect show_output_stream before preview
        try:
            show_output_stream.seek(0)
            size_before = len(show_output_stream.getvalue())
        except Exception:
            size_before = None
        print(f"DEBUG: before preview_view, show_output_stream type={type(show_output_stream)}, size={size_before}")
        doc_stream = await fill_data_utils.preview_view(doc_stream=show_output_stream, remark=data.remark.value if data.remark else None)
        # DEBUG: inspect returned doc_stream
        if doc_stream is None:
            print("ERROR: preview_view returned None")
            raise APIException(ErrorCode.TEMPLATE_NOT_FOUND)
        try:
            doc_stream.seek(0)
            size_after = len(doc_stream.getvalue())
        except Exception:
            size_after = None
        print(f"DEBUG: after preview_view, doc_stream type={type(doc_stream)}, size={size_after}")
        # 根据页码类型处理
        # 从字符串描述转换为对应的value值
        template_desc_value_map = TemplatePageNumType.generate_decs_value_map()
        page_num_value = template_desc_value_map.get(data.page_num_type)
        
        if page_num_value != TemplatePageNumType.no_page.value:
            doc_stream = fill_data_utils.insert_header_page_number(doc_stream, alignment=page_num_value)

        # 获取 Word 字节内容
        doc_stream.seek(0)
        word_bytes = doc_stream.read()

        try:
            pdf_bytes = convert_docx_to_pdf(word_bytes)
        except Exception as e:
            print(f"ERROR: convert_docx_to_pdf failed: {e}")
            raise APIException(ErrorCode.CONVERT_PDF_FAILED)

        # ========== DEBUG 模式：保存中间文件到硬盘（需要时取消注释） ==========
        # debug_word_path = os.path.join(os.getcwd(), "debug_template.docx")
        # with open(debug_word_path, "wb") as f:
        #     f.write(word_bytes)
        # print(f"DEBUG: Word已保存到 {debug_word_path}，文件大小：{len(word_bytes)} bytes")
        # ====================================================================

        # 直接从内存转换为 PDF


        filename = f"{template_name}_filled.pdf"
        safe_name = quote(filename)
        return StreamingResponse(
            BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename*=UTF-8''{safe_name}",
                "Content-Length": str(len(pdf_bytes)),
            },
        )

async def insert_title(title_list, doc, template_id, measure_mode):
    title_list = title_list
    title_list_id = [item.bm_id for item in title_list]
    title_list_id_info_mapping = {item.bm_id: item for item in title_list}
    title_bookmark_instance = await TemplateBookmark.filter(template_doc_id=template_id, id__in=title_list_id, is_del = 0)
    for bookmark in title_bookmark_instance:
        name = bookmark.name
        value = title_list_id_info_mapping[bookmark.id].value
        bookmark_type = bookmark.type
        doc_stream = fill_word_bookmark(doc, name, value, bookmark_type, font_size=title_list_id_info_mapping[bookmark.id].font_size)
    return doc_stream

def apply_font_and_size(doc, font=None, font_size=None):
    """
    统一修改文档字体和字号。
    - font:      对所有 run 生效（中英文字体均修改）
    - font_size: 跳过标题段落（样式名含 'heading' 或 '标题'）
    """
    from docx.oxml.ns import qn
    from docx.oxml import OxmlElement

    HEADING_KEYWORDS = ('heading', '标题')

    def is_heading(paragraph):
        try:
            return any(kw in paragraph.style.name.lower() for kw in HEADING_KEYWORDS)
        except Exception:
            return False

    def process_run(r_elem, skip_size):
        rPr = r_elem.find(qn('w:rPr'))
        if rPr is None:
            rPr = OxmlElement('w:rPr')
            r_elem.insert(0, rPr)

        if font:
            rFonts = rPr.find(qn('w:rFonts'))
            if rFonts is None:
                rFonts = OxmlElement('w:rFonts')
                rPr.insert(0, rFonts)
            rFonts.set(qn('w:ascii'), font)
            rFonts.set(qn('w:hAnsi'), font)
            rFonts.set(qn('w:eastAsia'), font)
            rFonts.set(qn('w:cs'), font)

        if font_size and not skip_size:
            sz_val = str(int(float(font_size) * 2))  # Word XML 单位为半磅
            for tag_name in ('w:sz', 'w:szCs'):
                el = rPr.find(qn(tag_name))
                if el is None:
                    el = OxmlElement(tag_name)
                    rPr.append(el)
                el.set(qn('w:val'), sz_val)

    # 收集正文段落 + 表格内段落
    all_paragraphs = list(doc.paragraphs)
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                all_paragraphs.extend(cell.paragraphs)

    for para in all_paragraphs:
        skip_size = is_heading(para)
        for run in para.runs:
            process_run(run._r, skip_size)


def file_stream_to_base64(file_stream):
    doc_raw_bytes = file_stream.read()
    base64_str = base64.b64encode(doc_raw_bytes).decode("utf-8")
    return base64_str, doc_raw_bytes


def convert_docx_to_images_base64(file_stream) -> List[str]:
    """
    将Word文档转换为图片列表，返回base64编码列表
    适用于预览功能，保持格式完整性
    """
    doc_raw_bytes = file_stream.read()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        docx_path = os.path.join(tmpdir, "input.docx")
        
        # 保存docx文件
        with open(docx_path, "wb") as f:
            f.write(doc_raw_bytes)
        
        try:
            # 使用LibreOffice转换为图片（PNG格式保持高质量）
            cmd=get_libreoffice_command(tmpdir,docx_path,'png')
            result = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=get_libreoffice_timeout_seconds(), **get_libreoffice_subprocess_kwargs(cmd))
            
            # 收集所有生成的图片并转换为base64
            image_base64_list = []
            png_files = sorted([f for f in os.listdir(tmpdir) if f.endswith('.png')])
            
            for filename in png_files:
                img_path = os.path.join(tmpdir, filename)
                with open(img_path, "rb") as img_file:
                    img_base64 = base64.b64encode(img_file.read()).decode('utf-8')
                    image_base64_list.append(f"data:image/png;base64,{img_base64}")
            
            return image_base64_list
            
        except subprocess.CalledProcessError as e:
            detail = explain_libreoffice_returncode(e.returncode)
            if detail:
                print(f"LibreOffice诊断: {detail}")
            print(f"LibreOffice转换失败: {e}")
            return []
        except Exception as e:
            print(f"转换过程出错: {e}")
            return []

def convert_docx_to_pdf(docx_bytes: bytes) -> bytes:
    """
    使用 LibreOffice 将 docx 文件转换为 pdf 并返回 pdf 的字节内容。
    
    参数：
        docx_bytes: Word 文档的二进制内容（例如从 BytesIO 或 UploadFile.read() 得到）

    返回：
        转换后的 PDF 文件内容（bytes）
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        docx_path = os.path.join(tmpdir, "input.docx")
        pdf_path = os.path.join(tmpdir, "input.pdf")


        # 保存 docx 到临时文件
        with open(docx_path, "wb") as f:
            f.write(docx_bytes)
        

        # 转换 docx 为 pdf，LibreOffice 会自动输出到 tmpdir 中
        try:
            cmd=get_libreoffice_command(tmpdir,docx_path,'pdf')
            result = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=get_libreoffice_timeout_seconds(), **get_libreoffice_subprocess_kwargs(cmd))
        except subprocess.CalledProcessError as e:
            detail = explain_libreoffice_returncode(e.returncode)
            if detail:
                print(f"LibreOffice诊断: {detail}")
            raise RuntimeError(f"LibreOffice 转换失败: {e.stderr.decode()}")
        except subprocess.TimeoutExpired:
            raise RuntimeError("LibreOffice 转换超时（30秒）")

        # 等待一下，确保文件写入完成
        time.sleep(1)
        

        # 读取转换后的 PDF
        if not os.path.exists(pdf_path):
            raise FileNotFoundError("PDF 文件未生成")

        with open(pdf_path, "rb") as f:
            pdf_content = f.read()
            return pdf_content


def _get_html_from_template(template) -> str:
    """从 TemplateDoc 记录中提取 HTML 模板字符串。"""
    import base64 as _b64
    content_b64 = template.template_content
    if not content_b64:
        return ''
    # DEBUG: 打印原始数据 hex，对比两边是否一致
    print(f"[DEBUG] template={template.name} id={template.id} content_b64 type={type(content_b64)} len={len(content_b64)} hex[:40]={content_b64[:20].hex() if isinstance(content_b64, bytes) else content_b64[:20].encode().hex()}")
    raw_bytes = _b64.b64decode(content_b64)
    print(f"[DEBUG] b64decode len={len(raw_bytes)} hex[:40]={raw_bytes[:20].hex()}")
    for enc in ('utf-8', 'gbk', 'gb2312', 'gb18030', 'latin-1'):
        try:
            return raw_bytes.decode(enc)
        except (UnicodeDecodeError, UnicodeError):
            continue
    print(f"[_get_html_from_template] 模板 {template.name}(id={template.id}) 无法解码，使用 utf-8 replace 兜底")
    return raw_bytes.decode('utf-8', errors='replace')


def _save_classic_config_file(old_name: str, new_name: str, title_mapping: dict, header, footer, title_list=None, page_num=None, margin=None, orientation=None, line_height=None, header_position=None, footer_position=None):
    """
    经典模式另存为：从原 .py 配置文件复制，更新 title_mapping / 标题 / 页眉页脚 / 页码。
    header_position / footer_position: 'left' / 'center' / 'right'
    """
    import shutil

    py_dir = str(config.classic_structure_path)
    old_path = os.path.join(py_dir, f"{old_name}.py")
    new_path = os.path.join(py_dir, f"{new_name}.py")

    if not os.path.exists(old_path):
        print(f"[_save_classic_config_file] 原配置文件不存在: {old_path}")
        return

    shutil.copy(old_path, new_path)

    with open(new_path, 'r', encoding='utf-8') as f:
        content = f.read()

    import re

    # 1. 重建 title_mapping 段
    lines = ["title_mapping = {\n"]
    keys = list(title_mapping.keys())
    for i, k in enumerate(keys):
        info = title_mapping[k]
        comma = "," if i < len(keys) - 1 else ""
        lines.append(
            f"    '{k}': {{'name': '{info.get('name', '')}', "
            f"'font': '{info.get('font', '宋体')}', "
            f"'font_size': {info.get('font_size', 12)}}}{comma}\n"
        )
    lines.append("}\n")
    content = re.sub(r'title_mapping = \{[\s\S]*?\n\}\n', ''.join(lines), content)

    # 2. 更新 extra_info 中 header / footer
    if header and header.value:
        hf = header.font or "宋体"
        hs = header.font_size or 10
        hp = header_position or 'left'
        content = re.sub(r"'header'\s*:\s*\{[^}]*\}", f"'header': {{'value': '{header.value}', 'font': '{hf}', 'font_size': {hs}, 'position': '{hp}'}}", content)
    if footer and footer.value:
        ff = footer.font or "宋体"
        fs = footer.font_size or 9
        fp = footer_position or 'center'
        content = re.sub(r"'footer'\s*:\s*\{[^}]*\}", f"'footer': {{'value': '{footer.value}', 'font': '{ff}', 'font_size': {fs}, 'position': '{fp}'}}", content)

    # 3. 更新 extra_info 中 title_list
    if title_list:
        tl_lines = ["'title_list': [\n"]
        for t in title_list:
            tl_lines.append(
                f"        {{'name': '报告名称', 'value': '{t.value}', "
                f"'font': '{t.font or '黑体'}', 'font_size': {t.font_size or 15}}},\n"
            )
        tl_lines.append("    ]")
        tl_block = ''.join(tl_lines)
        content = re.sub(r"'title_list'\s*:\s*\[[\s\S]*?\]", tl_block, content)

    # 4. 更新 extra_info 中 page_num
    if page_num:
        pn_block = f"'page_num': {{'position': '{page_num['position']}', 'font': '{page_num.get('font', '宋体')}', 'font_size': {page_num.get('font_size', 9)}}}"
        content = re.sub(r"'page_num'\s*:\s*\{[^}]*\}", pn_block, content)
    elif page_num is not None:
        # 不展示页码：从 extra_info 中删除 page_num 条目
        content = re.sub(r"\s*'page_num'\s*:\s*\{[^}]*\},?\s*\n?", '\n', content)

    # 5. 更新 extra_info 中 margin（动态边距）
    if margin is not None:
        content = re.sub(r"'margin'\s*:\s*\{[^}]*\}", f"'margin': {{'value': '{margin}'}}", content)

    # 6. 更新 extra_info 中 orientation（横向/纵向）
    if orientation is not None:
        content = re.sub(r"'orientation'\s*:\s*\{[^}]*\}", f"'orientation': {{'value': {orientation}}}", content)

    # 7. 更新 extra_info 中 line_height（行边距）
    if line_height is not None:
        content = re.sub(r"'line_height'\s*:\s*\{[^}]*\}", f"'line_height': {{'value': '{line_height}'}}", content)

    with open(new_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"[_save_classic_config_file] 配置文件已保存: {new_path}")
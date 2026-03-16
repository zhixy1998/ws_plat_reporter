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
from utils.doc_converter import get_libreoffice_command, get_libreoffice_subprocess_kwargs, explain_libreoffice_returncode
from constants.template_constant import TemplatePageNumType, MeasureMode
from config import config
from utils.EditDocxXML import fill_word_bookmark

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
    header: BookmarkItem = Field(None, description='页眉')
    footer: BookmarkItem = Field(None, description='页脚')
    operation_type: int = Field(None, description='操作类型 0: 预览 1:另存为 2: 保存')
    name: str = Field(None, description='模板名称 当另存为的时候传入')
    remark: Optional[BookmarkItem]= Field(None, description='备注')
    project_name: Optional[BookmarkItem] = Field(None, description='动态项目名称')
    page_num_type: str = Field(TemplatePageNumType.no_page.value, description='页码类型')
    measure_mode: int = Field(None, description='测量模式 1:默认 2:仅测量标签位置不修改标签字体大小')



class DataSchema(BaseModel):
    file_base64: str = Field(..., description='文件base64')


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
        content = base64.b64decode(content_base64)  # 解码 base64 回原始 DOCX 字节

        # 如果传递了页眉或页脚，先插入到文档中，再更新 content 和 content_base64
        if data.header or data.footer:
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
            content_base64 = base64.b64encode(content).decode('utf-8')

        if data.measure_mode == MeasureMode.classic.value:
            await classic_create_template(new_name, content_base64, content=content, template_type=template.type, experiment_type=template.experiment_type, title_mapping=merged_title_mapping, old_template_name=template_name)
        else:
            await create_template(data.name, content_base64, content=content, template_type=template.type, 
        industry_type=template.industry_type, experiment_type=template.experiment_type, 
        title_mapping=merged_title_mapping, old_template_name=template_name)
        return {'code': 200, 'message': '模板另存为成功', 'data': {'file_base64': ''}}

    else:  # 预览

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
            result = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30, **get_libreoffice_subprocess_kwargs(cmd))
            
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
            result = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30, **get_libreoffice_subprocess_kwargs(cmd))
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
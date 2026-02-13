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
from app.classic_template_doc.routes.classic_create_template_view import create_template as classic_create_template
from .create_template_view import create_template
from utils.fille_template_utils import FillDataUtils
from exceptions.command_exception import APIException
from utils.handle_header_footer import set_header_footer
from utils.template_utils import get_doc_obj_by_template_id, get_title_mapping
from utils.doc_converter import get_libreoffice_command
from constants.template_constant import TemplatePageNumType, MeasureMode

router = APIRouter()

class BookmarkItem(BaseModel):
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



# class OutSchema(BaseModel):
#     code: int = Field(200, description='状态码')
#     message: str = Field('获取成功', description='返回信息')
#     data: DataSchema = Field(..., description='返回数据')


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
        print(f"Section 0 Header Paragraphs: {len(doc.sections[0].header.paragraphs)}") 
        output_stream = BytesIO()
        doc.save(output_stream)
        output_stream.seek(0)

        # 先获取原始字节数据
        doc_raw_bytes = output_stream.getvalue()
    
        # 为显示创建流（处理docxtpl标识）
        show_output_stream = BytesIO(doc_raw_bytes)
        if data.measure_mode == MeasureMode.classic.value:
            fill_data_utils = FillDataUtils(template_name, fake=True, new_title_mapping=new_title_mapping, template=template, structure_path='template_structure_classic')
        else:
            fill_data_utils = FillDataUtils(template_name, fake=True, new_title_mapping=new_title_mapping, template=template, structure_path='template_structure')
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

        # ========== DEBUG 模式：保存中间文件到硬盘（需要时取消注释） ==========
        # debug_word_path = os.path.join(os.getcwd(), "debug_template.docx")
        # with open(debug_word_path, "wb") as f:
        #     f.write(word_bytes)
        # print(f"DEBUG: Word已保存到 {debug_word_path}，文件大小：{len(word_bytes)} bytes")
        # ====================================================================

        # 直接从内存转换为 PDF

        # 使用 BytesIO 包装字节流，确保 StreamingResponse 正确发送整个文件
        filename = f"{template_name}_filled.docx"
        safe_name = quote(filename)
        headers = {
            "Content-Disposition": f"attachment; filename*=UTF-8''{safe_name}",
            "Content-Length": str(len(word_bytes))
        }
        return StreamingResponse(BytesIO(word_bytes), media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document", headers=headers)






# @router.post('/update_bookmark')
# @log_response
# async def update_bookmark(data: InputSchema):
#     operation_type = data.operation_type
#     template = await TemplateDoc.get_or_none(id=data.template_id)
#     if not template:
#         raise APIException(ErrorCode.TEMPLATE_NOT_FOUND)
#     bookmarks_instance = await TemplateBookmark.filter(template_doc_id=data.template_id, is_del=0)
#     bookmark_ids = [bookmark.id for bookmark in bookmarks_instance]
#     bookmark_id_font_mapping = {i.id : {'id': i.id, 'font': i.font, 'font_size': i.font_size, 'name': i.name, 'type': i.type} for i in bookmarks_instance}

#     input_bookmark_info_list = data.bookmark_list
#     input_bookmarks_id_list = [i.bm_id for i in input_bookmark_info_list]

#     del_bookmark_id_list = list(set(bookmark_ids) - set(input_bookmarks_id_list)) # 取出来要删除的id，不渲染的标签的id

#     title_list_id = [i.bm_id for i in data.title_list]
#     title_list_id_info_mapping = {i.bm_id: i for i in data.title_list}

#     # 去除掉标题的id，因为标题的要单独处理
#     del_bookmark_id_list_not_in_title = [i for i in del_bookmark_id_list if i not in title_list_id]

#     # input_bookmarks_id_str = ','.join([str(i.bm_id) for i in data.bookmark_list])
#     # sql = f"""select template_bookmark.* from template_doc 
#     #         inner join template_bookmark on template_doc.id = template_bookmark.template_doc_id where template_doc.id = %s
#     #         and template_bookmark.id in ({input_bookmarks_id_str})"""
#     # input_bookmarks = await execute_safe_sql(sql, [data.template_id], return_dict=True)

#     # 删除标签
#     del_bookmark_name_list = []
#     if del_bookmark_id_list_not_in_title:
#         del_bookmarks_id_str = ','.join([str(i) for i in del_bookmark_id_list_not_in_title])
#         sql = f"""select template_bookmark.name from template_doc 
#                 inner join template_bookmark on template_doc.id = template_bookmark.template_doc_id where template_doc.id = %s
#                 and template_bookmark.id in ({del_bookmarks_id_str})"""
#         del_bookmarks = await execute_safe_sql(sql, [data.template_id], return_dict=True)
#         for i in del_bookmarks:
#             del_bookmark_name_list.append(i.get('name'))

#     doc = await get_doc_obj_by_template_id(template_id=data.template_id)
#     for bookmark_name in del_bookmark_name_list:
#         doc_stream = delete_bookmark_content(doc=doc, bookmark_name=bookmark_name, output_path=None)
        

#     # 处理标题 
#     title=None
#     subtitle=None
#     title_bookmark_instance = await TemplateBookmark.filter(template_doc_id=data.template_id, id__in=title_list_id, is_del = 0)
#     for bookmark in title_bookmark_instance:
#         name = bookmark.name
#         value = title_list_id_info_mapping[bookmark.id].value
#         bookmark_type = bookmark.type
#         doc_stream = fill_word_bookmark(doc, name, value, bookmark_type)

#     # 处理替换修改字体和字体大小
#     update_bookmark_list = get_update_bookmark(bookmark_id_font_mapping, [*data.bookmark_list, *data.title_list])
#     for bookmark in update_bookmark_list:
#         name = bookmark.get('name')
#         font = bookmark.get('font')
#         font_size = bookmark.get('font_size')
#         bookmark_type = bookmark.get('type')
#         doc_stream = fill_word_bookmark(doc, name, value=None, value_type=bookmark_type, font=font, font_size=font_size)

#     # 处理页眉页脚
#     header_info = data.header
#     if header_info:
#         set_header_footer(doc, header_text=header_info.value, header_font_name=header_info.font, header_font_size=header_info.font_size)
#     footer_info = data.footer
#     if footer_info:
#         set_header_footer(doc, footer_text=footer_info.value, footer_font_name=footer_info.font, footer_font_size=footer_info.font_size)
    
#     custom_info ={}
#     #更新返回值的项目名和备注
#     if data.project_name:
#         custom_info["project_name"] = data.project_name.value
#     if data.note:
#          custom_info["note"]=data.note.value
#     # if data.project_name:
#     #     custom_info["project_name"] = data.project_name
#     # if data.note:
#     #      custom_info["note"]=data.note

#     #更新数据库CustomBookmark
#     try:
#         result = await TemplateExtraInfo.update_custom_bookmark(
#         template_id=data.template_id,
#         note=data.note.value if data.note else None, 
#         project_name=data.project_name.value if data.project_name else None,
#         header=data.header.value if data.header else None,
#         footer=data.footer.value if data.footer else None,
#         title=title if title else None,
#         subtitle=subtitle if subtitle else None)
#         if not result:
#             print("Warning: Custom bookmark update returned False")
#         # 根据业务需求决定是否继续执行或抛出异常
#     except Exception as e:
#         print(f"Error updating custom bookmark: {str(e)}")

#     # 保存为 BytesIO 返回
#     output_stream = BytesIO()
#     doc.save(output_stream)
#     output_stream.seek(0)

#     # 先获取原始字节数据
#     doc_raw_bytes = output_stream.getvalue()
    
#     # 为显示创建流（处理docxtpl标识）
#     show_output_stream = BytesIO(doc_raw_bytes)
#     template_instance = await TemplateDoc.get_or_none(id=data.template_id)
#     template_name = template_instance.name
#     fill_data_utils = FillDataUtils(template_name, data.template_id)
#     blank_table_context = await fill_data_utils.get_blank_table_context(template_name=template_name)
#     show_output_stream = fill_data_utils.fill_template_jinja_custom_info(doc_stream=show_output_stream, custom_info=custom_info, additional_context=blank_table_context)

#     show_base64_str = convert_docx_to_images_base64(show_output_stream)
    
#     # 为保存创建流（保持原始内容）
#     save_output_stream = BytesIO(doc_raw_bytes)
#     base64_str, _ = file_stream_to_base64(file_stream=save_output_stream)

#     if operation_type == 1: # 另存为
#         await create_template(data.name, base64_str, doc_raw_bytes)
#     if operation_type == 2: # 保存
#         await TemplateDoc.filter(id=data.template_id).update(template_content=base64_str)
#         for bookmark in update_bookmark_list:
#             await TemplateBookmark.filter(id=bookmark.get('id')).update(font=bookmark.get('font'), font_size=bookmark.get('font_size'))
#         for del_bookmark_name in del_bookmark_name_list:
#             await TemplateBookmark.filter(template_doc_id = data.template_id, name=del_bookmark_name).update(is_del=1)
#     return {'code': 200, 'message': '模板更新成功', 'data': {'file_base64': show_base64_str}}
#     # 返回文件
#     # return StreamingResponse(content=BytesIO(pdf_raw_bytes), media_type="application/pdf", headers={
#     #     "Content-Disposition": "attachment; filename=converted.pdf"
#     # })


def file_stream_to_base64(file_stream):
    doc_raw_bytes = file_stream.read()
    base64_str = base64.b64encode(doc_raw_bytes).decode("utf-8")
    return base64_str, doc_raw_bytes


# def get_update_bookmark(real_id_font_mapping: Dict[int, BookmarkItem], input_bookmark_list: List[BookmarkItem]):
#     """
#     拿传入的和实际的对比
#     找到修改的并且返回
#     """
#     update_book_mark = []
#     for i in input_bookmark_list:
#         i_dict = dict(i)
#         if i.bm_id in real_id_font_mapping:
#             if real_id_font_mapping[i.bm_id]['font'] != i.font or real_id_font_mapping[i.bm_id]['font_size'] != i.font_size:
#                 i_dict['name'] = real_id_font_mapping[i.bm_id]['name']
#                 i_dict['type'] = real_id_font_mapping[i.bm_id]['type']
#                 i_dict['id'] = i.bm_id
#                 update_book_mark.append(i_dict)
#     return update_book_mark

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
            result = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30)
            
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
            result = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30)
        except subprocess.CalledProcessError as e:
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
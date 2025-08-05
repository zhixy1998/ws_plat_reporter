import base64, os, json, shutil
from io import BytesIO
from zipfile import BadZipFile

import jinja2
from docxtpl import DocxTemplate
from fastapi import APIRouter, UploadFile, File, Form
from tortoise.transactions import in_transaction
from ..model.template_doc import TemplateDoc
from ..model.template_doc_base import TemplateDocBase
from ..model.template_bookmark import TemplateBookmark
from ..model.bookmark_data import BookmarkData
from utils.LoadAndDelete import AnalysisBookMark
from utils.doc_converter import convert_doc_to_docx, detect_file_format
from exceptions.error import ErrorCode
from exceptions.command_exception import APIException
from constants.template_constant import TemplateBookMarkType, TemplateType
from app.db import execute_safe_sql

router = APIRouter()

# class InputSchema(BaseModel):
#     name: str = Field(None, description='模板名称')

@router.post('/upload_template')
async def create_template_view(
    name: str = Form(None, description='模板名称'),
    template_type: int = Form(0, description=f"""模板类型 \n
                     {TemplateType.original_records.decs}: {TemplateType.original_records.value} \n
                     {TemplateType.report_template.decs}:{TemplateType.report_template.value} \n
                     {TemplateType.calibration_template.decs}:{TemplateType.calibration_template.value} \n
                     {TemplateType.installation_acceptance_template.decs}:{TemplateType.installation_acceptance_template.value}"""),
    file: UploadFile = File(..., description='模板文件')
    ):
    try:
        name = name if name else file.filename.split('.')[0]
        if await TemplateDocBase.get_or_none(name=name, is_del=0):
            raise APIException(ErrorCode.TEMPLATE_NAME_EXIST)
        content = await file.read()

        # 检测文件格式并自动转换DOC到DOCX
        file_format = detect_file_format(content)
        if file_format == 'doc':
            print(f"检测到DOC文件，正在转换为DOCX: {file.filename}")
            try:
                docx_stream = convert_doc_to_docx(content)
                content = docx_stream.read()  # 获取转换后的字节内容
                print(f"✅ DOC文件转换成功: {file.filename}")
            except Exception as e:
                print(f"❌ DOC文件转换失败: {e}")
                raise APIException(ErrorCode.INVALID_DOCX_FORMAT)
        elif file_format == 'docx':
            print(f"检测到DOCX文件: {file.filename}")
        else:
            print(f"❌ 不支持的文件格式: {file.filename}")
            raise APIException(ErrorCode.INVALID_DOCX_FORMAT)

        content_base64 = base64.b64encode(content).decode('utf-8')
        # 存入数据库
        try:
            await create_template(name, content_base64, content, template_type=template_type)
        except BadZipFile:
            raise APIException(ErrorCode.INVALID_DOCX_FORMAT) 
    except APIException as e:
        raise e
    except Exception as e:
        import traceback
        traceback.print_exc()
        # 返回统一错误
        raise APIException(ErrorCode.SAVE_TEMPLATE_FAILED)
    return {'code': 200, 'message': '模板保存成功'}

async def create_template(name: str, content_base64: str, content: bytes, template_type: int = 0):
    async with in_transaction() as connection:
        create_info = {
            'name': name,
            'template_content': content_base64,
            'type': template_type
        }
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
        await create_python_setting_file(template_id = template.id, name=name, template_file_steam=BytesIO(content), connection=connection)



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
        if new_bookmark.type == TemplateBookMarkType.sheet.value and bookmark.get('table_structure'):
            bookmark_id= new_bookmark.id
            structure_type = bookmark.get('table_structure').get('structure_type')
            if structure_type is not None:  # 可能是0 0也是正确的
                table_structure = bookmark.get('table_structure')
                await BookmarkData.create(bookmark_id=bookmark_id, structure_type=structure_type, table_structure=table_structure)
            
                
        for child in bookmark['children']:
            if child.get('name') and child.get('id'):
                await recursion_create_bookmark(child, template_id, new_bookmark.id)

async def create_python_setting_file(template_id: int, name: str, template_file_steam: BytesIO, connection=None):
    """
    只创建一个空的JSON文件
    
    Args:
        name: 文件名称
        output_dir: 输出目录
    """
    py_folders = 'template_structure'
    # 确保输出目录存在
    os.makedirs(py_folders, exist_ok=True)

    # 模版内容
    doc = DocxTemplate(template_file_steam)
    try:
        doc = DocxTemplate(template_file_steam)
        context_vars = doc.get_undeclared_template_variables()
    except jinja2.exceptions.TemplateSyntaxError as e:
        print(e)
        raise APIException(ErrorCode.INVALID_TEMPLATE_FIELD)
    py_lines = [
        "# 模板字段定义\n",
        "# fill_type: 0 表示从模板中提取的字段, fill_type: 1 表示表格截取的字段\n\n",
        "# get_type: 0: 表示从通用数据中取, 1: 表示从接口中取 2: 表从数据库中取\n\n"
        "python_template_var = {\n"
    ]

    # 获取表格表头
    table_list = []
    tables = await get_table_structure_by_template_name(template_id=template_id, template_name=name, connection=connection)
    if tables:
        for table in tables:
            # table_fields = []
            # table_dict = {
            #     'table_name': None,
            #     'table_fields': []
            # }
            table_structure = json.loads(table.get('table_structure'))
            # table_dict['table_name'] = table_structure.get('table_name')
            # headers = table_structure.get('headers')
            # if len(headers) == 1:
            #     for h in headers[0]:
            #         table_fields.append(h)
            # else:
            #     table_fields = ["-".join(map(str, group)) for group in zip(*headers)]
            # table_dict['table_fields'] = table_fields
            table_list.append(table_structure)



    context = list(context_vars)
    for i, var in enumerate(context):
        comma = "," if i < len(context) - 1 else ""
        if var in context_vars:
            py_lines.append(f'    "{var}": {{"fill_type": 0}}{comma}\n')
    py_lines.append("}\n")
    
    # 字段渲染表格
    py_lines.append("table_fields = ")
    # 使用更安全的方式处理中文字符，确保编码正确
    table_fields_str = json.dumps(table_list, indent=4, ensure_ascii=False, separators=(',', ': '))
    table_fields_str = table_fields_str.replace("null", "None")
    py_lines.append(f"{table_fields_str}\n") 
    
    # 创建文件
    py_path = os.path.join(py_folders, f"{name}.py")
    backup_path = os.path.join(py_folders, f"{name}_back.py")
    # 如果原文件存在，先备份
    if os.path.exists(py_path):
        # 如果之前已有备份，也可以选择是否覆盖，这里直接覆盖
        shutil.copy2(py_path, backup_path)
    
    # 使用更安全的文件写入方式，确保 UTF-8 编码正确
    with open(py_path, "w", encoding="utf-8", newline='\n') as f:
        for line in py_lines:
            f.write(line)
     
    return py_path

async def get_table_structure_by_template_name(template_id, template_name, connection):
    sql_text = """
    select bookmark_data.table_structure from template_doc 
    left join template_bookmark on template_doc.id = template_bookmark.template_doc_id 
    left join bookmark_data on template_bookmark.id = bookmark_data.bookmark_id 
    where template_doc.name = %s and template_doc.id = %s and template_bookmark.type = %s and template_doc.is_del = %s
    """
    sql_result = await execute_safe_sql(sql_text, [template_name, template_id,TemplateBookMarkType.sheet.value, 0], return_dict=True, connection=connection)
    return sql_result

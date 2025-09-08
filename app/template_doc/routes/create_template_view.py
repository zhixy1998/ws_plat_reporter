import base64, os, json, shutil
from io import BytesIO
from zipfile import BadZipFile

import jinja2
from docxtpl import DocxTemplate
from fastapi import APIRouter, UploadFile, File, Form
from tortoise.transactions import in_transaction
from app.template_doc.model.template_doc import TemplateDoc
from app.template_doc.model.template_doc_base import TemplateDocBase
from app.template_doc.model.template_bookmark import TemplateBookmark
from app.template_doc.model.template_extra_info import TemplateExtraInfo
from ..model.bookmark_data import BookmarkData
from utils.LoadAndDelete import AnalysisBookMark
from utils.doc_converter import convert_doc_to_docx, detect_file_format
from exceptions.error import ErrorCode
from exceptions.command_exception import APIException
from constants.template_constant import TemplateBookMarkType, TemplateType
from app.db import execute_safe_sql
from utils.log_decorator import log_response
from utils.template_utils import extract_tr_variables

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
            template_id = await create_template(name, content_base64, content, template_type=template_type)
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

async def create_template(name: str, content_base64: str, content: bytes, template_type: int = 0) -> int:
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
        return template.id


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
                bookmark_data = await BookmarkData.create(bookmark_id=bookmark_id, structure_type=structure_type, table_structure=table_structure)
                bookmark_name = bookmark.get('name')
                book_mark_tpl_name = bookmark_name + '_tpl' # 这个代表这个表格有tpl横向表格
                for child in bookmark.get("children"):
                    if child.get('name') == book_mark_tpl_name:
                        await TemplateExtraInfo.create(
                            template_doc_id = template_id,
                            bookmark_data_id = bookmark_data.id,
                            has_tr = 1
                        )
                        
                        # 反过来更新BookmarkData的table_structure字段，添加has_tr标识
                        updated_table_structure = bookmark_data.table_structure
                        updated_table_structure['has_tr'] = 1
                        # 更新BookmarkData记录
                        bookmark_data.table_structure = updated_table_structure
                        await bookmark_data.save()

            
                
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
    has_tr_syntax = False
    try:
        doc = DocxTemplate(template_file_steam)
        context_vars = doc.get_undeclared_template_variables()
        
        # 检测是否有tr语法并提取变量
        has_tr_syntax = extract_tr_variables(template_file_steam)
        
        # 保存tr语法检测结果到TemplateExtraInfo表
        # await TemplateExtraInfo.update_or_create(
        #     template_doc_id=template_id,
        #     defaults={
        #         'has_tr': 1 if has_tr_syntax else 0,
        #         'is_del': 0
        #     }
        # )
        
        
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
            table_structure = json.loads(table.get('table_structure'))
            table_list.append(table_structure)



    context = list(context_vars)
    
    # 分离普通变量和带索引的变量
    normal_vars = []
    indexed_vars = {}

    for var in context:
        # 检查是否是带索引的变量（如：标准溶液加入体积_0）
        if '_' in var and var.split('_')[-1].isdigit():
            base_name = '_'.join(var.split('_')[:-1])  # 获取基础名称
            index = var.split('_')[-1]  # 获取索引
            
            if base_name not in indexed_vars:
                indexed_vars[base_name] = []
            indexed_vars[base_name].append(var)
        else:
            normal_vars.append(var)
    
    # 写入普通变量
    for i, var in enumerate(normal_vars):
        comma = "," if i < len(normal_vars) - 1 else ""
        py_lines.append(f'    "{var}": {{"fill_type": 0}}{comma}\n')
    
    py_lines.append("}\n")
    
    # 添加 table_jinja_values 分组信息（作为独立变量）
    if indexed_vars:
        py_lines.append("\n# 表格字段分组\n")
        py_lines.append("table_jinja_values = {\n")
        
        for i, (base_name, vars_list) in enumerate(indexed_vars.items()):
            vars_list.sort(key=lambda x: int(x.split('_')[-1]))  # 按索引排序
            vars_str = "', '".join(vars_list)
            comma = "," if i < len(indexed_vars) - 1 else ""
            py_lines.append(f"    '{base_name}': ['{vars_str}']{comma}\n")
        
        py_lines.append("}\n")
    
    # 添加 tr 变量信息到生成的文件中
    # if has_tr_syntax and tr_variables:
    #     py_lines.append("\n# tr语法变量列表\n")
    #     py_lines.append(f"tr_variables = {tr_variables}\n")
    #     py_lines.append(f"has_tr_syntax = {has_tr_syntax}\n")
    
    # 字段渲染表格
    custom_bookmark = {
       'project_name' : '项目名称',
        'note':'备注',
    }
    # 添加 custom_bookmark 到生成的文件中
    py_lines.append("\n# 字段渲染表格\n")
    py_lines.append("custom_bookmark = {\n")
    for key, values in custom_bookmark.items():
        py_lines.append(f"    '{key}':'{values}',\n")
    py_lines.append("}\n\n")
    
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
    inner join template_bookmark on template_doc.id = template_bookmark.template_doc_id 
    inner join bookmark_data on template_bookmark.id = bookmark_data.bookmark_id 
    where template_doc.name = %s and template_doc.id = %s and template_bookmark.type = %s and template_doc.is_del = %s
    and bookmark_data.table_structure is not null
    """
    sql_result = await execute_safe_sql(sql_text, [template_name, template_id,TemplateBookMarkType.sheet.value, 0], return_dict=True, connection=connection)
    
    print(f"Debug: Found {len(sql_result)} table_structure records")
    return sql_result

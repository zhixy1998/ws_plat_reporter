import os, base64, re
import importlib
from io import BytesIO
from dotenv import load_dotenv
import urllib.parse
import requests
from docx import Document
from docx.shared import Cm
from docx.oxml.ns import qn
from docxtpl import InlineImage
from docxtpl import DocxTemplate
from docx.oxml import OxmlElement
from exceptions.error import ErrorCode
from utils.EditDocxXML import fill_word_bookmark
from exceptions.command_exception import APIException
from constants.template_constant import TemplateBookMarkType
# from app.template_doc.model.bookmark_data import BookmarkData
from app.template_doc.model.template_bookmark import TemplateBookmark
from constants.template_constant import GetTypeConstant, FillTypeConstant, StructureType
from utils.table_data_processor import TableDataProcessor, GetHeaderAndData

load_dotenv(override=True)

class FillDataUtils():
    def __init__(self, name, template_id):
        self.name = name
        self.sample_id = None
        private_mod = None
        self.template_id = template_id
        self.common_val = None   # 代表通用数据接口返回的数据
        self.common_key = None   # 代表通用数据的描述
        self.private_key = None  # 代表私有数据的描述
        self.python_jinja_mapping = {}
        self.table_contexts = {}


    async def fill_data(self, doc_stream, task_id, sample_id=None):
        self.sample_id = sample_id
        template_common_url = os.getenv('TEMPLATE_COMMON_VAR_URL') + '?taskId=' + urllib.parse.quote(str(task_id), safe='')
        # print(f"DEBUG: 请求URL: {template_common_url}")
        # print(f"DEBUG: 原始task_id: {repr(task_id)}")
        try:
            res = requests.get(template_common_url, timeout=5)
            if res.status_code == 200:
                try:
                    res_json = res.json()
                    if res_json.get('code') == 200:
                        common_val = res_json.get('data')
                    else:
                        common_val = {}
                except Exception as e:
                    print(e)
                    common_val = {}
            else:
                print("请求通用数据失败, url:", template_common_url)
                common_val = {}
        except requests.exceptions.Timeout:
            print(f"请求超时，跳过: {template_common_url}")
            common_val = {}
        except Exception as e:
            print(f"请求异常，跳过: {e}")
            common_val = {}
        
        self.common_val = common_val
        # 先加载通用数据
        module_name = "template_structure." + 'common_data'  # 比如 name = "my_template"
        common_mod = importlib.import_module(module_name)
        common_key = common_mod.data
        self.common_key = common_key
        common_table_info_dict = common_mod.table_name_list


        module_name = "template_structure." + self.name  # 比如 name = "my_template"
        try:
            private_mod = importlib.import_module(module_name)
        except Exception as e:
            raise APIException(error=ErrorCode.TEMPLATE_NOT_FOUND)
        self.private_mod = private_mod
        # 不是表格数据
        self.private_key = private_mod.python_template_var
        private_key_text_fields = private_mod.python_template_var    
        # 表格数据
        private_data_table_fields = private_mod.table_fields
        self.table_fields = private_mod.table_fields

        get_data_from_common_data_jinja = [] # 这个数据从通用里面取 然后jinja填充
        get_data_from_common_data_bookmark = [] # 这个数据从通用里面取 然后书签填充 
        get_data_from_endpoint_jinja = [] # 这个数据从接口取 然后jinja填充
        get_data_from_endpoint_bookmark = [] # 这个数据从接口取 然后书签填充
        get_data_from_database_jinja = [] # 这个数据从数据库取 然后jinja填充
        get_data_from_database_bookmark = [] # 这个数据从数据库取 然后书签填充

        for k, item in private_key_text_fields.items():
            if item.get('get_type') is None or int(item.get('get_type'))  == GetTypeConstant.common.value:
                if int(item.get('fill_type')) == FillTypeConstant.jinja.value:
                    get_data_from_common_data_jinja.append({k:item})
                if int(item.get('fill_type')) == FillTypeConstant.bookmark.value:
                    get_data_from_common_data_bookmark.append({k:item})
                
            elif int(item.get('get_type')) == GetTypeConstant.endpoint.value:
                if int(item.get('fill_type')) == FillTypeConstant.jinja.value:
                    get_data_from_endpoint_jinja.append({k:item})
                if int(item.get('fill_type')) == FillTypeConstant.bookmark.value:
                    get_data_from_endpoint_bookmark.append({k:item})
            elif int(item.get('get_type')) == GetTypeConstant.database.value:
                if int(item.get('fill_type')) == FillTypeConstant.jinja.value:
                    get_data_from_database_jinja.append({k:item})
                if int(item.get('fill_type')) == FillTypeConstant.bookmark.value:
                    get_data_from_database_bookmark.append({k:item})

        # if get_data_from_common_data_jinja:
        #     # 检查是否有表格需要单独tpl对象渲染，如果有，合并context
        #     if hasattr(self.private_mod, 'table_jinja_values'):
        #         table_jinja_values = self.private_mod.table_jinja_values
        #         # table_jinja_and_num_mapping = {}
        #         # for context_name, text_list in table_jinja_values.items():
        #         #     table_jinja_and_num_mapping[context_name] = len(text_list)
        #         self.table_contexts = self.get_context(table_jinja_values)
            
        if get_data_from_common_data_bookmark:
            pass
        if get_data_from_endpoint_jinja:
            pass
        if get_data_from_endpoint_bookmark:
            pass
        if get_data_from_database_jinja:
            pass
        if get_data_from_database_bookmark:
            pass

        origin_header_real_header_mapping = {} # {'模版本来的表头': '实际表头'} 
        table_data_processor = TableDataProcessor(self.name)
        if not hasattr(table_data_processor.handler_instance, 'HEADER_M_MAPPING'):
            raise APIException(error=ErrorCode.TABLE_DATA_HANDLER_NOT_FOUND)
        HEADER_M_MAPPING = table_data_processor.handler_instance.HEADER_M_MAPPING  # 每个私有文件都要声明的
        TABLE_NAME = table_data_processor.handler_instance.TABLE_NAME
        get_header_and_data_class_instance = GetHeaderAndData(task_id)
        await get_header_and_data_class_instance._get_all_headers()
        self.HEADER_M_MAPPING = HEADER_M_MAPPING
        for origin_header, m in HEADER_M_MAPPING.items():
            get_real_header_bool, real_header = await get_header_and_data_class_instance.get_header(m)
            if get_real_header_bool:
                origin_header = TABLE_NAME + '_' + origin_header
                origin_header_real_header_mapping[origin_header] = real_header if real_header else origin_header
        # 把原来的表头替换成真实的表头
        for name, value in origin_header_real_header_mapping.items():
            doc_stream = fill_word_bookmark(doc_stream, name, value, TemplateBookMarkType.text.value)
        

        # 处理表格
        for table_info in private_data_table_fields:
            table_name = table_info.get('table_name')
            common_table_val = self.get_common_table_data(table_name, task_id)
            if table_name in common_table_info_dict: 
                # 如果表格名字在通用表格名称里（就是接口已经定义的）
                # 就通过 通过表格接口传递参数获取
                table_header_data_mapping = common_table_info_dict.get(table_name)
                table_header_data_mapping = self.filter_table_header(table_info.get('headers'), table_header_data_mapping)
                if hasattr(self.private_mod, 'handle_endpoint_data_to_table_row'):
                    row_list = common_table_val = self.private_mod.handle_endpoint_data_to_table_row(table_header_data_mapping, common_table_val)
                else:
                    row_list = self.handle_endpoint_data_to_table_row(table_header_data_mapping, common_table_val)
                bookmark_type = TemplateBookMarkType.sheet.value
                # table_name实际就是表格名字
                current_table_column_widths = table_info.get('column_width')
                doc_stream = fill_word_bookmark(doc_stream, table_name, row_list, bookmark_type, specific_column_widths=current_table_column_widths)
            else:
                if 'has_tr' in table_info:  # 这个代表这个表格是用了tr表格渲染的语法
                    sheet_bookmark = await TemplateBookmark.get(name=table_name, template_doc_id=self.template_id, is_del=0)
                    # 递归获取所有子标签，组成一维列表，排除包含'_tpl'的标签
                    all_child_bookmarks = await self.get_all_child_bookmarks(sheet_bookmark.id)
                    # 过滤掉包含'_tpl'的标签
                    filtered_bookmarks = [b for b in all_child_bookmarks if '_tpl' not in b.name]
                    filtered_bookmark_names = [b.name.split(table_name + '_')[1] for b in filtered_bookmarks]
                    # 现在拿到了所有的需要批量获取的tpl变量。
                    tr_context = self.get_tr_context(table_name, filtered_bookmark_names)
                    self.table_contexts.update(tr_context)
                    # print(f"表格 {table_name} 的tr变量: {filtered_bookmark_names}")


                
        doc_stream = await self.common_fill_data_by_jinja(doc_stream)
        doc_stream = self.insert_header_page_number(doc_stream)
        return doc_stream



    # 通用数据的jinja填充数据
    async def common_fill_data_by_jinja(self, doc_stream, additional_context=None):
        """
        逻辑: 如果private里面有，但是没有描述position, 那么就从common里面取, 如果描述了position，再说
        """
        if additional_context is None:
            additional_context = {}

        tpl = DocxTemplate(doc_stream)
        value_list = [] # 所有的值的列表
        for private_k, v_dict in self.private_key.items():
            # 如果私有文件描述了怎么取数据。
            if v_dict.get('position'):
                pass
            else:
            # 查看通用数据是否描述了这个变量的取值方法。
                if private_k in self.common_key:
                    get_desc = self.common_key[private_k]
                    if get_desc.get('position'):
                        await self.handle_position(private_k, get_desc.get('position'), value_list)
                    if get_desc.get('children'):
                        await self.handle_children(private_k, get_desc.get('children'), value_list, connect_str=get_desc.get('connect_str', ''))
                else:
                    self.python_jinja_mapping[private_k] = ''
        max_len_val_blank = ''
        for v in value_list:
            if v and len(v) > len(max_len_val_blank):
                max_len_val_blank = len(v) * ' '

        for k, v in self.python_jinja_mapping.items():
            # print(k, v)
            if v == '':
                self.python_jinja_mapping[k] = max_len_val_blank
        intermediate_stream = self.fill_template_by_jinja(tpl, additional_context)
        return intermediate_stream

    # 从通用接口取当前表格需要的jinja数据
    async def get_common_val_by_private_position(self, position):
        val = self.common_val.get(position[0])
        return val

    # 处理position position代表这个数据获取的描述方法。
    async def handle_position(self, private_k, position, value_list):
        val = await self.get_common_val_by_private_position(position)
        if '图片' in private_k and isinstance(val, str) and self.is_base64(val):
            try:
                self.python_jinja_mapping[private_k] = await self.decode_base64_image(bookmark_name=private_k, tpl=tpl, val=val)
            except Exception as e:
                print(f"{private_k} 解码失败: {e}")
        else:
            self.python_jinja_mapping[private_k] = val if val else ''
            value_list.append(val)
    
    # 处理children children代表这个数据获取的描述方法。
    async def handle_children(self, private_k, children, value_list, connect_str=''):
        final_val_list = []
        for child in children:
            get_desc = self.common_key.get(child)
            if get_desc and get_desc.get('position'):
                val = await self.get_common_val_by_private_position(get_desc.get('position'))
                if val:
                    final_val_list.append(val)
        if final_val_list:
            self.python_jinja_mapping[private_k] = connect_str.join(final_val_list)
            value_list.append(connect_str.join(final_val_list))
        


    @staticmethod
    def fill_template_jinja_blank(doc_stream):
        """
        获取docxtpl模板中所有未填充的Jinja变量，并将它们填充为空字符串
        
        Args:
            doc_stream: Word文档的BytesIO流
            
        Returns:
            填充后的文档BytesIO流
        """
        try:
            from docxtpl import DocxTemplate
            from io import BytesIO
            
            # 创建DocxTemplate对象
            tpl = DocxTemplate(doc_stream)
            
            # 获取模板中所有未声明的变量
            undeclared_vars = tpl.get_undeclared_template_variables()
            

            # 为所有未声明的变量创建空字符串映射
            blank_context = {}
            for var in undeclared_vars:
                blank_context[var] = ""

            # 如果没有未声明的变量，直接返回原文档
            if not blank_context:
                doc_stream.seek(0)
                return doc_stream
            
            # 使用空字符串上下文渲染模板
            tpl.render(blank_context)
            
            # 保存到新的BytesIO流
            output_stream = BytesIO()
            tpl.save(output_stream)
            output_stream.seek(0)
            
            return output_stream
            
        except Exception as e:
            # 出错时返回原文档
            doc_stream.seek(0)
            return doc_stream

    # 通用的通过书签填充
    def common_fill_data_by_bookmark(private_key, common_key, common_val, doc_stream):
        pass

    # 通过接口获取数据然后jinja填充
    def endpoint_fill_data_by_jinja(self):
        pass

    # 通过接口获取数据然后书签填充
    def endpoint_fill_data_by_bookmark(self):
        pass

    # 通过数据库获取数据然后jinja填充
    def database_fill_data_by_jinja(self):
        pass

    # 通过数据库获取数据然后书签填充
    def database_fill_data_by_bookmark(self):
        pass

    def fill_template_by_jinja(self, tpl, additional_context=None):
        """
        """
        # 合并context
        final_context = self.python_jinja_mapping.copy()
        if additional_context:
            final_context.update(additional_context)
            # print("Merged context:", final_context)
        
        # 处理python jinja语法变量
        tpl.render(context=final_context)
        # 写入内存流，返回
        output_stream = BytesIO()
        tpl.save(output_stream)
        output_stream.seek(0)  # 很重要：回到开头，供后续读取
        
        # 后处理：移除表格中的空行
        output_stream = self.remove_empty_table_rows(output_stream)
        
        return output_stream
    
    def remove_empty_table_rows(self, doc_stream: BytesIO) -> BytesIO:
        """移除表格中的空行"""
        try:
            from docx import Document
            doc = Document(doc_stream)
            
            for table in doc.tables:
                rows_to_remove = []
                for i, row in enumerate(table.rows):
                    # 检查行是否为空（所有单元格都为空或只包含空白字符）
                    is_empty = True
                    for cell in row.cells:
                        cell_text = cell.text.strip()
                        if cell_text:
                            is_empty = False
                            break
                    
                    if is_empty:
                        rows_to_remove.append(i)
                
                # 从后往前删除空行，避免索引问题
                for row_idx in reversed(rows_to_remove):
                    if row_idx < len(table.rows):
                        table._element.remove(table.rows[row_idx]._element)
            
            # 保存处理后的文档
            output_stream = BytesIO()
            doc.save(output_stream)
            output_stream.seek(0)
            return output_stream
            
        except Exception as e:
            print(f"Error removing empty table rows: {e}")
            doc_stream.seek(0)
            return doc_stream
    
    def get_common_table_data(self, table_name: str, task_id: str) -> dict:
        template_common_url = os.getenv('TEMPLATE_COMMON_TABLE_URL') + '?taskId=' + urllib.parse.quote(str(task_id), safe='') + '&reportName=' + table_name + "&sampleId=" + urllib.parse.quote(str(self.sample_id), safe='')
        print(f"DEBUG: 请求URL: {template_common_url}")
        print(f"DEBUG: 原始task_id: {repr(task_id)}")
        try:
            res = requests.get(template_common_url, timeout=5)
            if res.status_code == 200:
                common_table_val = res.json().get('data')
            else:
                print("请求通用表格数据失败, url:", template_common_url)
                common_table_val = {}
        except requests.exceptions.Timeout:
            print(f"请求超时，跳过: {template_common_url}")
            common_table_val = {}
        except Exception as e:
            print(f"请求异常，跳过: {e}")
            common_table_val = {}
        return common_table_val
    
    def handle_endpoint_data_to_table_row(self, table_fields: list, common_table_val) -> list:
        pass

    def is_base64(self, s: str) -> bool:
        if not isinstance(s, str):
            return False
        try:
            # base64 字符长度必须是4的倍数
            if len(s) % 4 != 0:
                return False
            # 符合 base64 编码字符集
            if not re.match(r'^[A-Za-z0-9+/=\s]+$', s):
                return False
            # 能否成功 decode
            base64.b64decode(s, validate=True)
            return True
        except Exception:
            return False
    
    async def decode_base64_image(self, bookmark_name, tpl, val):
        try:
            image_data = base64.b64decode(val)
            image_stream = BytesIO(image_data)
            img_bookmark_instance = await TemplateBookmark.get_or_none(template_doc_id=self.template_id, name=bookmark_name, is_del=0)
            if img_bookmark_instance and img_bookmark_instance.img_size:
                return InlineImage(tpl, image_stream, width=Cm(img_bookmark_instance.img_size))  # 根据需要调整宽度
            else:
                return InlineImage(tpl, image_stream, width=Cm(14))  # 根据需要调整宽度
        except Exception as e:
            print("图片解码失败", e)
            return None
    
    def filter_table_header(self, private_header, table_header_data_mapping):
        private_header = self.handle_table_header(private_header)
        new_table_header_data_mapping = {}
        for header in private_header:
            if header in table_header_data_mapping:
                new_table_header_data_mapping[header] = table_header_data_mapping[header]
        return new_table_header_data_mapping
    
    def handle_table_header(self, headers):
        """
        数据库存储的表头可能是嵌套的，需要处理
        两层嵌套，就用 '-' 把同一列连接起来。
        """
        if len(headers) == 1:
            return headers[0]
        else:
            return ["-".join(map(str, group)) for group in zip(*headers)]
    

    def insert_header_page_number(self, doc_stream: BytesIO) -> BytesIO:
        doc = Document(doc_stream)

        section = doc.sections[0]
        header = section.header
        paragraph = header.paragraphs[0] if header.paragraphs else header.add_paragraph()

        paragraph.alignment = 2  # 右对齐

        def add_field(p, field_code):
            run = p.add_run()
            fldChar_begin = OxmlElement('w:fldChar')
            fldChar_begin.set(qn('w:fldCharType'), 'begin')
            instrText = OxmlElement('w:instrText')
            instrText.set(qn('xml:space'), 'preserve')
            instrText.text = field_code
            fldChar_separate = OxmlElement('w:fldChar')
            fldChar_separate.set(qn('w:fldCharType'), 'separate')
            fldChar_end = OxmlElement('w:fldChar')
            fldChar_end.set(qn('w:fldCharType'), 'end')
            run._r.append(fldChar_begin)
            run._r.append(instrText)
            run._r.append(fldChar_separate)
            run._r.append(fldChar_end)

        paragraph.add_run("第 ")
        add_field(paragraph, "PAGE")
        paragraph.add_run(" 页，共 ")
        add_field(paragraph, "NUMPAGES")
        paragraph.add_run(" 页")

        # 保存回字节流
        output_stream = BytesIO()
        doc.save(output_stream)
        output_stream.seek(0)
        return output_stream
    
    # def get_context(self, table_jinja_values):
    #     fake_table_jinja_contexts = {}
    #     if hasattr(self.private_mod, 'fake_table_jinja_contexts'):
    #         fake_table_jinja_contexts = self.private_mod.fake_table_jinja_contexts
    #     contexts = {}
    #     for context_name, children_list in table_jinja_values.items():
    #         context = self.get_one_context(context_name, children_list)
    #         if not context and fake_table_jinja_contexts.get(context_name): # 如果没有取到数据，并且写了假数据，就用假数据代替
    #             context = self.fill_fake_context_data(children_list, fake_table_jinja_contexts.get(context_name))
    #         contexts.update(context)
    #     return contexts
    
    # def get_one_context(self, context_name, children_list):
    #     """
    #     这个字段负责具体表格的每个变量如何获取，
    #     比如 这9个数据
    #     ['减空白后吸光度_0', '减空白后吸光度_1', '减空白后吸光度_2', '减空白后吸光度_3', '减空白后吸光度_4', '减空白后吸光度_5', '减空白后吸光度_6', '减空白后吸光度_7', '减空白后吸光度_8'
    #     先根据task_id去数据库中查询context_name 怎么获取，
    #     然后获取到 9个数据。
    #     然后返回一个字典，key是children_list中的值，value是获取到的数据。
    #     """
    #     return {}

    def fill_fake_context_data(self, children_list, fake_context_list):
        context = {}
        for children_context in children_list:
            context_index = children_context.split('_')[1]
            # print(children_context, context_index)
            context[children_context] = fake_context_list[int(context_index)]
        return context
    
    async def get_all_child_bookmarks(self, parent_id):
        """
        递归获取所有子标签，组成一维列表
        
        Args:
            parent_id: 父标签的ID
            
        Returns:
            list: 所有子标签的一维列表
        """
        all_children = []
        
        # 获取直接子标签
        direct_children = await TemplateBookmark.filter(
            parent_id=parent_id, 
            template_doc_id=self.template_id, 
            is_del=0
        ).all()
        
        for child in direct_children:
            # 添加当前子标签到列表
            all_children.append(child)
            
            # 递归获取这个子标签的所有子标签
            grandchildren = await self.get_all_child_bookmarks(child.id)
            all_children.extend(grandchildren)
        
        return all_children
    
    def get_tr_context(self, table_name, filtered_bookmark_names, row_num=5):
        """
        : table_name: 表格名称 因为模版中的语法设置的循环的列表名字是 [table_name]_rows 比如 数据表格_rows 所以这个作为返回的变量
        : filtered_bookmark_names: 过滤后的标签名称列表  这个名称和标签名称一致 表格每一个列都要设置一个标签 标签以_连接，作为子标签
        : row_num: 行数 查询多少行
        """
        key = table_name + '_rows'
        # [{}]
        if hasattr(self.private_mod, key):
            return {key: getattr(self.private_mod, key)}
        data_list = []
        return {key: data_list}

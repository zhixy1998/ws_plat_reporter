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
from constants.template_constant import GetTypeConstant, FillTypeConstant

load_dotenv(override=True)

class FillDataUtils():
    def __init__(self, name, template_id):
        self.name = name
        private_mod = None
        self.template_id = template_id
        self.common_val = None   # 代表通用数据接口返回的数据
        self.common_key = None   # 代表通用数据的描述
        self.private_key = None  # 代表私有数据的描述
        self.python_jinja_mapping = {}

    async def fill_data(self, doc_stream, task_id):

        template_common_url = os.getenv('TEMPLATE_COMMON_VAR_URL') + '?taskId=' + urllib.parse.quote(str(task_id), safe='')
        # print(f"DEBUG: 请求URL: {template_common_url}")
        # print(f"DEBUG: 原始task_id: {repr(task_id)}")
        res = requests.get(template_common_url, timeout=15)
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

        if get_data_from_common_data_jinja:
            doc_stream = await self.common_fill_data_by_jinja(doc_stream)
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

        for table_info in private_data_table_fields:
            table_name = table_info.get('table_name')
            if table_name in common_table_info_dict: 
                # 如果表格名字在通用表格名称里（就是接口已经定义的）
                # 就通过 通过表格接口传递参数获取
                table_header_data_mapping = common_table_info_dict.get(table_name)
                table_header_data_mapping = self.filter_table_header(table_info.get('headers'), table_header_data_mapping)
                common_table_val = self.get_common_table_data(table_name, task_id)
                if hasattr(self.private_mod, 'handle_endpoint_data_to_table_row'):
                    row_list = common_table_val = self.private_mod.handle_endpoint_data_to_table_row(table_header_data_mapping, common_table_val)
                else:
                    row_list = self.handle_endpoint_data_to_table_row(table_header_data_mapping, common_table_val)
                bookmark_type = TemplateBookMarkType.sheet.value
                # table_name实际就是表格名字
                current_table_column_widths = table_info.get('column_width')
                doc_stream = fill_word_bookmark(doc_stream, table_name, row_list, bookmark_type, specific_column_widths=current_table_column_widths)
        doc_stream = self.insert_header_page_number(doc_stream)
        return doc_stream



    # 通用数据的jinja填充数据
    async def common_fill_data_by_jinja(self, doc_stream):
        """
        逻辑: 如果private里面有，但是没有描述position, 那么就从common里面取, 如果描述了position，再说
        """

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
                        # val_key = get_desc.get('position') 
                        # if val_key:
                        #     val = common_val.get(val_key[0])
                        #     if '图片' in k and isinstance(val, str) and self.is_base64(val):
                        #         try:
                        #             python_jinja_mapping[k] = await self.decode_base64_image(bookmark_name=k, tpl=tpl, val=val)
                        #         except Exception as e:
                        #             print(f"{k} 解码失败: {e}")
                        #             [k] = val
                        #     else:
                        #         python_jinja_mapping[k] = val if val else ''
                        #         value_list.append(val)
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
        intermediate_stream = self.fill_template_by_jinja(tpl)
        return intermediate_stream
    
    # 处理position position代表这个数据获取的描述方法。
    async def handle_position(self, private_k, position, value_list):
        val = self.common_val.get(position[0])
        if '图片' in private_k and isinstance(val, str) and self.is_base64(val):
            try:
                self.python_jinja_mapping[private_k] = await self.decode_base64_image(bookmark_name=private_k, tpl=tpl, val=val)
            except Exception as e:
                print(f"{private_k} 解码失败: {e}")
        else:
            self.python_jinja_mapping[private_k] = val if val else ''
            value_list.append(val)
        


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

    def fill_template_by_jinja(self, tpl):
        """
        """
        # 处理python jinja语法变量
        tpl.render(context=self.python_jinja_mapping)
        # 写入内存流，返回
        output_stream = BytesIO()
        tpl.save(output_stream)
        output_stream.seek(0)  # 很重要：回到开头，供后续读取
        return output_stream
    
    def get_common_table_data(self, table_name: str, task_id: str) -> dict:
        template_common_url = os.getenv('TEMPLATE_COMMON_TABLE_URL') + '?taskId=' + urllib.parse.quote(str(task_id), safe='') + '&reportName=' + table_name
        print(f"DEBUG: 请求URL: {template_common_url}")
        print(f"DEBUG: 原始task_id: {repr(task_id)}")
        res = requests.get(template_common_url)
        if res.status_code == 200:
            common_table_val = res.json().get('data')
        else:
            print("请求通用b表格据失败, url:", template_common_url)
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
    
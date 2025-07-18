import os
import importlib
from io import BytesIO
from dotenv import load_dotenv

import requests
from docxtpl import DocxTemplate

from constants.template_constant import GetTypeConstant, FillTypeConstant

load_dotenv(override=True)

class FillDataUtils():
    def __init__(self, name):
        self.name = name

    def fill_data(self, doc_stream, task_id):

        template_common_url = os.getenv('TEMPLATE_COMMON_VAR_URL') + '?taskId=' + task_id
        res = requests.get(template_common_url)
        if res.status_code == 200:
            common_val = res.json().get('data')
        else:
            print("请求通用数据失败, url:", template_common_url)
            common_val = {}

        # 先加载通用数据
        module_name = "template_structure." + 'common_data'  # 比如 name = "my_template"
        common_mod = importlib.import_module(module_name)
        common_key = common_mod.data


        module_name = "template_structure." + self.name  # 比如 name = "my_template"
        private_mod = importlib.import_module(module_name)
        private_key = private_mod.python_template_var

        get_data_from_common_data_jinja = [] # 这个数据从通用里面取 然后jinja填充
        get_data_from_common_data_bookmark = [] # 这个数据从通用里面取 然后书签填充 
        get_data_from_endpoint_jinja = [] # 这个数据从接口取 然后jinja填充
        get_data_from_endpoint_bookmark = [] # 这个数据从接口取 然后书签填充
        get_data_from_database_jinja = [] # 这个数据从数据库取 然后jinja填充
        get_data_from_database_bookmark = [] # 这个数据从数据库取 然后书签填充

        for k, item in private_key.items():
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
            doc_stream = self.common_fill_data_by_jinja(private_key, common_key, common_val, doc_stream)
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

        return doc_stream



    # 通用数据的jinja填充数据
    def common_fill_data_by_jinja(self, private_key, common_key, common_val, doc_stream):
        """
        逻辑: 如果private里面有，但是没有描述position, 那么就从common里面取, 如果描述了position，再说
        """
        python_jinja_mapping = {}
        for k, v_dict in private_key.items():
            if v_dict.get('position'):
                pass
            else:
                if k in common_key:
                    get_desc = common_key[k]
                    if get_desc.get('position'):
                        val_key = get_desc.get('position') 
                        if val_key:
                            val = common_val.get(val_key[0])
                            python_jinja_mapping[k] = val

        intermediate_stream = self.fill_template_by_jinja(doc_stream, python_template_var_mapping=python_jinja_mapping)
        return intermediate_stream

    # 通用的通过书签填充
    def common_fill_data_by_bookmark(private_key, common_key, common_val, doc_stream):
        pass

    # 通过接口获取数据然后jinja填充
    def endpoint_fill_data_by_jinja():
        pass

    # 通过接口获取数据然后书签填充
    def endpoint_fill_data_by_bookmark():
        pass

    # 通过数据库获取数据然后jinja填充
    def database_fill_data_by_jinja():
        pass

    # 通过数据库获取数据然后书签填充
    def database_fill_data_by_bookmark():
        pass

    def fill_template_by_jinja(self, doc_stream, python_template_var_mapping):
        """
        """
        tpl = DocxTemplate(doc_stream)
        # 处理python jinja语法变量
        tpl.render(context=python_template_var_mapping)
        # 写入内存流，返回
        output_stream = BytesIO()
        tpl.save(output_stream)
        output_stream.seek(0)  # 很重要：回到开头，供后续读取
        return output_stream




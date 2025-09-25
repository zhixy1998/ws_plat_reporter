
import os
import re
import base64
import importlib
import urllib.parse
from io import BytesIO
from typing import List, Dict
from dotenv import load_dotenv

import requests
from docx import Document
from docx.shared import Cm
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from docxtpl import InlineImage, DocxTemplate

from app.db import execute_safe_sql
from exceptions.error import ErrorCode
from utils.EditDocxXML import fill_word_bookmark
from constants.template_constant import MeasureType
from exceptions.command_exception import APIException
from constants.template_constant import TemplateBookMarkType
from app.template_doc.model.template_bookmark import TemplateBookmark
from constants.template_constant import GetTypeConstant, FillTypeConstant
from utils.table_data_processor import TableDataProcessor, GetHeaderAndData

common_data_mapping = {
    # 光谱
    MeasureType.spectral_scanning.decs: {
        '仪器型号': 'instrumentModel',
        '仪器序号': 'instrumentSerialNumber',
        '光谱带宽': 'spectrumBandwidth',
        '扫描范围': 'scanRange',
        '光度模式': 'luminosityMode',
        '增益': 'gain',
        '扫描间隔': 'timeInterval',
        '扫描速度': 'scanSpeed',
        '数据文件': 'taskName',
        '分析时间': 'detectionEndTime',
        '方法信息': 'methodName',
        '检测项目': 'project',
        '备注': 'remark',
        '光谱扫描图片': 'spectrumScanImage'
    },
    # 时间
    MeasureType.time_scanning.decs: {
        '仪器型号': 'instrumentModel',
        '仪器序号': 'instrumentSerialNumber',
        '光谱带宽': 'spectrumBandwidth',
        '光度模式': 'luminosityMode',
        '时间单位': 'timeUnit',
        '扫描时间': 'scanTime',
        '时间间隔': 'timeInterval',
        '采样数': 'totalNumber',
        '测量波长': 'instrumentWavelength',
        '数据文件': 'taskName',
        '分析时间': 'detectionEndTime',
        '方法信息': 'methodName',
        '检测项目': 'project',
        '备注': 'remark',
        '时间扫描图片': 'timeScanImage'
    },
    # 定量测定
    MeasureType.quantitative_determination.decs: {

    },
    # 光度测定
    MeasureType.photometric_measurement.decs: {
        '仪器型号': 'instrumentModel',
        '仪器序号': 'instrumentSerialNumber',
        '光谱带宽': 'spectrumBandwidth',
        '数据文件': 'taskName',
        '分析时间': 'detectionEndTime',
        '方法信息': 'methodName',
        '检测项目': 'project',
        '备注': 'remark',
    },
}

load_dotenv(override=True)

class ClassicFillDataUtils():
    def __init__(self, name, template_id, measure_type):
        self.name = name
        self.sample_id = None
        private_mod = None
        self.template_id = template_id
        self.common_val = None   # 代表通用数据接口返回的数据
        self.common_key = None   # 代表通用数据的描述
        self.private_key = None  # 代表私有数据的描述
        self.python_jinja_mapping = {}
        self.table_contexts = {}
        self.end_point_header_and_data = None
        self.measure_type = measure_type

    async def fill_data(self, doc_stream, task_id, sample_id=None, serial_number=None):
        common_val = self.get_common_data_by_endpoint(task_id, sample_id, serial_number)

        end_point_header_and_data = self.get_table_head_data_from_endpoint(task_id, sample_id)
        self.end_point_header_and_data = end_point_header_and_data

        tpl = DocxTemplate(doc_stream)
        contexts = await self.get_context(tpl)
        tpl.render(context=contexts)
        output_stream = BytesIO()
        tpl.save(output_stream)
        output_stream.seek(0)  # 很重要：回到开头，供后续读取

        return output_stream

    async def get_context(self, tpl):
        contexts = {}
        print(self.end_point_header_and_data)
        # 光谱扫描
        if self.measure_type == MeasureType.spectral_scanning.decs:
            spectral_scanning_mapping = common_data_mapping.get(self.measure_type)
            for jinja_val, common_val_key in spectral_scanning_mapping.items():
                if jinja_val == '光谱扫描图片':
                    img_base64 = self.common_val.get(common_val_key)
                    contexts[jinja_val] = await self.decode_base64_image(tpl, img_base64)
                elif jinja_val == '扫描范围':
                    scan_range = self.common_val.get('startWaveLength')  + '至' + self.common_val.get('endWaveLength')
                    contexts[jinja_val] = scan_range
                else:
                    contexts[jinja_val] = self.common_val.get(common_val_key) if self.common_val.get(common_val_key) else ''
            header_list = self.end_point_header_and_data.get('headList')
            data_list = self.end_point_header_and_data.get('dataList')
            rows = []
            for data in data_list:
                row = {}
                row['序号'] = data.get('id')
                row['峰_谷'] = data.get('peakValley') if data.get('peakValley') else ''
                row['波长'] = data.get('waveLength') if data.get('waveLength') else ''
                row['es'] = data.get('luminosity') if data.get('luminosity') else ''
                row['备注'] = data.get('remark') if data.get('remark') else ''
                rows.append(row)
            contexts['rows'] = rows

        # 时间扫描
        if self.measure_type == MeasureType.time_scanning.decs:
            time_scanning_mapping = common_data_mapping.get(self.measure_type)
            for jinja_val, common_val_key in time_scanning_mapping.items():
                if jinja_val != '时间扫描图片':
                    contexts[jinja_val] = self.common_val.get(common_val_key) if self.common_val.get(common_val_key) else ''
                else:
                    img_base64 = self.common_val.get(common_val_key)
                    contexts[jinja_val] = await self.decode_base64_image(tpl, img_base64)
        # 定量
        if self.measure_type  == MeasureType.quantitative_determination.decs:
            # origin_header_real_header_mapping, tpl_context = await self.get_quantitative_determination_photometric_measurement_from_endpoint(doc_stream, task_id)
            quantitative_determination = common_data_mapping.get(self.measure_type)
            for jinja_val, common_val_key in quantitative_determination.items():
                contexts[jinja_val] = self.common_val.get(common_val_key) if self.common_val.get(common_val_key) else ''
            header_list = self.end_point_header_and_data.get('headList')
            data_list = self.end_point_header_and_data.get('dataList')
            abs_identity = None
            same_number_identity = 'sampleNumber'
            for header in header_list:
                if header.get('locate') == 'measure' and 'Abs' in header.get('name'):
                    abs_identity = header.get('identity')

            rows = []
            for index, data in enumerate(data_list):
                row = {'序号': index + 1}
                same_number = data.get(same_number_identity) if data.get(same_number_identity) else ''
                row['编号'] = same_number
                row['模式'] = self.common_val.get('luminosityMode') if self.common_val.get('luminosityMode') else ''
                row['波长'] = data.get(abs_identity) if data.get(abs_identity) else ''
                rows.append(row)
            contexts['rows'] = rows
            contexts['波长'] = str(abs_identity.split('-')[0])
        # 光度测量
        if self.measure_type  == MeasureType.photometric_measurement.decs:
            # origin_header_real_header_mapping, tpl_context = await self.get_quantitative_determination_photometric_measurement_from_endpoint(doc_stream, task_id)
            photometric_measurement = common_data_mapping.get(self.measure_type)
            for jinja_val, common_val_key in photometric_measurement.items():
                contexts[jinja_val] = self.common_val.get(common_val_key) if self.common_val.get(common_val_key) else ''
            header_list = self.end_point_header_and_data.get('headList')
            data_list = self.end_point_header_and_data.get('dataList')
            abs_identity = None
            same_number_identity = 'sampleNumber'
            for header in header_list:
                if header.get('locate') == 'measure' and 'Abs' in header.get('name'):
                    abs_identity = header.get('identity')

            rows = []
            for index, data in enumerate(data_list):
                row = {'序号': index + 1}
                same_number = data.get(same_number_identity) if data.get(same_number_identity) else ''
                row['编号'] = same_number
                row['模式'] = self.common_val.get('luminosityMode') if self.common_val.get('luminosityMode') else ''
                row['波长'] = data.get(abs_identity) if data.get(abs_identity) else ''
                rows.append(row)
            contexts['rows'] = rows
            contexts['波长'] = str(abs_identity.split('-')[0])

        return contexts

    def get_common_data_by_endpoint(self, task_id, sample_id, serial_number):
        template_common_url = os.getenv('TEMPLATE_COMMON_VAR_URL') + '?taskId=' + urllib.parse.quote(str(task_id), safe='')+ '&sampleId=' + urllib.parse.quote(str(sample_id), safe='') + '&serialNumber=' + urllib.parse.quote(str(serial_number), safe='')
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
        return common_val

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
        
    def fill_template_by_jinja(self, tpl):
        """
        """
        # 合并context
        final_context = self.python_jinja_mapping.copy()
        if additional_context:
            final_context.update(self.table_contexts)
            # print("Merged context:", final_context)
        # 处理python jinja语法变量
        tpl.render(context=final_context)
        # 写入内存流，返回
        output_stream = BytesIO()
        tpl.save(output_stream)
        output_stream.seek(0)  # 很重要：回到开头，供后续读取
        
        # 移除表格中的空行
        output_stream = self.remove_empty_table_rows(output_stream)
        
        return output_stream
    
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
    
    async def decode_base64_image(self, tpl, val):
        try:
            image_data = base64.b64decode(val)
            image_stream = BytesIO(image_data)
            return InlineImage(tpl, image_stream, width=Cm(10))  # 根据需要调整宽度
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
    
    def fill_template_jinja_custom_info(self,doc_stream, custom_info=None, additional_context=None):
        """
        doc_stream    模板文件流
        custom_info   自定义标签信息
        """
        module_name = "template_structure." + self.name
        try:
            private_mod = importlib.import_module(module_name)
        except Exception as e:
            private_mod = None
        if private_mod and hasattr(private_mod, 'custom_bookmark'):
            custom_bookmark=private_mod.custom_bookmark
        else:
            custom_bookmark = {'note': '备注', 'project_name': '项目名称'}

        try:
            from docxtpl import DocxTemplate
            from io import BytesIO

            # 创建DocxTemplate对象
            tpl = DocxTemplate(doc_stream)

            # 获取模板中所有未声明的变量
            undeclared_vars = tpl.get_undeclared_template_variables()

            blank_context = {}
            for var in undeclared_vars:
                blank_context[var] = ""
            if custom_info:
                for i in undeclared_vars:
                    if i in custom_bookmark['project_name']:
                        blank_context[i] = custom_info.get('project_name')
                    if i in custom_bookmark['note']:
                        blank_context[i] = custom_info.get('note')

            # 为所有未声明的变量创建空字符串映射

            # 如果没有未声明的变量，直接返回原文档
            if not blank_context:
                doc_stream.seek(0)
                return doc_stream
            if additional_context:
                blank_context.update(additional_context)
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
    
    async def get_quantitative_determination_photometric_measurement_from_endpoint(self, doc_stream, task_id, origin_header_real_header_mapping={}, tpl_context={}):
        table_data_processor = TableDataProcessor(self.name)
        table_fields = table_data_processor.get_table_fields()
        if table_fields:
            if not hasattr(table_data_processor.handler_instance, 'HEADER_M_MAPPING'):
                raise APIException(error=ErrorCode.TABLE_DATA_HANDLER_NOT_FOUND)
            HEADER_M_MAPPING = table_data_processor.handler_instance.HEADER_M_MAPPING  # 每个私有文件都要声明的
            TABLE_NAME_MAP_REVERSE = table_data_processor.handler_instance.TABLE_NAME_MAP_REVERSE
            # get_header_and_data_class_instance = GetHeaderAndData(task_id)
            # await get_header_and_data_class_instance._get_all_headers()
            self.HEADER_M_MAPPING = HEADER_M_MAPPING
            # total_handler_list = table_data_processor.list_available_handlers()
            # for handler in total_handler_list:
            #     handler()
            standard = table_data_processor.handler_instance.standard
            if not standard:
                standard = []
            origin_header_data_mapping = {}
            last_unknown_origin_header = None
            print('TABLE_NAME_MAP_REVERSE', TABLE_NAME_MAP_REVERSE)
            for table_name, origin_header_list in TABLE_NAME_MAP_REVERSE.items():
                table_origin_header_data_mapping = {}  # 每个表格单独的数据映射
                for origin_header in origin_header_list:
                    m = HEADER_M_MAPPING.get(origin_header)
                    if origin_header in standard:
                        # 标准样处理
                        handler = getattr(table_data_processor.handler_instance, 'handle_' + origin_header)
                        real_header, sample_data = handler(self.end_point_header_and_data, m)
                        for index, data in enumerate(sample_data):
                            tpl_context[origin_header + '_' + str(index)] = data
                            origin_header_real_header_mapping[origin_header] = real_header if real_header else '' # old_header 标签名字
                    else:
                        # 未知样处理
                        real_header, identity = self.get_unknown_sample_header(m)
                        origin_header_real_header_mapping[origin_header] = real_header if real_header else ''
                        if identity:
                            data = self.get_unknown_sample_data(identity)
                            table_origin_header_data_mapping[origin_header] = data
                
                # 为每个表格生成行数据
                if table_origin_header_data_mapping:
                    rows = self.columns_to_rows(table_origin_header_data_mapping)
                    rows_name = table_name + '_rows'
                    tpl_context[rows_name] = rows
        return origin_header_real_header_mapping, tpl_context
    
    def get_table_head_data_from_endpoint(self, task_id, sample_id):
        template_common_url = os.getenv('TEMPLATE_TABLE_HEAD_DATA_URL') + '?taskId=' + urllib.parse.quote(str(task_id), safe='') + '&sampleId=' + urllib.parse.quote(str(sample_id), safe='')
        response = requests.get(template_common_url)
        res_json = response.json()
        # print(res_json)
        return res_json.get('data')

    def get_unknown_sample_header(self, m) -> (str, str):
        """
        未知样品:
            头: 
                1 去mapRelation list[dict] 里面取  paramIdentity=m 然后取headIdentity = identity 
                    真实表头 paramName
                    if paramName is None:
                        拿  identity  去 unknowHeadList 匹配 identity 取 printTitle 就是真实的表头
                2 去unknowHeadList 里面找
                    identity = m    printTitle就是真实的表头
            数据:
                unknowDataList 
                根据identity取数据
        """
        identity = None
        real_header = None
        if self.end_point_header_and_data:
            map_relation = self.end_point_header_and_data.get('mapRelation')
            for one_map_relation in map_relation:
                if one_map_relation.get('paramIdentity') == m:
                    identity = one_map_relation.get('headIdentity')
                    real_header = one_map_relation.get('paramName')
                    if not real_header:
                        unknown_header_list = self.end_point_header_and_data.get('unknowHeadList')
                        for one_unknown_header in unknown_header_list:
                            if one_unknown_header.get('identity') == identity:
                                real_header = one_unknown_header.get('printTitle')
        if identity is None and real_header is None:
            unknown_header_list = self.end_point_header_and_data.get('unknowHeadList')
            for one_unknown_header in unknown_header_list:
                if one_unknown_header.get('identity') == m:
                    real_header = one_unknown_header.get('printTitle')
                    identity = m
        return real_header, identity


    def get_unknown_sample_data(self, identity: str) -> List[str]:
        """
        未知样品:
            头: 
                1 去mapRelation list[dict] 里面取  paramIdentity=m 然后取headIdentity = identity 
                    真实表头 paramName
                    if paramName is None:
                        拿  identity  去 unknowHeadList 匹配 identity 取 printTitle 就是真实的表头
                2 去unknowHeadList 里面找
                    identity = m    printTitle就是真实的表头
            数据:
                unknowDataList 
                根据identity取数据
        """
        data = []
        for one_unknown_data in self.end_point_header_and_data.get('unknowDataList'):
            if one_unknown_data.get(identity) or one_unknown_data.get(identity) == '':
                data.append(one_unknown_data.get(identity))
        return data
    
    @staticmethod
    def columns_to_rows(data: Dict[str, List]) -> List[Dict]:
        """
        将 {'a':[1,2,3], 'b':[4,5,6], 'c':[7,8,9]}
        转成 [{'a':1,'b':4,'c':7}, {'a':2,'b':5,'c':8}, {'a':3,'b':6,'c':9}]
        """
        if not data:
            return []
        keys = list(data.keys())
        columns = [data[k] for k in keys]
        return [dict(zip(keys, row)) for row in zip(*columns)]
    
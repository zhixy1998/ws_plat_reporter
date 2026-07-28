"""
表格数据处理工具类
用于动态导入模板配置文件并处理表格数据映射关系
"""
import sys
import importlib
import json
from typing import Dict, List, Any, Optional, Tuple
from exceptions.error import ErrorCode
from exceptions.command_exception import APIException
from app.db import execute_safe_sql
from config import config

class TableDataProcessor:
    """表格数据处理器，负责动态加载模板配置并处理表格数据"""
    
    def __init__(self, template_name: str, structure_path=config.structure_module):
        """
        初始化表格数据处理器
        
        Args:
            template_name: 模板名称，如 '光度测量报告模版_test'
        """
        self.template_name = template_name
        self.template_module = None
        self.handler_instance = None
        self.structure_path = structure_path
        self._load_template_module()
    
    def _load_template_module(self):
        """动态加载模板配置模块（绕过 sys.modules 缓存以确保读取最新内容，同时支持相对导入）"""
        import importlib.util
        import os

        try:
            full_module_name = f"{self.structure_path}.{self.template_name}"

            # 确保父包已在 sys.modules 中（相对导入解析时需要从此处查找兄弟模块）
            # 同时通过父包的 __path__ 拿到磁盘上的绝对路径，避免依赖当前工作目录
            if self.structure_path not in sys.modules:
                importlib.import_module(self.structure_path)
            parent_pkg = sys.modules[self.structure_path]
            base_dir = parent_pkg.__path__[0]
            file_path = os.path.join(base_dir, f"{self.template_name}.py")

            spec = importlib.util.spec_from_file_location(full_module_name, file_path)
            if spec and spec.loader:
                self.template_module = importlib.util.module_from_spec(spec)
                # 设置 __package__，使模板文件内的相对导入（如 from .common_data import ...）能正常解析
                self.template_module.__package__ = self.structure_path
                # 临时注册，exec_module 期间相对导入需要通过 sys.modules 查找父包
                sys.modules[full_module_name] = self.template_module
                try:
                    spec.loader.exec_module(self.template_module)
                finally:
                    # 加载完成后移出缓存，确保下次调用时仍重新从磁盘读取最新内容
                    sys.modules.pop(full_module_name, None)
            else:
                from utils.template_utils import import_template_module
                self.template_module = import_template_module(self.structure_path, self.template_name)

            # 检查是否有TableDataHandler类
            if hasattr(self.template_module, 'TableDataHandler'):
                self.handler_instance = self.template_module.TableDataHandler()
        except Exception as e:
            print(f"动态加载模板失败 [{self.template_name}]: {e}")
            raise APIException(error=ErrorCode.TEMPLATE_NOT_FOUND)
    
    def get_known_sample_jinja_v(self):
        if hasattr(self.template_module, 'known_sample_jinja_v'):
            return self.template_module.known_sample_jinja_v
        else:
            return 'known_sample_sub_table'
    
    def get_table_fields(self) -> List[Dict]:
        """获取表格字段配置"""
        if not self.template_module or not hasattr(self.template_module, 'table_fields'):
            return []
        return self.template_module.table_fields
    
    def process_table_data(self, table_name: str, data_list: List[Dict], context: Optional[Dict] = None) -> List[List[str]]:
        """
        处理表格数据，根据映射关系和处理函数生成表格行数据
        
        Args:
            table_name: 表格名称
            data_list: 原始数据列表
            context: 上下文数据
            
        Returns:
            处理后的表格行数据
        """
        if not self.handler_instance:
            return []
        
        return 
    
    def has_custom_handler(self) -> bool:
        """检查是否有自定义处理器类"""
        return self.handler_instance is not None
    
    def get_HEADER_M_MAPPING(self) -> Dict[str, str]:
        """获取列映射配置"""
        if self.handler_instance and hasattr(self.handler_instance, 'HEADER_M_MAPPING'):
            return self.handler_instance.HEADER_M_MAPPING
        return {}
    
    def list_available_handlers(self) -> List[str]:
        """列出所有可用的处理方法"""
        if not self.handler_instance:
            return []
        
        handlers = []
        for attr_name in dir(self.handler_instance):
            if attr_name.startswith('handle_') and callable(getattr(self.handler_instance, attr_name)):
                handlers.append(attr_name)
        
        return handlers



class GetHeaderAndData():

    def __init__(self, task_id) -> None:
        self.task_id = task_id
        self.all_headers = []
        self.method_key = None  # 方法key
        self.map_relation = None
        self.m_data_key = None # 用来找m的数据的key
        # 注意：不能在__init__中调用异步方法，需要手动调用 await instance._get_all_headers()
        self.header_identity_map_list = []
        self.tel_val_data_list = {} # {tel_val: []}
        self.measure_data_id = None
    
    async def _get_all_headers(self):
        table_info_sql = "SELECT method_key, sample_key, table_info FROM t_measure_task WHERE id = %s and is_delete = 0"
        table_info_sql_result = await execute_safe_sql(table_info_sql, [self.task_id], return_dict=True)
        if table_info_sql_result:
            # 修复：直接使用查询结果，不需要json.loads
            result_row = table_info_sql_result[0]
            
            self.method_key = result_row.get('method_key')
            if result_row.get('sample_key'):
                self.sample_key = json.loads(result_row.get('sample_key'))
            
            # table_info可能是字符串，需要解析
            table_info_raw = result_row.get('table_info')
            if isinstance(table_info_raw, str):
                table_info = json.loads(table_info_raw)
            else:
                table_info = table_info_raw
            
            if table_info:
                self.map_relation = table_info.get('unknownHead').get('mapRelation')
                if table_info.get('taskHeads'):
                    self.all_headers = table_info.get('taskHeads')
                if table_info.get('sampleHeads'):
                    self.all_headers.extend(table_info.get('sampleHeads'))
    
    async def get_header(self, m) -> Tuple[bool, Optional[str]]:
        """
        m代表这个表头对应的数据库的标识
        比如在私有文件配置 “序号” = x1
        那么m = x1 传递过来的就是x1 取数据库找标识为x1的表头和值
        这个函数是找表头
        """
        identify = None
        measurement_param_info_sql = 'select measurement_param_info from t_measure_method where id = %s'
        measurement_param_info_sql_result = await execute_safe_sql(measurement_param_info_sql, [self.method_key], return_dict=True)
        if measurement_param_info_sql_result:
            measurement_param_info_raw = measurement_param_info_sql_result[0].get('measurement_param_info')
            # 修复：检查 measurement_param_info 是否为空
            if measurement_param_info_raw:
                # 如果是字符串，需要解析JSON
                if isinstance(measurement_param_info_raw, str):
                    measurement_param_info = json.loads(measurement_param_info_raw)
                else:
                    measurement_param_info = measurement_param_info_raw
                
                sample_input_params = measurement_param_info.get('sampleInputParams', [])
                for sample_input_param in sample_input_params:
                    if sample_input_param.get('resultIdentity') == m:
                        identify = sample_input_param.get('resultIdentity')
                        break 
        real_header = None 
        if self.map_relation:
            for map_relation_one in self.map_relation:
                if map_relation_one.get('paramIdentity') == identify:
                    self.m_data_key = map_relation_one.get('headIdentity')
                    real_header = map_relation_one.get('headName') # 用户手输的
                    # return map_relation_one.get('paramName')  # 方法的名字
        if real_header:
            return True, real_header
        else:
            # 修复：检查 self.all_headers 是否为空
            if self.all_headers:
                for header_info in self.all_headers:
                    if header_info.get('identity') == m:
                        self.m_data_key = header_info.get('identity')
                        return True, header_info.get('printTitle')
        # 如果都没找到，返回None或空字符串
        return False, None
    
    async def get_data(self):
        for sample_key_map in self.sample_key:
            sample_key = sample_key_map.get('specimenKey')
            if sample_key:
                # 1 先从样品表去数据
                sample_data_sql = "SELECT * FROM t_measure_sample WHERE id = %s"
                sample_data_sql_result = await execute_safe_sql(sample_data_sql, [sample_key], return_dict=True)
                if sample_data_sql_result:
                    sample_data = sample_data_sql_result[0]
                    new_col_data = sample_data.get('new_col_data')                    
                    if new_col_data:
                        new_col_data = json.loads(new_col_data)
                        for header_identity_map in self.header_identity_map_list:
                            tel_val = header_identity_map.get('tel_val')
                            identity = header_identity_map.get('identity')
                            if identity in new_col_data:
                                self.tel_val_data_list.setdefault(tel_val, []).append(new_col_data.get(identity))             
                # 2 从测量数据表取数据 
                measure_data_sql = "SELECT * FROM t_measure_data WHERE task_id = %s and sample_key = %s order by serial_number desc limit 1" 
                measure_data_sql_result = await execute_safe_sql(measure_data_sql, [self.task_id, sample_key], return_dict=True) 
                if measure_data_sql_result:
                    measure_data = measure_data_sql_result[0]
                    self.measure_data_id = measure_data.get('id')
                    original_calculation_data = json.loads(measure_data.get('original_calculation_data'))
                    result_original_calculation_data = [o for o in original_calculation_data if o.get('identity') == 'result']
                    if result_original_calculation_data:
                        for result_original_calculation_data_one in result_original_calculation_data:
                            if result_original_calculation_data_one.get('data'):
                                original_data = result_original_calculation_data_one.get('data')
                                for header_identity_map in self.header_identity_map_list:
                                    tel_val = header_identity_map.get('tel_val')
                                    identity = header_identity_map.get('identity')
                                    if identity in original_data:
                                        self.tel_val_data_list.setdefault(tel_val, []).append(original_data.get(identity))             
                # 3 从分析数据表取数据
                analysis_result_list = await self.get_analysis_data(sample_key) 
                if analysis_result_list:
                    analysis_result_list = json.loads(analysis_result_list)
                    for analysis_result_one in analysis_result_list:
                        if analysis_result_one:
                            result_identity = analysis_result_one.get('resultIdentity')
                            formula_text = analysis_result_one.get('formulaText')
                            if result_identity and formula_text:
                                key = result_identity + '_' + formula_text
                                for header_identity_map in self.header_identity_map_list:
                                    tel_val = header_identity_map.get('tel_val')
                                    identity = header_identity_map.get('identity')
                                    if identity == key:
                                        self.tel_val_data_list.setdefault(tel_val, []).append(analysis_result_one.get('countValue'))             
                        


    

    async def get_original_data(self):
        measure_task_sql = "SELECT sample_key FROM t_measure_task WHERE id = %s"
        measure_task_sql_result = await execute_safe_sql(measure_task_sql, [self.task_id], return_dict=True)
        if measure_task_sql_result:
            sample_key_list_json = measure_task_sql_result[0].get('sample_key')
            if sample_key_list_json:
                sample_key_list = json.loads(sample_key_list_json)
                for sample_key_dict in sample_key_list:
                    if sample_key_dict.get('isTested') == '1' and sample_key_dict.get('deleteType') == '0':
                        self.sample_key_list.append(sample_key_dict.get('specimenKey'))
        if self.sample_key_list:
            for sample_key in self.sample_key_list:
                measure_data_sql = "SELECT id, original_calculation_data, serial_number FROM t_measure_data WHERE task_id = %s and sample_key = %s order by serial_number desc limit 1"
                measure_data_sql_result = await execute_safe_sql(measure_data_sql, [self.task_id, sample_key], return_dict=True)
                if measure_data_sql_result:
                    original_calculation_data = measure_data_sql_result[0].get('original_calculation_data')
                    self.original_calculation_data_list.append(json.loads(original_calculation_data))
                self.measure_data_id_list.append(measure_data_sql_result[0].get('id'))
        return self.original_calculation_data_list
    
    async def get_analysis_data(self, sample_key):
        if self.measure_data_id:
            analysis_data_sql = "select analysis_result from t_measure_analysis_data where task_id = %s and measure_data_id = %s and sample_key = %s order by data_version desc limit 1"
            analysis_data_sql_result = await execute_safe_sql(analysis_data_sql, [self.task_id, self.measure_data_id, sample_key], return_dict=True)
            if analysis_data_sql_result:
                analysis_result = analysis_data_sql_result[0].get('analysis_result')
                self.analysis_result = analysis_result
                return analysis_result
            return None
    
    async def get_all_m(self):
        m_list = []
        measurement_param_info_sql = 'select measurement_param_info from t_measure_method where id = %s'
        measurement_param_info_sql_result = await execute_safe_sql(measurement_param_info_sql, [self.method_key], return_dict=True)
        if measurement_param_info_sql_result:
            measurement_param_info_raw = measurement_param_info_sql_result[0].get('measurement_param_info')
            # 修复：检查 measurement_param_info 是否为空
            if measurement_param_info_raw:
                # 如果是字符串，需要解析JSON
                if isinstance(measurement_param_info_raw, str):
                    measurement_param_info = json.loads(measurement_param_info_raw)
                else:
                    measurement_param_info = measurement_param_info_raw
                
                sample_input_params = measurement_param_info.get('sampleInputParams', [])
                for sample_input_param in sample_input_params:
                    m_list.append(sample_input_param.get('resultIdentity'))
            # 修复：检查 self.all_headers 是否为空
        if self.all_headers:
            for header_info in self.all_headers:
                m_list.append(header_info.get('identity'))
        return m_list

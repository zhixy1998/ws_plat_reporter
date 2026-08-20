# 模板字段定义
# fill_type: 0 表示从模板中提取的字段, fill_type: 1 表示表格截取的字段

# get_type: 0: 表示从通用数据中取, 1: 表示从接口中取 2: 表从数据库中取

from .common_data import BaseTableDataHandler, checkbox
python_template_var = {
    "project": {"fill_type": 0},
    "solution_concentration": {"fill_type": 0},
    "instrument_num": {"fill_type": 0},
    "known_sample_sub_table": {"fill_type": 0},
    "storage_condition": {"fill_type": 0},
    "instrument_name": {"fill_type": 0},
    "remark": {"fill_type": 0},
    "detection_basis": {"fill_type": 0},
    "calculation_formula": {"fill_type": 0},
    "standard_solution_number": {"fill_type": 0},
    "b": {"fill_type": 0},
    "t3_h": {"fill_type": 0},
    "sample_status": {"fill_type": 0},
    "t": {"fill_type": 0},
    "t4_h": {"fill_type": 0},
    "r": {"fill_type": 0},
    "t1_h": {"fill_type": 0},
    "detection_time": {"fill_type": 0},
    "t5_h": {"fill_type": 0},
    "grouped_data": {"fill_type": 0},
    "a": {"fill_type": 0},
    "t2_h": {"fill_type": 0},
    "sample_preparation": {"fill_type": 0},
    "rh": {"fill_type": 0},
    "t6_h": {"fill_type": 0},
    "regression_equation": {"fill_type": 0}
}

# 标题映射（包含字体和字号信息）
title_mapping = {
    'project_t': {'name': '检测项目', 'font': '宋体', 'font_size': 12},
    'storage_condition_t': {'name': '存放条件', 'font': '宋体', 'font_size': 12},
    'remark_t': {'name': '备注', 'font': '宋体', 'font_size': 12},
    'detection_basis_t': {'name': '检测依据', 'font': '宋体', 'font_size': 12},
    'sample_preparation_t': {'name': '样品前处理', 'font': '宋体', 'font_size': 12},
    'sample_status_t': {'name': '样品状态', 'font': '宋体', 'font_size': 12},
    'standard_solution_number_t': {'name': '标准溶液及编号', 'font': '宋体', 'font_size': 12},
    'instrument_name_t': {'name': '仪器名称', 'font': '宋体', 'font_size': 12},
    'trh_t': {'name': '环境条件', 'font': '宋体', 'font_size': 12},
    'regression_equation_t': {'name': '回归方程', 'font': '宋体', 'font_size': 12},
    'instrument_num_t': {'name': '仪器编号', 'font': '宋体', 'font_size': 12},
    'solution_concentration_t': {'name': '溶液浓度()', 'font': '宋体', 'font_size': 12},
    'calculation_formula_t': {'name': '计算公式', 'font': '宋体', 'font_size': 12},
    'detection_time_t': {'name': '分析日期', 'font': '宋体', 'font_size': 12}
}

# 字段渲染表格
extra_info = {
    'remark': {'value': '', 'font_size': 12, 'font': '宋体'},  # 备注
    'page_num_type': 0,

    # 页眉页脚：左中右三段，type=0 关联 title_mapping 字段（value 为字段名），type=1 自定义文本，value 为空不展示
    'left_header': {'type': 1, 'value': '', 'font': '宋体', 'font_size': 10, 'position': 'left'},
    'mid_header': {'type': 1, 'value': '', 'font': '宋体', 'font_size': 10, 'position': 'center'},
    'right_header': {'type': 1, 'value': '', 'font': '宋体', 'font_size': 10, 'position': 'right'},
    'left_footer': {'type': 1, 'value': '', 'font': '宋体', 'font_size': 9, 'position': 'left'},
    'mid_footer': {'type': 1, 'value': '', 'font': '宋体', 'font_size': 9, 'position': 'center'},
    'right_footer': {'type': 1, 'value': '', 'font': '宋体', 'font_size': 9, 'position': 'right'},
    # 页码（position: left / center / right）
    'page_num': {'position': 'left', 'font': '宋体', 'font_size': 9},
    # 报告标题
    'title_list': [
        {'name': '报告名称', 'value': '定量测定原始数据', 'font': '黑体', 'font_size': 15},
    ],
    # 动态边距（mm），前端自由输入
    'margin': {'value': '20'},
    # 横向/纵向：0=纵向（portrait）| 1=横向（landscape）
    'orientation': {'value': 0},
    # 行边距（line-height 倍数）
    'line_height': {'value': '1.5'},
}


class TableDataHandler(BaseTableDataHandler):
    """表格数据处理类，用于处理数据映射和处理逻辑"""
    
    # 简单字段映射：表头名称 -> 数据库字段名
    STAND = ['normalConcentration', 'Abs', 'sumAbs']
    
    # 简单字段映射：表头名称 -> 数据库字段名
    HEADER_M_MAPPING_LIST = [{
        "t1": "sampleNumber",  
        "t2":"2191OJP", 
        "t3":"2191OJP", 
        "t4":"2191OJP", 
        "t5":"2191OJP", 
        "t6":"Abs",
        "t7":"2191OJP",
    }]

    TABLE_HEADER_MAP = {
        't1_h': '样品编号',
        't2_h': '所取试样体积v（   ）',
        't3_h': '空白吸光度A0（   ）',
        't4_h': '试样吸光度A（   ）',
        't5_h': '由校准曲线上查得的硼含量m（   ）',
        't6_h': '水样中硼含量C（   ）',
        't7_h': '平均值（   ）'
    }

    def __init__(self):
        pass

    def handle_unknown_sample_table(self, fake=False, end_point_header_and_data=None):
        if end_point_header_and_data:
            self.end_point_header_and_data = end_point_header_and_data
        temp_context = {}
        for index, origin_header_map in enumerate(self.HEADER_M_MAPPING_LIST):
            table_name = 'grouped_data'
            table_origin_header_data_mapping = {}  # 每个表格单独的数据映射
            for jinja_header_value, m in origin_header_map.items():
                # 表头映射
                table_title_k = jinja_header_value + '_h'
                if table_title_k not in self.TABLE_HEADER_MAP:
                    print(f'数据字段{jinja_header_value}没有在TABLE_HEADER_MAP中定义，跳过该字段。 应该定义{table_title_k}')
                    continue
                if not fake:
                    real_header, identity = self.table_handle_get_unknown_sample_header(m)
                    temp_context[table_title_k] = real_header if real_header else ''
                    if identity:
                        # 表格数据
                        data = self.table_handle_get_unknown_sample_data(identity)
                        table_origin_header_data_mapping[jinja_header_value] = data
                else:
                    temp_context[table_title_k] = self.TABLE_HEADER_MAP.get(table_title_k)
                    data = [f'样品{n+1}' for n in range(6)]
                    table_origin_header_data_mapping[jinja_header_value] = ['*', '*', '*', '*']
                
            # 为每个表格生成行数据
            if table_origin_header_data_mapping:
                rows = self.columns_to_rows(table_origin_header_data_mapping)
                
                # 将行数据转换为分组格式（每2行一组，t1/t3/t11合并）
                grouped_data = self.convert_to_grouped_format(rows, group_size=2, merge_fields=['t1', 't2', 't7'])
                temp_context['grouped_data'] = grouped_data
        return temp_context
    
    def convert_to_grouped_format(self, rows, group_size=2, merge_fields=None):
        """
        将行数据转换为分组格式，支持合并字段
        
        Args:
            rows (list): 原始行数据列表，每个元素是一个字典
            group_size (int): 每组的行数，默认为2
            merge_fields (list): 需要合并的字段列表，如 ['t1', 't3', 't11']
        
        Returns:
            list: 分组后的数据列表
        """
        if not rows:
            return []
        
        if merge_fields is None:
            merge_fields = []
        
        grouped_data = []
        
        # 按 group_size 分组
        for i in range(0, len(rows), group_size):
            group_rows = rows[i:i + group_size]
            
            if not group_rows:
                continue
            
            # 从第一行提取合并字段的值
            first_row = group_rows[0]
            group_info = {}
            
            # 设置合并字段（从第一行取值）
            for field in merge_fields:
                group_info[field] = first_row.get(field, '')
            
            # 提取每行的非合并字段
            group_info['rows'] = []
            for row in group_rows:
                row_data = {}
                for key, value in row.items():
                    if key not in merge_fields:
                        row_data[key] = value
                group_info['rows'].append(row_data)
            
            grouped_data.append(group_info)
        
        return grouped_data


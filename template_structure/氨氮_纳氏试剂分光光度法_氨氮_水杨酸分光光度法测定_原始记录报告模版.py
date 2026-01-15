# 模板字段定义
# fill_type: 0 表示从模板中提取的字段, fill_type: 1 表示表格截取的字段

# get_type: 0: 表示从通用数据中取, 1: 表示从接口中取 2: 表从数据库中取

from .common_data import BaseTableDataHandler, checkbox
python_template_var = {
    "table_1_rows": {"fill_type": 0},
    "rh": {"fill_type": 0},
    "storage_condition": {"fill_type": 0},
    "project": {"fill_type": 0},
    "instrument_num": {"fill_type": 0},
    "calculation_formula": {"fill_type": 0},
    "remark": {"fill_type": 0},
    "t1_h": {"fill_type": 0},
    "standard_solution_number": {"fill_type": 0},
    "solution_concentration": {"fill_type": 0},
    "instrument_name": {"fill_type": 0},
    "detection_basis": {"fill_type": 0},
    "r": {"fill_type": 0},
    "detection_time": {"fill_type": 0},
    "sample_preparation": {"fill_type": 0},
    "b": {"fill_type": 0},
    "sample_status": {"fill_type": 0},
    "known_sample_sub_table": {"fill_type": 0},
    "t": {"fill_type": 0},
    "regression_equation": {"fill_type": 0},
    "a": {"fill_type": 0}
}

# 标题映射（包含字体和字号信息）
title_mapping = {
    'detection_basis_t': {'name': '检测依据', 'font': '宋体', 'font_size': 12},
    'storage_condition_t': {'name': '存放条件', 'font': '宋体', 'font_size': 12},
    'instrument_name_t': {'name': '仪器名称', 'font': '宋体', 'font_size': 12},
    'sample_preparation_t': {'name': '样品前处理', 'font': '宋体', 'font_size': 12},
    'instrument_num_t': {'name': '仪器编号', 'font': '宋体', 'font_size': 12},
    'calculation_formula_t': {'name': '计算公式', 'font': '宋体', 'font_size': 12},
    'regression_equation_t': {'name': '回归方程', 'font': '宋体', 'font_size': 12},
    'remark_t': {'name': '备注', 'font': '宋体', 'font_size': 12},
    'project_t': {'name': '检测项目', 'font': '宋体', 'font_size': 12},
    'detection_time_t': {'name': '分析日期', 'font': '宋体', 'font_size': 12},
    'sample_status_t': {'name': '样品状态', 'font': '宋体', 'font_size': 12},
    'solution_concentration_t': {'name': '溶液浓度()', 'font': '宋体', 'font_size': 12},
    'trh_t': {'name': '环境条件', 'font': '宋体', 'font_size': 12},
    'standard_solution_number_t': {'name': '标准溶液及编号', 'font': '宋体', 'font_size': 12}
}

# 字段渲染表格
extra_info = {
    'remark':{'value': '', 'font_size': 12, 'font': '宋体'},
    'page_num_type':'0',
}

known_sample_jinja_v = 'known_sample_sub_table'


class TableDataHandler(BaseTableDataHandler):
    """表格数据处理类，用于处理数据映射和处理逻辑"""

    # 标准样的字段，按顺序横向展示
    STAND = ['normalConcentration', 'Abs', 'sumAbs']
    
    # 简单字段映射：表头名称 -> 数据库字段名
    HEADER_M_MAPPING_LIST = [{
        "t1": "sampleNumber",  
        "t2":"2191OJP", 
        "t3":"Abs", 
        "t4":"2191OJP",
        "t5":"2191OJP",
        "t6":"2191OJP",
        "t7":"2191OJP",
    }]

    TABLE_HEADER_MAP = {
        't1_h': '样品编号',
        't2_h': '水样体积V（   ）',
        't3_h': '空白试验吸光度A0',
        't4_h': '水样吸光度A',
        't5_h': '从标准曲线上查得的样品管中氨氮的质量m（   ）',
        't6_h': '水样中氨氮质量浓度ρ(NH3-N)（   ）',
        't7_h': '平均值（    ）',
    }


    
    def __init__(self):
        # TABLE_NAME_MAP_REVERSE = {'表格': ['吸光值']}
        pass
    


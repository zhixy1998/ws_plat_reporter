# 模板字段定义
# fill_type: 0 表示从模板中提取的字段, fill_type: 1 表示表格截取的字段

# get_type: 0: 表示从通用数据中取, 1: 表示从接口中取 2: 表从数据库中取

from .common_data import BaseTableDataHandler, checkbox
python_template_var = {
    "instrument_num": {"fill_type": 0},
    "solution_concentration": {"fill_type": 0},
    "t4_h": {"fill_type": 0},
    "remark": {"fill_type": 0},
    "t7_h": {"fill_type": 0},
    "b": {"fill_type": 0},
    "table_1_rows": {"fill_type": 0},
    "project": {"fill_type": 0},
    "t5_h": {"fill_type": 0},
    "r": {"fill_type": 0},
    "sample_preparation_2": {"fill_type": 0},
    "sample_preparation_1": {"fill_type": 0},
    "known_sample_sub_table": {"fill_type": 0},
    "t1_h": {"fill_type": 0},
    "storage_condition": {"fill_type": 0},
    "calculation_formula": {"fill_type": 0},
    "t6_h": {"fill_type": 0},
    "t3_h": {"fill_type": 0},
    "sample_status": {"fill_type": 0},
    "regression_equation": {"fill_type": 0},
    "t2_h": {"fill_type": 0},
    "detection_time": {"fill_type": 0},
    "rh": {"fill_type": 0},
    "detection_basis": {"fill_type": 0},
    "standard_solution_number": {"fill_type": 0},
    "a": {"fill_type": 0},
    "instrument_name": {"fill_type": 0},
    "t": {"fill_type": 0}
}

# 标题映射（包含字体和字号信息）
title_mapping = {
    'instrument_name_t': {'name': '仪器名称', 'font': '宋体', 'font_size': 12},
    'regression_equation_t': {'name': '回归方程', 'font': '宋体', 'font_size': 12},
    'trh_t': {'name': '环境条件', 'font': '宋体', 'font_size': 12},
    'detection_time_t': {'name': '分析日期', 'font': '宋体', 'font_size': 12},
    'remark_t': {'name': '备注', 'font': '宋体', 'font_size': 12},
    'sample_status_t': {'name': '样品状态', 'font': '宋体', 'font_size': 12},
    'sample_preparation_t': {'name': '样品前处理', 'font': '宋体', 'font_size': 12},
    'calculation_formula_t': {'name': '计算公式', 'font': '宋体', 'font_size': 12},
    'project_t': {'name': '检测项目', 'font': '宋体', 'font_size': 12},
    'detection_basis_t': {'name': '检测依据', 'font': '宋体', 'font_size': 12},
    'instrument_num_t': {'name': '仪器编号', 'font': '宋体', 'font_size': 12},
    'solution_concentration_t': {'name': '溶液浓度()', 'font': '宋体', 'font_size': 12},
    'standard_solution_number_t': {'name': '标准溶液及编号', 'font': '宋体', 'font_size': 12},
    'storage_condition_t': {'name': '存放条件', 'font': '宋体', 'font_size': 12}
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
        't3_h': '稀释倍数',
        't4_h': '空白吸光度A0',
        't5_h': '水样吸光度A',
        't6_h': '校正吸光度A-A0',
        't7_h': '样品中挥发酚的质量m（   ）',
    }


    
    def __init__(self):
        # TABLE_NAME_MAP_REVERSE = {'表格': ['吸光值']}
        pass

# 模板字段定义
# fill_type: 0 表示从模板中提取的字段, fill_type: 1 表示表格截取的字段

# get_type: 0: 表示从通用数据中取, 1: 表示从接口中取 2: 表从数据库中取

from .common_data import BaseTableDataHandler, checkbox
python_template_var = {
    "扫描范围": {"fill_type": 0},
    "重复次数": {"fill_type": 0},
    "波长间隔": {"fill_type": 0},
    "光谱带宽": {"fill_type": 0},
    "show_gain": {"fill_type": 0},
    "备注": {"fill_type": 0},
    "方法名称": {"fill_type": 0},
    "show_energy_light": {"fill_type": 0},
    "光谱扫描图片": {"fill_type": 0},
    "仪器序号": {"fill_type": 0},
    "数据文件": {"fill_type": 0},
    "仪器型号": {"fill_type": 0},
    "能量灯": {"fill_type": 0},
    "table_data": {"fill_type": 0},
    "扫描速度": {"fill_type": 0},
    "is_repeat": {"fill_type": 0},
    "增益": {"fill_type": 0},
    "扫描间隔": {"fill_type": 0},
    "光度模式": {"fill_type": 0},
    "重复模式": {"fill_type": 0},
    "分析时间": {"fill_type": 0}
}

# 标题映射（包含字体和字号信息）
title_mapping = {
    '数据类型_t': {'name': '数据类型', 'font': '宋体', 'font_size': 12},
    '波长间隔_t': {'name': '波长间隔', 'font': '宋体', 'font_size': 12},
    '扫描间隔_t': {'name': '扫描间隔', 'font': '宋体', 'font_size': 12},
    '审核员_t': {'name': '审核员', 'font': '宋体', 'font_size': 12},
    '重复次数_t': {'name': '重复次数', 'font': '宋体', 'font_size': 12},
    '扫描范围_t': {'name': '扫描范围', 'font': '宋体', 'font_size': 12},
    '增益_t': {'name': '增益', 'font': '宋体', 'font_size': 12},
    '分析时间_t': {'name': '分析时间', 'font': '宋体', 'font_size': 12},
    '数据文件_t': {'name': '数据文件', 'font': '宋体', 'font_size': 12},
    '光度模式_t': {'name': '光度模式', 'font': '宋体', 'font_size': 12},
    '能量灯_t': {'name': '能量灯', 'font': '宋体', 'font_size': 12},
    '重复模式_t': {'name': '重复模式', 'font': '宋体', 'font_size': 12},
    '备注_t': {'name': '备注', 'font': '宋体', 'font_size': 12},
    '分析员_t': {'name': '分析员', 'font': '宋体', 'font_size': 12},
    '方法名称_t': {'name': '方法名称', 'font': '宋体', 'font_size': 12},
    '扫描速度_t': {'name': '扫描速度', 'font': '宋体', 'font_size': 12}
}

# 字段渲染表格
extra_info = {
    'remark': {'value': '', 'font_size': 12, 'font': '宋体'},  # 备注
    'header': {'value': '', 'font': '宋体', 'font_size': 10, 'position': 'left'},
    'footer': {'value': '', 'font': '宋体', 'font_size': 9, 'position': 'left'},
    'page_num': {'position': 'left', 'font': '宋体', 'font_size': 9},
    'title_list': [
        {'name': '报告名称', 'value': '光谱测量原始数据', 'font': '黑体', 'font_size': 15},
    ],
    'margin': {'value': '20'},
    # 横向/纵向：0=纵向（portrait）| 1=横向（landscape）
    'orientation': {'value': 0},
    # 行边距（line-height 倍数）
    'line_height': {'value': '1.5'},
}

table_fields = []

# 模板字段定义
# fill_type: 0 表示从模板中提取的字段, fill_type: 1 表示表格截取的字段

# get_type: 0: 表示从通用数据中取, 1: 表示从接口中取 2: 表从数据库中取

from .common_data import BaseTableDataHandler, checkbox
python_template_var = {
    "方程次数": {"fill_type": 0},
    "knows_table_data": {"fill_type": 0},
    "切换样品池": {"fill_type": 0},
    "测量波长": {"fill_type": 0},
    "数据文件": {"fill_type": 0},
    "分析时间": {"fill_type": 0},
    "曲线方程": {"fill_type": 0},
    "k_values": {"fill_type": 0},
    "零点插入": {"fill_type": 0},
    "r2": {"fill_type": 0},
    "重复测量": {"fill_type": 0},
    "r": {"fill_type": 0},
    "unknown_table_data": {"fill_type": 0},
    "强制过零点": {"fill_type": 0},
    "方法名称": {"fill_type": 0},
    "公式": {"fill_type": 0}
}

# 标题映射（包含字体和字号信息）
title_mapping = {
    '曲线方程_t': {'name': '曲线方程', 'font': '宋体', 'font_size': 12},
    '数据文件_t': {'name': '数据文件', 'font': '宋体', 'font_size': 12},
    '测量波长_t': {'name': '测量波长', 'font': '宋体', 'font_size': 12},
    # 'R_t': {'name': 'R', 'font': '宋体', 'font_size': 12},
    '零点插入_t': {'name': '零点插入', 'font': '宋体', 'font_size': 12},
    '自动切换样品池_t': {'name': '自动切换样品池', 'font': '宋体', 'font_size': 12},
    '分析时间_t': {'name': '分析时间', 'font': '宋体', 'font_size': 12},
    '方程次数_t': {'name': '方程次数', 'font': '宋体', 'font_size': 12},
    '校正方法_t': {'name': '校正方法', 'font': '宋体', 'font_size': 12},
    '强制过零点_t': {'name': '强制过零点', 'font': '宋体', 'font_size': 12},
    '数据类型_t': {'name': '数据类型', 'font': '宋体', 'font_size': 12},
    '重复测量_t': {'name': '重复测量', 'font': '宋体', 'font_size': 12},
    '公式_t': {'name': '公式', 'font': '宋体', 'font_size': 12},
    '方法名称_t': {'name': '方法名称', 'font': '宋体', 'font_size': 12}
}

# 字段渲染表格
extra_info = {
    'remark': {'value': '', 'font_size': 12, 'font': '宋体'},  # 备注
    'page_num_type': 0
}

table_fields = []

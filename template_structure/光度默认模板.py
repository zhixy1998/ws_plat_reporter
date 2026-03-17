# 模板字段定义
# fill_type: 0 表示从模板中提取的字段, fill_type: 1 表示表格截取的字段

# get_type: 0: 表示从通用数据中取, 1: 表示从接口中取 2: 表从数据库中取

from .common_data import BaseTableDataHandler, checkbox
python_template_var = {
    "仪器型号": {"fill_type": 0},
    "数据文件": {"fill_type": 0},
    "方法名称": {"fill_type": 0},
    "table_data": {"fill_type": 0},
    "仪器序号": {"fill_type": 0},
    "分析时间": {"fill_type": 0},
    "光谱带宽": {"fill_type": 0},
    "注释": {"fill_type": 0}
}

# 标题映射（包含字体和字号信息）
title_mapping = {
    '方法名称_t': {'name': '方法名称', 'font': '宋体', 'font_size': 12},
    '分析时间_t': {'name': '分析时间', 'font': '宋体', 'font_size': 12},
    '仪器型号_t': {'name': '仪器型号', 'font': '宋体', 'font_size': 12},
    '数据文件_t': {'name': '数据文件', 'font': '宋体', 'font_size': 12},
    '光谱带宽_t': {'name': '光谱带宽', 'font': '宋体', 'font_size': 12},
    '数据类型_t': {'name': '数据类型', 'font': '宋体', 'font_size': 12},
    '仪器序号_t': {'name': '仪器序号', 'font': '宋体', 'font_size': 12}
}

# 字段渲染表格
extra_info = {
    'remark': {'value': '', 'font_size': 12, 'font': '宋体'},  # 备注
    'page_num_type': 0
}

table_fields = []

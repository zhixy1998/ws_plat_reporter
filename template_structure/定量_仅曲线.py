# 模板字段定义
# fill_type: 0 表示从模板中提取的字段, fill_type: 1 表示表格截取的字段

# get_type: 0: 表示从通用数据中取, 1: 表示从接口中取 2: 表从数据库中取

from .common_data import BaseTableDataHandler, checkbox
python_template_var = {
    "定量分析图片": {"fill_type": 0}
}

# 标题映射（包含字体和字号信息）
title_mapping = {
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

table_fields = []

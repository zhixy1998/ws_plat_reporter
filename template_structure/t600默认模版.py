# 模板字段定义
# fill_type: 0 表示从模板中提取的字段, fill_type: 1 表示表格截取的字段

# get_type: 0: 表示从通用数据中取, 1: 表示从接口中取 2: 表从数据库中取

from .common_data import BaseTableDataHandler, checkbox
python_template_var = {
    "检验软件版本号": {"fill_type": 0},
    "UV_v": {"fill_type": 0},
    "产品编号": {"fill_type": 0},
    "sl": {"fill_type": 0},
    "wt": {"fill_type": 0},
    "sb": {"fill_type": 0},
    "ds": {"fill_type": 0},
    "复核员": {"fill_type": 0},
    "bs": {"fill_type": 0},
    "bdn": {"fill_type": 0},
    "logo_image": {"fill_type": 0},
    "cc": {"fill_type": 0},
    "检验结果": {"fill_type": 0},
    "相对湿度": {"fill_type": 0},
    "insp_date": {"fill_type": 0},
    "pg": {"fill_type": 0},
    "result": {"fill_type": 0},
    "产品型号": {"fill_type": 0},
    "n": {"fill_type": 0},
    "ir": {"fill_type": 0},
    "as": {"fill_type": 0},
    "d": {"fill_type": 0},
    "av": {"fill_type": 0},
    "remark": {"fill_type": 0},
    "tt": {"fill_type": 0},
    "UVTouch_v": {"fill_type": 0},
    "检验员": {"fill_type": 0},
    "temp": {"fill_type": 0},
    "wen": {"fill_type": 0}
}

# 标题映射（包含字体和字号信息）
title_mapping = {
}

# 字段渲染表格
extra_info = {
    'remark': {'value': '', 'font_size': 12, 'font': '宋体'},  # 备注
    'page_num_type': 0
}

table_fields = []

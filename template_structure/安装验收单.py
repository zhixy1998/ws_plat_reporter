# 模板字段定义
# fill_type: 0 表示从模板中提取的字段, fill_type: 1 表示表格截取的字段

# get_type: 0: 表示从通用数据中取, 1: 表示从接口中取 2: 表从数据库中取

from .common_data import BaseTableDataHandler, checkbox
python_template_var = {
    "wl_rep_standard": {"fill_type": 0},
    "stab_value": {"fill_type": 0},
    "sub_table": {"fill_type": 0},
    "noise_value": {"fill_type": 0},
    "stray_lt_standard": {"fill_type": 0},
    "bsl_stab_standard": {"fill_type": 0},
    "photo_acc_standard": {"fill_type": 0},
    "stray_lt_value": {"fill_type": 0},
    "photo_acc_value": {"fill_type": 0},
    "wavelength_mpe_standard": {"fill_type": 0},
    "noise_standard": {"fill_type": 0},
    "bsl_stab_value": {"fill_type": 0},
    "stab_standard": {"fill_type": 0}
}

# 标题映射（包含字体和字号信息）
title_mapping = {
}

# 字段渲染表格
extra_info = {
    'remark': {'value': '', 'font_size': 12, 'font': '宋体'},  # 备注
    'page_num_type': 0
}


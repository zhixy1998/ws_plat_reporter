# 模板字段定义
# fill_type: 0 表示从模板中提取的字段, fill_type: 1 表示表格截取的字段

# get_type: 0: 表示从通用数据中取, 1: 表示从接口中取 2: 表从数据库中取

python_template_var = {
    "r2": {"fill_type": 0},
    "knows_table_data": {"fill_type": 0},
    "分析时间": {"fill_type": 0},
    "曲线方程": {"fill_type": 0},
    "k_values": {"fill_type": 0},
    "强制过零点": {"fill_type": 0},
    "测量波长": {"fill_type": 0},
    "切换样品池": {"fill_type": 0},
    "零点插入": {"fill_type": 0},
    "重复测量": {"fill_type": 0},
    "数据文件": {"fill_type": 0},
    "定量分析图片": {"fill_type": 0},
    "公式": {"fill_type": 0},
    "方法名称": {"fill_type": 0},
    "unknown_table_data": {"fill_type": 0},
    "方程次数": {"fill_type": 0}
}

# 字段渲染表格
custom_bookmark = {
    'project_name':'项目名称',
    'note':'备注',
}

table_fields = []

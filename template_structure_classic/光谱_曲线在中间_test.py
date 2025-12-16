# 模板字段定义
# fill_type: 0 表示从模板中提取的字段, fill_type: 1 表示表格截取的字段

# get_type: 0: 表示从通用数据中取, 1: 表示从接口中取 2: 表从数据库中取

python_template_var = {
    "光谱扫描图片": {"fill_type": 0},
    "增益": {"fill_type": 0},
    "备注": {"fill_type": 0},
    "仪器型号": {"fill_type": 0},
    "分析时间": {"fill_type": 0},
    "能量灯": {"fill_type": 0},
    "数据文件": {"fill_type": 0},
    "扫描间隔": {"fill_type": 0},
    "扫描范围": {"fill_type": 0},
    "光谱带宽": {"fill_type": 0},
    "扫描速度": {"fill_type": 0},
    "方法名称": {"fill_type": 0},
    "spectral_table_subdoc": {"fill_type": 0},
    "光度模式": {"fill_type": 0},
    "仪器序号": {"fill_type": 0}
}

# 字段渲染表格
custom_bookmark = {
    'project_name':'项目名称',
    'note':'备注',
}

table_fields = []

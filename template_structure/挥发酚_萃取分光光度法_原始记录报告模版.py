# 模板字段定义
# fill_type: 0 表示从模板中提取的字段, fill_type: 1 表示表格截取的字段

# get_type: 0: 表示从通用数据中取, 1: 表示从接口中取 2: 表从数据库中取

from .common_data import BaseTableDataHandler

python_template_var = {
    "前处理1": {"fill_type": 0},
    "前处理2": {"fill_type": 0},
    "温度": {"fill_type": 0},
    "备注": {"fill_type": 0},
    "仪器编号": {"fill_type": 0},
    "计算公式": {"fill_type": 0},
    "溶液浓度": {"fill_type": 0},
    "湿度": {"fill_type": 0},
    "标准溶液及编号": {"fill_type": 0},
    "仪器名称": {"fill_type": 0},
    "检测日期": {"fill_type": 0},
    "检测项目": {"fill_type": 0},
    "检测依据": {"fill_type": 0}
}

# 字段渲染表格
custom_bookmark = {
    'project_name':'项目名称',
    'note':'备注',
}

table_fields = []

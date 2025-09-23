# 模板字段定义
# fill_type: 0 表示从模板中提取的字段, fill_type: 1 表示表格截取的字段

# get_type: 0: 表示从通用数据中取, 1: 表示从接口中取 2: 表从数据库中取

from .common_data import BaseTableDataHandler

python_template_var = {
    "仪器编号": {"fill_type": 0},
    "b": {"fill_type": 0},
    "回归方程": {"fill_type": 0},
    "计算公式": {"fill_type": 0},
    "样品前处理": {"fill_type": 0},
    "检测日期": {"fill_type": 0},
    "检测依据": {"fill_type": 0},
    "r": {"fill_type": 0},
    "温度": {"fill_type": 0},
    "仪器名称": {"fill_type": 0},
    "检测项目": {"fill_type": 0},
    "a": {"fill_type": 0},
    "溶液浓度": {"fill_type": 0},
    "湿度": {"fill_type": 0},
    "备注": {"fill_type": 0},
    "标准溶液及编号": {"fill_type": 0}
}

# 表格字段分组
table_jinja_values = {
    '氮含量': ['氮含量_0', '氮含量_1', '氮含量_2', '氮含量_3', '氮含量_4', '氮含量_5'],
    '校正吸光度': ['校正吸光度_0', '校正吸光度_1', '校正吸光度_2', '校正吸光度_3', '校正吸光度_4', '校正吸光度_5'],
    '吸光度': ['吸光度_0', '吸光度_1', '吸光度_2', '吸光度_3', '吸光度_4', '吸光度_5']
}

# 字段渲染表格
custom_bookmark = {
    'project_name':'项目名称',
    'note':'备注',
}

table_fields = [
    {
        "headers": [
            [
                "氮含量"
            ],
            [
                "吸光度"
            ],
            [
                "校正吸光度"
            ]
        ],
        "col_count": 3,
        "data_rows": [],
        "row_count": 0,
        "table_name": "表格1",
        "column_width": [
            2781,
            2781,
            2781
        ],
        "structure_type": 1
    }
]


class TableDataHandler(BaseTableDataHandler):
    """表格数据处理类，用于处理数据映射和处理逻辑"""
    
    # 简单字段映射：表头名称 -> 数据库字段名
    HEADER_M_MAPPING = {
        "氮含量": "V5",
        "吸光度": "V6",
        "校正吸光度": "V7"
    }
    TABLE_NAME_MAP = {
       '氮含量':'表格1',
       '吸光度':'表格1',
       "校正吸光度": "表格1"
    }

    TEMPLATE_INFO_MAP = {
        '表格1': {
            'tpl_type': 1,   # 1: 每个单元格一个tpl对象，就是横向表格那种 2: 通过docxtpl循环语法渲染
            'column_count': 6
        }
    }

    standard = ['氮含量', '吸光度', '校正吸光度']
    
    def __init__(self):
        # TABLE_NAME_MAP_REVERSE = {'表格1': ['校正吸光度', '标准溶液', '吸光度']}
        self.TABLE_NAME_MAP_REVERSE = {v: [k for k, v2 in self.TABLE_NAME_MAP.items() if v2 == v] for v in set(self.TABLE_NAME_MAP.values())}
    
    
    
    def handle_吸光度(self, data, context):
        """处理检测时间和对应的吸光度列"""
        return data.get('m2', '')
    
    def handle_校正吸光度(self, data, context):
        """处理检测时间和对应的吸光度列"""
        return data.get('m2', '')
    
    def handle_氮含量(self, data, context):
        """处理T(min)列"""
        return data.get('m3', '')
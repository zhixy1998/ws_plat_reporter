# 模板字段定义
# fill_type: 0 表示从模板中提取的字段, fill_type: 1 表示表格截取的字段

# get_type: 0: 表示从通用数据中取, 1: 表示从接口中取 2: 表从数据库中取

python_template_var = {
    "b": {"fill_type": 0},
    "r": {"fill_type": 0},
    "检测依据": {"fill_type": 0},
    "检测项目": {"fill_type": 0},
    "湿度": {"fill_type": 0},
    "仪器编号": {"fill_type": 0},
    "回归方程": {"fill_type": 0},
    "检测项目1": {"fill_type": 0},
    "溶液浓度": {"fill_type": 0},
    "a": {"fill_type": 0},
    "计算公式": {"fill_type": 0},
    "检测日期": {"fill_type": 0},
    "温度": {"fill_type": 0},
    "检测项目2": {"fill_type": 0},
    "备注": {"fill_type": 0},
    "标准溶液及编号": {"fill_type": 0},
    "仪器名称": {"fill_type": 0}
}

# 表格字段分组
table_jinja_values = {
    '校正吸光度': ['校正吸光度_0', '校正吸光度_1', '校正吸光度_2', '校正吸光度_3', '校正吸光度_4', '校正吸光度_5', '校正吸光度_6', '校正吸光度_7'],
    '吸光度': ['吸光度_0', '吸光度_1', '吸光度_2', '吸光度_3', '吸光度_4', '吸光度_5', '吸光度_6', '吸光度_7'],
    '挥发酚质量': ['挥发酚质量_0', '挥发酚质量_1', '挥发酚质量_2', '挥发酚质量_3', '挥发酚质量_4', '挥发酚质量_5', '挥发酚质量_6', '挥发酚质量_7']
}
table_fields = [
    {
        "headers": [
            [
                "挥发酚质量"
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
        "table_name": "表格",
        "column_width": [
            2781,
            2781,
            2781
        ],
        "structure_type": 1
    }
]


class TableDataHandler:
    """表格数据处理类，用于处理数据映射和处理逻辑"""
    
    # 简单字段映射：表头名称 -> 数据库字段名
    HEADER_M_MAPPING = {
        "吸光度": "A1",  # 序号列
        "挥发酚质量": "A1",  # 序号列
        "校正吸光度": "V8",
    }
    TABLE_NAME_MAP = {
        "吸光度":'表格',  # 序号列
        "挥发酚质量": '表格',
        "校正吸光度": "表格",
    }

    TEMPLATE_INFO_MAP = {
        '表格': {
            'tpl_type': 1,   # 1: 每个单元格一个tpl对象，就是横向表格那种 2: 通过docxtpl循环语法渲染
            'column_count': 8
        }
    }
    
    def __init__(self):
        self.TABLE_NAME_MAP_REVERSE = {v: [k for k, v2 in self.TABLE_NAME_MAP.items() if v2 == v] for v in set(self.TABLE_NAME_MAP.values())}
    
    def handle_吸光度(self, data, context, row_index=0):
        return str(row_index + 1)
    def handle_挥发酚质量(self, data, context, row_index=0):
        return str(row_index + 1)
    def handle_校正吸光度(self, data, context):
        return data.get('m2', '')
    
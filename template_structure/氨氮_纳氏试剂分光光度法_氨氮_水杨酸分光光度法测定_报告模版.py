# 模板字段定义
# fill_type: 0 表示从模板中提取的字段, fill_type: 1 表示表格截取的字段

# get_type: 0: 表示从通用数据中取, 1: 表示从接口中取 2: 表从数据库中取

python_template_var = {
    "标准溶液及编号": {"fill_type": 0},
    "备注": {"fill_type": 0},
    "检测项目": {"fill_type": 0},
    "仪器编号": {"fill_type": 0},
    "a": {"fill_type": 0},
    "温度": {"fill_type": 0},
    "仪器名称": {"fill_type": 0},
    "b": {"fill_type": 0},
    # "前处理": {"fill_type": 0},
    "步骤": {"fill_type": 0},
    "公式参数": {"fill_type": 0},
    "检测依据": {"fill_type": 0},
    "检测日期": {"fill_type": 0},
    "回归方程": {"fill_type": 0},
    "计算公式": {"fill_type": 0},
    "湿度": {"fill_type": 0},
    "r": {"fill_type": 0},
    "溶液浓度": {"fill_type": 0}
}

# 表格字段分组
table_jinja_values = {
    '校正吸光度': ['校正吸光度_0', '校正吸光度_1', '校正吸光度_2', '校正吸光度_3', '校正吸光度_4', '校正吸光度_5', '校正吸光度_6', '校正吸光度_7'],
    '氨氮含量': ['氨氮含量_0', '氨氮含量_1', '氨氮含量_2', '氨氮含量_3', '氨氮含量_4', '氨氮含量_5', '氨氮含量_6', '氨氮含量_7'],
    '吸光度': ['吸光度_0', '吸光度_1', '吸光度_2', '吸光度_3', '吸光度_4', '吸光度_5', '吸光度_6', '吸光度_7']
}
table_fields = [
    {
        "headers": [
            [
                "氨氮含量"
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
        "table_name": "小表格",
        "column_width": [
            1922,
            1922,
            1922
        ],
        "structure_type": 1
    }
]



class TableDataHandler:
    """表格数据处理类，用于处理数据映射和处理逻辑"""
    
    # 简单字段映射：表头名称 -> 数据库字段名
    HEADER_M_MAPPING = {
        "氨氮含量": "A1",  # 序号列
        "吸光度": "V8",
        "校正吸光度": "V6"
    }
    TABLE_NAME_MAP = {
       '氨氮含量':'小表格',
       '吸光度':'小表格',
       '校正吸光度':'小表格'
    }

    TEMPLATE_INFO_MAP = {
        '小表格': {
            'tpl_type': 1,   # 1: 每个单元格一个tpl对象，就是横向表格那种 2: 通过docxtpl循环语法渲染
            'column_count': 7
        }
    }

    standard = ['氨氮含量', '吸光度', '校正吸光度']
    
    def __init__(self):
        # TABLE_NAME_MAP_REVERSE = {'小表格': ['氨氮含量', '吸光度', '校正吸光度']}
        self.TABLE_NAME_MAP_REVERSE = {v: [k for k, v2 in self.TABLE_NAME_MAP.items() if v2 == v] for v in set(self.TABLE_NAME_MAP.values())}
    
    def handle_氨氮含量(self, data):
        """处理序号列的逻辑"""
        return
    
    def handle_吸光度(self, data):
        """处理检测时间和对应的吸光值列"""
        return
    
    def handle_校正吸光度(self, data):
        """处理T(min)列"""
        return



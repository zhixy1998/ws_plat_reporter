# 模板字段定义
# fill_type: 0 表示从模板中提取的字段, fill_type: 1 表示表格截取的字段

# get_type: 0: 表示从通用数据中取, 1: 表示从接口中取 2: 表从数据库中取

from .common_data import BaseTableDataHandler

python_template_var = {
    "计算公式": {"fill_type": 0},
    "温度": {"fill_type": 0},
    "溶液浓度": {"fill_type": 0},
    "仪器名称": {"fill_type": 0},
    "湿度": {"fill_type": 0},
    "a": {"fill_type": 0},
    "检测日期": {"fill_type": 0},
    "仪器编号": {"fill_type": 0},
    "前处理": {"fill_type": 0},
    "检测依据": {"fill_type": 0},
    "r": {"fill_type": 0},
    "备注": {"fill_type": 0},
    "检测项目": {"fill_type": 0},
    "标准溶液及编号": {"fill_type": 0},
    "回归方程": {"fill_type": 0},
    "b": {"fill_type": 0}
}

# 表格字段分组
table_jinja_values = {
    '总氮含量': ['总氮含量_0', '总氮含量_1', '总氮含量_2', '总氮含量_3', '总氮含量_4', '总氮含量_5'],
    '吸光度2': ['吸光度2_0', '吸光度2_1', '吸光度2_2', '吸光度2_3', '吸光度2_4', '吸光度2_5'],
    '吸光度12': ['吸光度12_0', '吸光度12_1', '吸光度12_2', '吸光度12_3', '吸光度12_4', '吸光度12_5'],
    '吸光度11': ['吸光度11_0', '吸光度11_1', '吸光度11_2', '吸光度11_3', '吸光度11_4', '吸光度11_5']
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
                "总氮含量"
            ],
            [
                "吸光度11"
            ],
            [
                "吸光度2"
            ],
            [
                "校正吸光度"
            ]
        ],
        "col_count": 4,
        "data_rows": [],
        "row_count": 0,
        "table_name": "表格",
        "column_width": [
            2781,
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
        "总氮含量": "V5",  # 序号列
        "吸光度1": "V6",
        "吸光度2": "V5",  # 序号列
        "校正吸光度": "V5",  # 序号列
    }

    TABLE_NAME_MAP = {
        '总氮含量': '表格',
        '吸光度1': '表格',
        '吸光度2': '表格',
        '校正吸光度': '表格',
    }

    TEMPLATE_INFO_MAP = {
            '表格': {
             'tpl_type': 1,   # 1: 每个单元格一个tpl对象，就是横向表格那种 2: 通过docxtpl循环语法渲染
             'column_count': 4
            },
        }

    
    def __init__(self):
        # TABLE_NAME_MAP_REVERSE = {'数据表格': ['吸光度2', '水样体积', '由标准曲线查得甲醛的质量', '水样吸光度1', '水样中甲醛质量浓度', '水样氨氮质量浓度', '平均值']}
        self.TABLE_NAME_MAP_REVERSE = {v: [k for k, v2 in self.TABLE_NAME_MAP.items() if v2 == v] for v in set(self.TABLE_NAME_MAP.values())}
    
    def handle_总氮含量(self, data, context):
        return 
    
    def handle_吸光度1(self, data, context):
        return 
    
    def handle_吸光度2(self, data, context, row_index=0):
        return
    
    def handle_校正吸光度(self, data, context, row_index=0):
        return
    

# 模板字段定义
# fill_type: 0 表示从模板中提取的字段, fill_type: 1 表示表格截取的字段

# get_type: 0: 表示从通用数据中取, 1: 表示从接口中取 2: 表从数据库中取

from .common_data import BaseTableDataHandler

python_template_var = {
    "r": {"fill_type": 0},
    "前处理": {"fill_type": 0},
    "回归方程": {"fill_type": 0},
    "仪器名称": {"fill_type": 0},
    "标准溶液及编号": {"fill_type": 0},
    "温度": {"fill_type": 0},
    "仪器编号": {"fill_type": 0},
    "检测项目": {"fill_type": 0},
    "溶液浓度": {"fill_type": 0},
    "a": {"fill_type": 0},
    "计算公式": {"fill_type": 0},
    "分析日期": {"fill_type": 0},
    "湿度": {"fill_type": 0},
    "备注": {"fill_type": 0},
    "检测依据": {"fill_type": 0},
    "b": {"fill_type": 0}
}

# 表格字段分组
table_jinja_values = {
    '油浓度': ['油浓度_0', '油浓度_1', '油浓度_2', '油浓度_3', '油浓度_4', '油浓度_5'],
    '吸光值': ['吸光值_0', '吸光值_1', '吸光值_2', '吸光值_3', '吸光值_4', '吸光值_5']
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
                "油浓度"
            ],
            [
                "吸光值"
            ]
        ],
        "col_count": 2,
        "data_rows": [],
        "row_count": 0,
        "table_name": "表格",
        "column_width": [
            3915,
            3915
        ],
        "structure_type": 1
    }
]

class TableDataHandler(BaseTableDataHandler):
    """表格数据处理类，用于处理数据映射和处理逻辑"""
    
    # 简单字段映射：表头名称 -> 数据库字段名
    HEADER_M_MAPPING = {
        "油浓度": "A1",
        "吸光值": "A2"
    }
    TABLE_NAME_MAP = {
       '油浓度':'表格',
       '吸光值':'表格'
    }

    TEMPLATE_INFO_MAP = {
        '表格': {
            'tpl_type': 1,   # 1: 每个单元格一个tpl对象，就是横向表格那种 2: 通过docxtpl循环语法渲染
            'column_count': 6
        }
    }

    standard = ['油浓度', '吸光值']
    
    def __init__(self):
        # TABLE_NAME_MAP_REVERSE = {'小表格': ['吸光值', '油浓度']}
        self.TABLE_NAME_MAP_REVERSE = {v: [k for k, v2 in self.TABLE_NAME_MAP.items() if v2 == v] for v in set(self.TABLE_NAME_MAP.values())}
    
    
    
    def handle_吸光值(self, data, context):
        """处理吸光值列"""
        return data.get('m2', '')
    
    def handle_油浓度(self, data, context):
        """处理油浓度列"""
        return data.get('m3', '')

# 模板字段定义
# fill_type: 0 表示从模板中提取的字段, fill_type: 1 表示表格截取的字段

# get_type: 0: 表示从通用数据中取, 1: 表示从接口中取 2: 表从数据库中取

from .common_data import BaseTableDataHandler

python_template_var = {
    "a": {"fill_type": 0},
    "r": {"fill_type": 0},
    "表格2_rows": {"fill_type": 0},
    "b": {"fill_type": 0},
    "备注": {"fill_type": 0},
    "回归方程": {"fill_type": 0}
}

# 表格字段分组
table_jinja_values = {
    '酚含量': ['酚含量_0', '酚含量_1', '酚含量_2', '酚含量_3', '酚含量_4', '酚含量_5', '酚含量_6', '酚含量_7'],
    '校正吸光值': ['校正吸光值_0', '校正吸光值_1', '校正吸光值_2', '校正吸光值_3', '校正吸光值_4', '校正吸光值_5', '校正吸光值_6', '校正吸光值_7'],
    '吸光值': ['吸光值_0', '吸光值_1', '吸光值_2', '吸光值_3', '吸光值_4', '吸光值_5', '吸光值_6', '吸光值_7']
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
                "酚含量"
            ],
            [
                "吸光值"
            ],
            [
                "校正吸光值"
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
    },
    {
        "has_tr": 1,
        "headers": [
            [
                "样品编号",
                "试样体积",
                "空白试验吸光值",
                "试样吸光度值",
                "查曲线得酚含量",
                "试样中挥发酚的质量浓度",
                "平均值"
            ]
        ],
        "col_count": 7,
        "data_rows": [],
        "row_count": 0,
        "table_name": "表格2",
        "column_width": [
            2781,
            1816,
            1900,
            1900,
            2037,
            2487,
            2535
        ],
        "structure_type": 0
    }
]


class TableDataHandler(BaseTableDataHandler):
    """表格数据处理类，用于处理数据映射和处理逻辑"""
    
    # 简单字段映射：表头名称 -> 数据库字段名
    HEADER_M_MAPPING = {
        "酚含量": "V5",  # 序号列
        "吸光值": "V8",
        "校正吸光值": "V6",
        "样品编号": "V5",
        "试样体积": "V6",
        "查曲线得酚含量": "V7",
        "空白试验吸光值": "V8",
        "试样吸光度值": "V5",
        "试样中挥发酚的质量浓度": "V6",
        "平均值": "V7"
    }
    TABLE_NAME_MAP = {
       '酚含量':'表格1',
       '吸光值':'表格1',
       '校正吸光值':'表格1',
       '样品编号':'表格2',
       '试样体积':'表格2',
       '查曲线得酚含量':'表格2',
       '空白试验吸光值':'表格2',
       '试样吸光度值':'表格2',
       '试样中挥发酚的质量浓度':'表格2',
       '平均值':'表格2'
    }

    TEMPLATE_INFO_MAP = {
        '表格1': {
            'tpl_type': 1,   # 1: 每个单元格一个tpl对象，就是横向表格那种 2: 通过docxtpl循环语法渲染
            'column_count': 3
        },
        '表格2': {
            'tpl_type': 2,   # 1: 每个单元格一个tpl对象，就是横向表格那种 2: 通过docxtpl循环语法渲染
            'column_count': 7
        }
    }
    
    def __init__(self):
        # TABLE_NAME_MAP_REVERSE = {'小表格': ['酚含量', '吸光值', '校正吸光值']}
        self.TABLE_NAME_MAP_REVERSE = {v: [k for k, v2 in self.TABLE_NAME_MAP.items() if v2 == v] for v in set(self.TABLE_NAME_MAP.values())}
    
    def handle_酚含量(self, data, context, row_index=0):
        """处理序号列的逻辑"""
        return 
    
    def handle_吸光度(self, data, context):
        """处理检测时间和对应的吸光值列"""
        return 
    
    def handle_校正吸光度(self, data, context):
        """处理T(min)列"""
        return 
    
    def handle_样品编号(self, data, context):
        """处理T(min)列"""
        return 
    
    def handle_水样体积(self, data, context):
        """处理T(min)列"""
        return
    
    def handle_稀释倍数(self, data, context):
        """处理T(min)列"""
        return 
        
    def handle_空白试验吸光度(self, data, context):
        """处理T(min)列"""
        return
    
    def handle_水样吸光度(self, data, context):
        """处理T(min)列"""
        return
    
    def handle_水样中氨氮质量浓度(self, data, context):
        """处理T(min)列"""
        return
    
    def handle_平均值(self, data, context):
        """处理T(min)列"""
        return
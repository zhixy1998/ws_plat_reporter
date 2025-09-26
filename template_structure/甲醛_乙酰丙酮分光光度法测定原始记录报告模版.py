# 模板字段定义
# fill_type: 0 表示从模板中提取的字段, fill_type: 1 表示表格截取的字段

# get_type: 0: 表示从通用数据中取, 1: 表示从接口中取 2: 表从数据库中取
from .common_data import BaseTableDataHandler

python_template_var = {
    "温度": {"fill_type": 0},
    "溶液浓度": {"fill_type": 0},
    "表格_rows": {"fill_type": 0},
    "仪器名称": {"fill_type": 0},
    "回归方程": {"fill_type": 0},
    "检测依据": {"fill_type": 0},
    "前处理": {"fill_type": 0},
    "湿度": {"fill_type": 0},
    "检测日期": {"fill_type": 0},
    "r": {"fill_type": 0},
    "检测项目": {"fill_type": 0},
    "备注": {"fill_type": 0},
    "a": {"fill_type": 0},
    "计算公式": {"fill_type": 0},
    "标准溶液及编号": {"fill_type": 0},
    "b": {"fill_type": 0},
    "仪器编号": {"fill_type": 0}
}

# 表格字段分组
table_jinja_values = {
    '吸光度': ['吸光度_0', '吸光度_1', '吸光度_2', '吸光度_3', '吸光度_4', '吸光度_5'],
    '甲醛含量': ['甲醛含量_0', '甲醛含量_1', '甲醛含量_2', '甲醛含量_3', '甲醛含量_4', '甲醛含量_5'],
    '校正吸光度': ['校正吸光度_0', '校正吸光度_1', '校正吸光度_2', '校正吸光度_3', '校正吸光度_4', '校正吸光度_5']
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
                "甲醛含量"
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
                "水样体积",
                "空白吸光度",
                "水样吸光度",
                "从标准曲线上查得的甲醛量",
                "样品中甲醛质量浓度",
                "平均值"
            ]
        ],
        "col_count": 7,
        "data_rows": [],
        "row_count": 0,
        "table_name": "表格",
        "column_width": [
            2781,
            2112,
            2122,
            2102,
            2112,
            2112,
            2115
        ],
        "structure_type": 0
    }
]



class TableDataHandler(BaseTableDataHandler):
    """表格数据处理类，用于处理数据映射和处理逻辑"""
    
    # 简单字段映射：表头名称 -> 数据库字段名
    HEADER_M_MAPPING = {
        "甲醛含量": "normalConcentration",  # 序号列
        "吸光度": "Abs",
        "校正吸光度": "sumAbs",  # 序号列
        "样品编号": "sampleNumber",  # 序号列
        "水样体积": "2191OJP",
        "空白吸光度": "Abs",
        "水样吸光度": "Abs",
        "从标准曲线上查得的甲醛量": "2191OJP",
        "样品中甲醛质量浓度": "2191OJP",
        "平均值": "2191OJP",
    }

    TABLE_NAME_MAP = {
        '甲醛含量': '小表格',
        '吸光度': '小表格',
        '校正吸光度': '小表格',
        '样品编号': '表格',
        '水样体积': '表格',
        '空白吸光度': '表格',
        '水样吸光度': '表格',
        '从标准曲线上查得的甲醛量': '表格',
        '样品中甲醛质量浓度': '表格',
        '平均值': '表格'
    }

    TEMPLATE_INFO_MAP = {
            '小表格': {
             'tpl_type': 1,   # 1: 每个单元格一个tpl对象，就是横向表格那种 2: 通过docxtpl循环语法渲染
             'column_count': 3
            },
            '表格': {
             'tpl_type': 2,   # 1: 每个单元格一个tpl对象，就是横向表格那种 2: 通过docxtpl循环语法渲染
             'column_count': 7
            }
        }
    
    standard = ['甲醛含量', '吸光度', '校正吸光度']

    
    def __init__(self):
        # TABLE_NAME_MAP_REVERSE = {'表格': ['样品编号', '水样体积', '空白吸光度', '水样吸光度', '标准曲线上氨氮质量', '从标准曲线上查得的甲醛量', '平均值']}
        self.TABLE_NAME_MAP_REVERSE = {v: [k for k, v2 in self.TABLE_NAME_MAP.items() if v2 == v] for v in set(self.TABLE_NAME_MAP.values())}
    
    def handle_甲醛含量(self, data, m):
        real_header, sample_data = self.get_standard_head_and_data(data, m)
        return real_header, sample_data
    
    def handle_吸光度(self, data, m):
        real_header, sample_data = self.get_standard_head_and_data(data, m)
        return real_header, sample_data
    
    def handle_校正吸光度(self, data, m):
        """处理序号列的逻辑"""
        real_header, sample_data = self.get_standard_head_and_data(data, m)
        return real_header, sample_data
    
    def handle_样品编号(self, data, context, row_index=0):
        """处理序号列的逻辑"""
        return
    
    def handle_空白试验吸光度(self, data, context):
        """处理空白试验吸光度"""
        return
    
    def handle_水样体积(self, data, context):
        """处理检测时间和对应的吸光值列"""
        return
    
    def handle_稀释倍数(self, data, context):
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
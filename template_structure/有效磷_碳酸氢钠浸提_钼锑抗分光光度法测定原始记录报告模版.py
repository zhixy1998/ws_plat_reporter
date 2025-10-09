# 模板字段定义
# fill_type: 0 表示从模板中提取的字段, fill_type: 1 表示表格截取的字段

# get_type: 0: 表示从通用数据中取, 1: 表示从接口中取 2: 表从数据库中取

from .common_data import BaseTableDataHandler, checkbox
python_template_var = {
    "回归方程": {"fill_type": 0},
    "未知样表格2_rows": {"fill_type": 0},
    "分析日期": {"fill_type": 0},
    "仪器名称": {"fill_type": 0},
    "检测依据": {"fill_type": 0},
    "湿度": {"fill_type": 0},
    "溶液浓度": {"fill_type": 0},
    "温度": {"fill_type": 0},
    "未知样表格_rows": {"fill_type": 0},
    "计算公式": {"fill_type": 0},
    "样品前处理": {"fill_type": 0},
    "b": {"fill_type": 0},
    "备注": {"fill_type": 0},
    "标准溶液及编号": {"fill_type": 0},
    "a": {"fill_type": 0},
    "检测项目": {"fill_type": 0},
    "r": {"fill_type": 0},
    "仪器编号": {"fill_type": 0}
}

# 表格字段分组
table_jinja_values = {
    '校正吸光值': ['校正吸光值_0', '校正吸光值_1', '校正吸光值_2', '校正吸光值_3', '校正吸光值_4', '校正吸光值_5', '校正吸光值_6'],
    '磷浓度': ['磷浓度_0', '磷浓度_1', '磷浓度_2', '磷浓度_3', '磷浓度_4', '磷浓度_5', '磷浓度_6'],
    '吸光值': ['吸光值_0', '吸光值_1', '吸光值_2', '吸光值_3', '吸光值_4', '吸光值_5', '吸光值_6']
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
                "磷浓度"
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
        "table_name": "已知样表格",
        "column_width": [
            1999,
            1999,
            1999
        ],
        "structure_type": 1
    },
    {
        "has_tr": 1,
        "headers": [
            [
                "样品编号"
            ],
            [
                "取样量"
            ],
            [
                "稀释倍数"
            ],
            [
                "试料体积"
            ],
            [
                "吸取试料体积"
            ],
            [
                "土壤的干物质含量"
            ],
            [
                "土壤中有效磷含量"
            ],
            [
                "平均值"
            ],
            [
                "空白吸光度"
            ],
            [
                "样品吸光度"
            ],
            [
                "对比吸光度"
            ]
        ],
        "col_count": 11,
        "data_rows": [],
        "row_count": 0,
        "table_name": "未知样表格",
        "column_width": [
            1999,
            1559,
            1255,
            1188,
            1506,
            1681,
            1631,
            1509,
            999,
            985,
            1136
        ],
        "structure_type": 1
    },
    {
        "has_tr": 1,
        "headers": [
            [
                "样品编号",
                "取样量",
                "稀释倍数",
                "试料体积",
                "吸取试料体积",
                "土壤的干物质含量",
                "土壤中有效磷含量",
                "平均值",
                "空白吸光度",
                "样品吸光度",
                "对比吸光度"
            ]
        ],
        "col_count": 11,
        "data_rows": [],
        "row_count": 0,
        "table_name": "未知样表格2",
        "column_width": [
            1861,
            1559,
            1418,
            1457,
            1364,
            1600,
            1631,
            1632,
            900,
            1038,
            996
        ],
        "structure_type": 0
    }
]

class TableDataHandler(BaseTableDataHandler):
    """表格数据处理类，用于处理数据映射和处理逻辑"""
    
    # 简单字段映射：表头名称 -> 数据库字段名
    HEADER_M_MAPPING = {
        "磷浓度": "Abs",
        "吸光值": "Abs",
        "校正吸光值": "Abs",

        "样品编号": "V5",  # 序号列
        "取样量": "V5",
        "稀释倍数": "V5",
        "吸取试料体积": 'V5',
        "试料体积": 'V5',
        '空白吸光度': 'V5',
        '样品吸光度': 'V5',
        '对比吸光度': 'V5',
        '土壤中有效磷含量': 'V5' ,  
        '土壤的干物质含量': 'V5' ,  
        '平均值': 'V5' ,
    }

    TABLE_NAME_MAP_REVERSE = {
        '已知样表格': ['磷浓度', '吸光值', '校正吸光值'],
        '未知样表格': ['样品编号', '取样量', 
                '稀释倍数', '吸取试料体积', '试料体积','土壤的干物质含量',
                 '空白吸光度','样品吸光度','对比吸光度','土壤中有效磷含量','平均值'],
        '未知样表格2': ['样品编号', '取样量', 
                '稀释倍数', '吸取试料体积', '试料体积','土壤的干物质含量',
                 '空白吸光度','样品吸光度','对比吸光度','土壤中有效磷含量','平均值']
    }

    TEMPLATE_INFO_MAP = {
        '未知样表格': {
            'tpl_type': 2,   # 1: 每个单元格一个tpl对象，就是横向表格那种 2: 通过docxtpl循环语法渲染
            'column_count': None
        },
        '未知样表格2': {
            'tpl_type': 2,   # 1: 每个单元格一个tpl对象，就是横向表格那种 2: 通过docxtpl循环语法渲染
            'column_count': None
        },
        '已知样表格': {
            'tpl_type': 1,   # 1: 每个单元格一个tpl对象，就是横向表格那种 2: 通过docxtpl循环语法渲染
            'column_count': 6
        }
    }
    standard = ['磷浓度', '吸光值', '校正吸光值']
    unknown = ['样品编号', '取样量',  '稀释倍数', '吸取试料体积', '试料体积', 
            '空白吸光度','样品吸光度','对比吸光度', '土壤中有效磷含量', '平均值','土壤的干物质含量']
    
    def __init__(self):
        pass
    
    def handle_磷浓度(self, data, m):
        """处理序号列的逻辑"""
        real_header, sample_data = self.get_standard_head_and_data(data, m)
        return real_header, sample_data
    
    def handle_吸光值(self, data, m):
        """处理检测时间和对应的吸光值列"""
        real_header, sample_data = self.get_standard_head_and_data(data, m)
        return real_header, sample_data
    
    def handle_校正吸光值(self, data, m):
        """处理T(min)列"""
        real_header, sample_data = self.get_standard_head_and_data(data, m)
        return real_header, sample_data
       
    #未知样表格
    def handle_样品编号(self, data, context, row_index=0):
        return str(row_index + 1)
    
    def handle_取样量(self, data, context):
        return data.get('m2', '')
    
    def handle_稀释倍数(self, data, context):
        return data.get('m3', '')
    
    def handle_吸取试料体积(self, data, context):
        return data.get('m2', '')
    
    def handle_试料体积(self, data, context):
        return data.get('m3', '')
    
    def handle_空白吸光度(self, data, context):
        return data.get('m4', '')

    def handle_样品吸光度(self, data, context):
        return data.get('m4', '')
    
    def handle_对比吸光度(self, data, context):
        return data.get('m4', '')
    
    def handle_土壤中有效磷含量(self, data, context):
        return data.get('m5', '')
    
    def handle_土壤的干物质含量(self, data, context):
        return data.get('m6', '')
    
    def handle_平均值(self, data, context):
        return data.get('m5', '')
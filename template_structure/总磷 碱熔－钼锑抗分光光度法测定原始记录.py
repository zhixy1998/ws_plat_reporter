# 模板字段定义
# fill_type: 0 表示从模板中提取的字段, fill_type: 1 表示表格截取的字段

# get_type: 0: 表示从通用数据中取, 1: 表示从接口中取 2: 表从数据库中取

from .common_data import BaseTableDataHandler, checkbox
python_template_var = {
    "检测依据": {"fill_type": 0},
    "回归方程": {"fill_type": 0},
    "备注": {"fill_type": 0},
    "a": {"fill_type": 0},
    "标准溶液及编号": {"fill_type": 0},
    "b": {"fill_type": 0},
    "温度": {"fill_type": 0},
    "检测项目": {"fill_type": 0},
    "仪器编号": {"fill_type": 0},
    "样品前处理": {"fill_type": 0},
    "溶液浓度": {"fill_type": 0},
    "r": {"fill_type": 0},
    "湿度": {"fill_type": 0},
    "未知样表格_rows": {"fill_type": 0},
    "仪器名称": {"fill_type": 0},
    "计算公式": {"fill_type": 0},
    "分析日期": {"fill_type": 0}
}

# 表格字段分组
table_jinja_values = {
    '磷含量': ['磷含量_0', '磷含量_1', '磷含量_2', '磷含量_3', '磷含量_4', '磷含量_5'],
    '吸光度': ['吸光度_0', '吸光度_1', '吸光度_2', '吸光度_3', '吸光度_4', '吸光度_5'],
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
                "磷含量"
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
        "table_name": "已知样表格",
        "column_width": [
            3915,
            3915,
            3915
        ],
        "structure_type": 1
    },
    {
        "has_tr": 1,
        "headers": [
            [
                "样品编号",
                "取样量",
                "试样定容体积",
                "试料体积",
                "土壤的干物质含量",
                "土壤中总磷含量",
                "平均值",
                "空白吸光度",
                "样品吸光度",
                "对比吸光度"
            ]
        ],
        "col_count": 10,
        "data_rows": [],
        "row_count": 0,
        "table_name": "未知样表格",
        "column_width": [
            2781,
            1395,
            1395,
            1395,
            1395,
            1395,
            1400,
            1395,
            1395,
            1395
        ],
        "structure_type": 0
    }
]

class TableDataHandler(BaseTableDataHandler):
    """表格数据处理类，用于处理数据映射和处理逻辑"""
    
    # 简单字段映射：表头名称 -> 数据库字段名
    HEADER_M_MAPPING = {
        "磷含量": "Abs",
        "吸光度": "Abs",
        "校正吸光度": "Abs",

        "样品编号": "V7",  # 序号列
        "取样量": "V7",
        "试样定容体积": "V7",
        "试料体积": 'V7',
        "土壤的干物质含量": 'V7',
        '空白吸光度': 'V7',
        '样品吸光度': 'V7',
        '对比吸光度': 'V7',
        '土壤中总磷含量': 'V7' ,  
        '平均值': 'V7' ,
    }

    TABLE_NAME_MAP_REVERSE = {
        '已知样表格': ['磷含量', '吸光度', '校正吸光度'],
        '未知样表格': ['样品编号', '取样量', '试样定容体积', '试料体积', '土壤的干物质含量',
                 '空白吸光度','样品吸光度','对比吸光度','土壤中总磷含量','平均值']
    }

    TEMPLATE_INFO_MAP = {
        '未知样表格': {
            'tpl_type': 6,   # 1: 每个单元格一个tpl对象，就是横向表格那种 2: 通过docxtpl循环语法渲染
            'column_count': None
        },
        '已知样表格': {
            'tpl_type': 1,   # 1: 每个单元格一个tpl对象，就是横向表格那种 2: 通过docxtpl循环语法渲染
            'column_count': 10
        }
    }
    standard = ['磷含量', '吸光度', '校正吸光度']
    unknown = ['样品编号', '取样量',  '试样定容体积', '试料体积', '土壤的干物质含量', 
            '空白吸光度','样品吸光度','对比吸光度', '土壤中总磷含量', '平均值']
    
    def __init__(self):
        pass
    
    def handle_磷含量(self, data, m):
        """处理序号列的逻辑"""
        real_header, sample_data = self.get_standard_head_and_data(data, m)
        return real_header, sample_data
    
    def handle_吸光度(self, data, m):
        """处理检测时间和对应的吸光值列"""
        real_header, sample_data = self.get_standard_head_and_data(data, m)
        return real_header, sample_data
    
    def handle_校正吸光度(self, data, m):
        """处理T(min)列"""
        real_header, sample_data = self.get_standard_head_and_data(data, m)
        return real_header, sample_data
       
    #未知样表格
    def handle_样品编号(self, data, context, row_index=0):
        return str(row_index + 1)
    
    def handle_取样量(self, data, context):
        return data.get('m2', '')
    
    def handle_试样定容体积 (self, data, context):
        return data.get('m3', '')
    
    def handle_试料体积(self, data, context):
        return data.get('m2', '')
    
    def handle_土壤的干物质含量(self, data, context):
        return data.get('m3', '')
    
    def handle_空白吸光度(self, data, context):
        return data.get('m4', '')

    def handle_样品吸光度(self, data, context):
        return data.get('m4', '')
    
    def handle_对比吸光度(self, data, context):
        return data.get('m4', '')
    
    def handle_土壤中总磷含量(self, data, context):
        return data.get('m5', '')
    
    def handle_平均值(self, data, context):
        return data.get('m5', '')
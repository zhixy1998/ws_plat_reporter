# 模板字段定义
# fill_type: 0 表示从模板中提取的字段, fill_type: 1 表示表格截取的字段

# get_type: 0: 表示从通用数据中取, 1: 表示从接口中取 2: 表从数据库中取
from .common_data import BaseTableDataHandler
python_template_var = {
    "仪器编号": {"fill_type": 0},
    "计算公式": {"fill_type": 0},
    "温度": {"fill_type": 0},
    "样品前处理": {"fill_type": 0},
    "表格3_rows": {"fill_type": 0},
    "b": {"fill_type": 0},
    "检测依据": {"fill_type": 0},
    "溶液浓度": {"fill_type": 0},
    "湿度": {"fill_type": 0},
    "表格2_rows": {"fill_type": 0},
    "r": {"fill_type": 0},
    "a": {"fill_type": 0},
    "回归方程": {"fill_type": 0},
    "标准溶液及编号": {"fill_type": 0},
    "检测项目": {"fill_type": 0},
    "仪器名称": {"fill_type": 0},
    "备注": {"fill_type": 0},
    "检测日期": {"fill_type": 0}
}

# 表格字段分组
table_jinja_values = {
    '六价铬含量': ['六价铬含量_0', '六价铬含量_1', '六价铬含量_2', '六价铬含量_3', '六价铬含量_4', '六价铬含量_5', '六价铬含量_6', '六价铬含量_7', '六价铬含量_8'],
    '吸光度': ['吸光度_0', '吸光度_1', '吸光度_2', '吸光度_3', '吸光度_4', '吸光度_5', '吸光度_6', '吸光度_7', '吸光度_8'],
    '校正吸光度': ['校正吸光度_0', '校正吸光度_1', '校正吸光度_2', '校正吸光度_3', '校正吸光度_4', '校正吸光度_5', '校正吸光度_6', '校正吸光度_7', '校正吸光度_8']
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
                "六价铬含量"
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
            2711,
            2711,
            2711
        ],
        "structure_type": 1
    },
    {
        "has_tr": 1,
        "headers": [
            [
                "样品编号",
                "色度校正吸光度",
                "空白吸光度",
                "色度校正吸光度",
                "试样吸光度",
                "校正吸光度",
                "试样含量",
                "试样浓度",
                "平均浓度"
            ]
        ],
        "col_count": 9,
        "data_rows": [],
        "row_count": 0,
        "table_name": "表格2",
        "column_width": [
            2711,
            1843,
            1559,
            1560,
            1559,
            1559,
            1559,
            1524,
            1582
        ],
        "structure_type": 0
    }
]

class TableDataHandler(BaseTableDataHandler):
    """表格数据处理类，用于处理数据映射和处理逻辑"""
    
    # 简单字段映射：表头名称 -> 数据库字段名
    HEADER_M_MAPPING = {
        "六价铬含量": "normalConcentration",  # 序号列
        "吸光度": "Abs",
        "已知校正吸光度": "Abs",


        "样品编号": "V5",  # 序号列
        "平均浓度":"V6",
        "空白吸光度":"V7", 
        "色度校正吸光度":"V6", 
        "试样吸光度":"V8", 
        "校正吸光度":"V6", 
        "试样含量":"V6", 
        "试样浓度":"V6", 
    }

    TABLE_NAME_MAP_REVERSE = {
        '表格1': ['六价铬含量', '吸光度', "已知校正吸光度"],
        '表格2': ['样品编号', '色度校正吸光度', '空白吸光度', '试样吸光度', '校正吸光度', '试样含量', '平均浓度', '试样浓度'],
        '表格3':['样品编号', '色度校正吸光度', '空白吸光度', '试样吸光度', '校正吸光度', '试样含量', '平均浓度', '试样浓度']
    }


    TEMPLATE_INFO_MAP = {
            '表格1': {
             'tpl_type': 1,   # 1: 每个单元格一个tpl对象，就是横向表格那种 2: 通过docxtpl循环语法渲染
             'column_count': None
            },
            '表格2': {
             'tpl_type': 2,   # 1: 每个单元格一个tpl对象，就是横向表格那种 2: 通过docxtpl循环语法渲染
             'column_count': None
            },
            '表格3': {
             'tpl_type': 2,   # 1: 每个单元格一个tpl对象，就是横向表格那种 2: 通过docxtpl循环语法渲染
             'column_count': None
            },
        }
    
    standard = ['六价铬含量', '吸光度',"已知校正吸光度"]
    unknown = ['样品编号', '色度校正吸光度', '空白吸光度', '试样吸光度', '校正吸光度', '试样含量', '平均浓度', '试样浓度']

    def __init__(self):
        # TABLE_NAME_MAP_REVERSE = {'小表格': ['氨氮含量', '吸光度', '校正吸光度']}
        pass
    
    def handle_六价铬含量(self, data, m):
        """处理序号列的逻辑"""
        real_header, sample_data = self.get_standard_head_and_data(data, m)
        return real_header, sample_data
    
    def handle_吸光度(self, data, m):
        """处理检测时间和对应的吸光值列"""
        real_header, sample_data = self.get_standard_head_and_data(data, m)
        return real_header, sample_data
    
    def handle_已知校正吸光度(self, data, m):
        """处理已知校正吸光度"""
        real_header, sample_data = self.get_standard_head_and_data(data, m)
        return real_header, sample_data


    def handle_样品编号(self, data, context, row_index=0):
        """处理序号列的逻辑"""
        return str(row_index + 1)

    def handle_色度校正吸光度(self, data, context):
        """处理取色度校正吸光度"""
        return data.get('m2', '')
    
    def handle_空白吸光度(self, data, context):
        """处理空白吸光度列"""
        return data.get('m3', '')

    def handle_试样吸光度(self, data, context):
        """处理试样吸光度列"""
        return data.get('m4', '')
    
    def handle_校正吸光度(self, data, context):
        """校准曲线校正吸光度"""
        return data.get('m8', '')

    def handle_试样含量(self, data, context):
        """试样含量"""
        return data.get('m9', '')
    
    def handle_平均浓度(self, data, context):
        """平均浓度"""
        return data.get('m10', '')

    def handle_试样浓度(self, data, context):
        """试样浓度"""
        return data.get('m11', '')
    
# 模板字段定义
# fill_type: 0 表示从模板中提取的字段, fill_type: 1 表示表格截取的字段

# get_type: 0: 表示从通用数据中取, 1: 表示从接口中取 2: 表从数据库中取

from .common_data import BaseTableDataHandler, checkbox
python_template_var = {
    "检测项目": {"fill_type": 0},
    "检测依据": {"fill_type": 0},
    "未知样表格_rows": {"fill_type": 0},
    "r": {"fill_type": 0},
    "备注": {"fill_type": 0},
    "分析日期": {"fill_type": 0},
    "样品前处理": {"fill_type": 0},
    "湿度": {"fill_type": 0},
    "计算公式": {"fill_type": 0},
    "回归方程": {"fill_type": 0},
    "未知样表格1_rows": {"fill_type": 0},
    "a": {"fill_type": 0},
    "b": {"fill_type": 0},
    "溶液浓度": {"fill_type": 0},
    "标准溶液及编号": {"fill_type": 0},
    "仪器编号": {"fill_type": 0},
    "温度": {"fill_type": 0},
    "仪器名称": {"fill_type": 0}
}

# 表格字段分组
table_jinja_values = {
    '校正吸光度': ['校正吸光度_0', '校正吸光度_1', '校正吸光度_2', '校正吸光度_3', '校正吸光度_4', '校正吸光度_5'],
    '吸光值': ['吸光值_0', '吸光值_1', '吸光值_2', '吸光值_3', '吸光值_4', '吸光值_5'],
    '浓度': ['浓度_0', '浓度_1', '浓度_2', '浓度_3', '浓度_4', '浓度_5']
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
                "浓度"
            ],
            [
                "吸光值"
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
            2750,
            2750,
            2750
        ],
        "structure_type": 1
    },
    {
        "has_tr": 1,
        "headers": [
            [
                "样品编号",
                "阴离子洗涤剂浓度",
                "样品总体积",
                "平均值",
                "空白吸光值",
                "样品吸光值",
                "对比吸光值"
            ]
        ],
        "col_count": 7,
        "data_rows": [],
        "row_count": 0,
        "table_name": "未知样表格",
        "column_width": [
            3502,
            3502,
            2042,
            1816,
            2043,
            2044,
            2043
        ],
        "structure_type": 0
    },
    {
        "has_tr": 1,
        "headers": [
            [
                "样品编号",
                "样品总体积",
                "阴离子洗涤剂浓度",
                "平均值",
                "空白吸光值",
                "样品吸光值",
                "对比吸光值"
            ]
        ],
        "col_count": 7,
        "data_rows": [],
        "row_count": 0,
        "table_name": "未知样表格1",
        "column_width": [
            3502,
            2042,
            2043,
            1816,
            2043,
            2044,
            2043
        ],
        "structure_type": 0
    }
]

class TableDataHandler(BaseTableDataHandler):
    """表格数据处理类，用于处理数据映射和处理逻辑"""
    
    # 简单字段映射：表头名称 -> 数据库字段名
    HEADER_M_MAPPING = {
        "浓度": "Abs",
        "吸光值": "Abs",
        "校正吸光度": "Abs",

        "样品编号": "V7",  # 序号列
        "样品总体积": "V7",
        '空白吸光值': 'V7',
        '样品吸光值': 'V7',
        '对比吸光值': 'V7',
        '阴离子洗涤剂浓度': 'V7' ,  
        '平均值': 'V7' ,
    }

    TABLE_NAME_MAP_REVERSE = {
        '已知样表格': ['浓度', '吸光值', '校正吸光度'],
        '未知样表格': ['样品编号', '样品总体积', 
                 '空白吸光值','样品吸光值','对比吸光值',
                 '阴离子洗涤剂浓度','平均值'],
        '未知样表格1': ['样品编号', '样品总体积', 
                 '空白吸光值','样品吸光值','对比吸光值',
                 '阴离子洗涤剂浓度','平均值']
    }

    TEMPLATE_INFO_MAP = {
        '未知样表格': {
            'tpl_type': 2,   # 1: 每个单元格一个tpl对象，就是横向表格那种 2: 通过docxtpl循环语法渲染
            'column_count': None
        },
        '未知样表格1': {
            'tpl_type': 2,   # 1: 每个单元格一个tpl对象，就是横向表格那种 2: 通过docxtpl循环语法渲染
            'column_count': None
        },
        '已知样表格': {
            'tpl_type': 1,   # 1: 每个单元格一个tpl对象，就是横向表格那种 2: 通过docxtpl循环语法渲染
            'column_count': 6
        }
    }
    standard = ['浓度', '吸光值', '校正吸光度']
    unknown = ['样品编号', '样品总体积', 
            '空白吸光值','样品吸光值','对比吸光值', '阴离子洗涤剂浓度', '平均值']
    
    def __init__(self):
        pass
    
    def handle_浓度(self, data, m):
        """处理序号列的逻辑"""
        real_header, sample_data = self.get_standard_head_and_data(data, m)
        return real_header, sample_data
    
    def handle_吸光值(self, data, m):
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
    
    def handle_样品总体积(self, data, context):
        return data.get('m2', '')
    
    def handle_ (self, data, context):
        return data.get('m3', '')
    
    def handle_(self, data, context):
        return data.get('m2', '')
    
    def handle_(self, data, context):
        return data.get('m3', '')
    
    def handle_空白吸光值(self, data, context):
        return data.get('m4', '')

    def handle_样品吸光值(self, data, context):
        return data.get('m4', '')
    
    def handle_对比吸光值(self, data, context):
        return data.get('m4', '')
    
    def handle_阴离子洗涤剂浓度(self, data, context):
        return data.get('m5', '')
    
    def handle_平均值(self, data, context):
        return data.get('m5', '')
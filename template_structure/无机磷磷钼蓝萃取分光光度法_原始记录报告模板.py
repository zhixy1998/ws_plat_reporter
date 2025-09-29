# 模板字段定义
# fill_type: 0 表示从模板中提取的字段, fill_type: 1 表示表格截取的字段

# get_type: 0: 表示从通用数据中取, 1: 表示从接口中取 2: 表从数据库中取
from .common_data import BaseTableDataHandler

python_template_var = {
    "温度": {"fill_type": 0},
    "仪器名称": {"fill_type": 0},
    "r": {"fill_type": 0},
    "检测项目": {"fill_type": 0},
    "数据表格_rows": {"fill_type": 0},
    "溶液浓度": {"fill_type": 0},
    "a": {"fill_type": 0},
    "湿度": {"fill_type": 0},
    "备注": {"fill_type": 0},
    "检测依据": {"fill_type": 0},
    "分析日期": {"fill_type": 0},
    "仪器编号": {"fill_type": 0},
    "前处理": {"fill_type": 0},
    "回归方程": {"fill_type": 0},
    "标准溶液及编号": {"fill_type": 0},
    "计算公式": {"fill_type": 0},
    "b": {"fill_type": 0},
    "表格2_rows": {"fill_type": 0},
}

# 表格字段分组
table_jinja_values = {
    '磷酸盐浓度表格': ['磷酸盐浓度表格_0', '磷酸盐浓度表格_1', '磷酸盐浓度表格_2', '磷酸盐浓度表格_3', '磷酸盐浓度表格_4', '磷酸盐浓度表格_5'],
    '校正吸光值': ['校正吸光值_0', '校正吸光值_1', '校正吸光值_2', '校正吸光值_3', '校正吸光值_4', '校正吸光值_5'],
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
                "磷酸盐浓度表格"
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
        "table_name": "表格",
        "column_width": [
            3502,
            3502,
            3502
        ],
        "structure_type": 1
    },
    {
        "has_tr": 1,
        "headers": [
            [
                "样品编号",
                "样品总体积",
                "磷酸盐浓度",
                "平均值",
                "吸光值样品",
                "吸光值空白",
                "吸光值对比"
            ]
        ],
        "col_count": 7,
        "data_rows": [],
        "row_count": 0,
        "table_name": "表格2",
        "column_width": [
            2219,
            2219,
            2219,
            2219,
            2219,
            2219,
            2219
        ],
        "structure_type": 0
    },
    {
        "has_tr": 1,
        "headers": [
            [
                "样品编号",
                "样品总体积",
                "磷酸盐浓度",
                "平均值",
                "吸光值样品",
                "吸光值空白",
                "吸光值对比"
            ]
        ],
        "col_count": 7,
        "data_rows": [],
        "row_count": 0,
        "table_name": "数据表格",
        "column_width": [
            3436,
            2042,
            2043,
            2047,
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
        "磷酸盐浓度表格": "Abs",  # 序号列
        "吸光值": "Abs",
        "校正吸光值": "sumAbs",

        "样品编号": "sampleNumber",
        "样品总体积": "2191OJP",
        "磷酸盐浓度": "2191OJP",
        "平均值": "2191OJP",
        "吸光值样品": "Abs",
        "吸光值空白": "2191OJP",
        "吸光值对比": "Abs"
    }
    TABLE_NAME_MAP_REVERSE = {
        '表格': ['磷酸盐浓度表格', '吸光值', '校正吸光值'],
        '表格2': ['样品编号', '样品总体积', '磷酸盐浓度', '平均值', '吸光值样品', '吸光值空白', '吸光值对比'],
        '数据表格': ['样品编号', '样品总体积', '磷酸盐浓度', '平均值', '吸光值样品', '吸光值空白', '吸光值对比']
    }

    TEMPLATE_INFO_MAP = {
        '表格': {
            'tpl_type': 1,   # 1: 每个单元格一个tpl对象，就是横向表格那种 2: 通过docxtpl循环语法渲染
            'column_count': 3
        },
        '表格2': {
            'tpl_type': 2,   # 1: 每个单元格一个tpl对象，就是横向表格那种 2: 通过docxtpl循环语法渲染
            'column_count': 7
        },
        '数据表格': {
            'tpl_type': 2,   # 1: 每个单元格一个tpl对象，就是横向表格那种 2: 通过docxtpl循环语法渲染
            'column_count': 7
        }
    }

    standard = ['磷酸盐浓度表格', '吸光值', '校正吸光值']
    unknown = ['样品编号', '样品总体积', '磷酸盐浓度', '平均值', '吸光值样品', '吸光值空白', '吸光值对比']
    
    def __init__(self):
        # TABLE_NAME_MAP_REVERSE = {'小表格': ['氨氮含量', '吸光度', '校正吸光度']}
        pass
    
    def handle_磷酸盐浓度表格(self, data, m):
        """处理磷酸盐浓度表格列的逻辑"""

        real_header, sample_data = self.get_standard_head_and_data(data, m)
        return real_header, sample_data
    
    def handle_吸光值(self, data, m):
        """处理吸光值列"""
        real_header, sample_data = self.get_standard_head_and_data(data, m)
        return real_header, sample_data
    
    def handle_校正吸光值(self, data, m):
        """处理校正吸光值列"""
        real_header, sample_data = self.get_standard_head_and_data(data, m)
        return real_header, sample_data
    

    def handle_样品编号(self, data, context):
        """处理样品编号列"""
        return 
    
    def handle_样品总体积(self, data, context):
        """处理样品总体积列"""
        return
    
    def handle_磷酸盐浓度(self, data, context):
        """处理磷酸盐浓度列"""
        return 
        
    def handle_平均值(self, data, context):
        """处理平均值列"""
        return
    
    def handle_吸光值样品(self, data, context):
        """处理吸光值样品列"""
        return
    
    def handle_吸光值空白(self, data, context):
        """处理吸光值空白列"""
        return
    
    def handle_吸光值对比(self, data, context):
        """处理吸光值对比列"""
        return
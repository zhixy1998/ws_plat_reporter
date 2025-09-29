# 模板字段定义
# fill_type: 0 表示从模板中提取的字段, fill_type: 1 表示表格截取的字段

# get_type: 0: 表示从通用数据中取, 1: 表示从接口中取 2: 表从数据库中取
from .common_data import BaseTableDataHandler
python_template_var = {
    "b": {"fill_type": 0},
    "r": {"fill_type": 0},
    "计算公式": {"fill_type": 0},
    "湿度": {"fill_type": 0},
    "标准溶液及编号": {"fill_type": 0},
    "检测项目": {"fill_type": 0},
    "回归方程": {"fill_type": 0},
    "前处理1": {"fill_type": 0},
    "前处理2": {"fill_type": 0},
    "a": {"fill_type": 0},
    "检测依据": {"fill_type": 0},
    "备注": {"fill_type": 0},
    "分析日期": {"fill_type": 0},
    "仪器名称": {"fill_type": 0},
    "数据表格_rows": {"fill_type": 0},
    "溶液浓度": {"fill_type": 0},
    "仪器编号": {"fill_type": 0},
    "温度": {"fill_type": 0}
}

# 表格字段分组
table_jinja_values = {
    'A1': ['A1_0', 'A1_1', 'A1_2', 'A1_3', 'A1_4', 'A1_5', 'A1_6'],
    'A2': ['A2_0', 'A2_1', 'A2_2', 'A2_3', 'A2_4', 'A2_5', 'A2_6'],
    '硝酸盐氮浓度': ['硝酸盐氮浓度_0', '硝酸盐氮浓度_1', '硝酸盐氮浓度_2', '硝酸盐氮浓度_3', '硝酸盐氮浓度_4', '硝酸盐氮浓度_5', '硝酸盐氮浓度_6'],
    'A校准': ['A校准_0', 'A校准_1', 'A校准_2', 'A校准_3', 'A校准_4', 'A校准_5', 'A校准_6']
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
                "硝酸盐氮浓度"
            ],
            [
                "A1"
            ],
            [
                "A2"
            ],
            [
                "A校准"
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
    },
    {
        "has_tr": 1,
        "headers": [
            [
                "样品编号",
                "水样体积",
                "稀释倍数",
                "吸光度A1",
                "吸光度A2",
                "校正吸光度",
                "测定浓度",
                "样品浓度",
                "硝酸盐氮含量平均值"
            ]
        ],
        "col_count": 9,
        "data_rows": [],
        "row_count": 0,
        "table_name": "数据表格",
        "column_width": [
            2780,
            1583,
            1584,
            1584,
            1584,
            1584,
            1586,
            1584,
            1587
        ],
        "structure_type": 0
    }
]

class TableDataHandler(BaseTableDataHandler):
    """表格数据处理类，用于处理数据映射和处理逻辑"""
    
    # 简单字段映射：表头名称 -> 数据库字段名
    HEADER_M_MAPPING = {
        "硝酸盐氮浓度": "Abs",  # 序号列
        "A1": "Abs",
        "A2": "sumAbs",
        "A校准": "Abs",

        "样品编号": "sampleNumber",
        "水样体积": "2191OJP",
        "稀释倍数": "2191OJP",
        "吸光度A1": "2191OJP",
        "吸光度A2": "Abs",
        "校正吸光度": "2191OJP",
        "测定浓度": "Abs",
        "样品浓度":"2191OJP",
        "硝酸盐氮含量平均值":"2191OJP"
    }
    TABLE_NAME_MAP_REVERSE = {
        '表格': ['硝酸盐氮浓度', 'A1', 'A2','A校准'],
        '数据表格': ['样品编号', '水样体积', '稀释倍数', '吸光度A1', '吸光度A2', '校正吸光度', '测定浓度','样品浓度','硝酸盐氮含量平均值']
    }

    TEMPLATE_INFO_MAP = {
        '表格': {
            'tpl_type': 1,   # 1: 每个单元格一个tpl对象，就是横向表格那种 2: 通过docxtpl循环语法渲染
            'column_count': 7
        },        
        '数据表格': {
            'tpl_type': 2,   # 1: 每个单元格一个tpl对象，就是横向表格那种 2: 通过docxtpl循环语法渲染
            'column_count': 9
        }
    }

    standard = ['硝酸盐氮浓度', 'A1', 'A2','A校准']
    unknown = ['样品编号', '水样体积', '稀释倍数', '吸光度A1', '吸光度A2', '校正吸光度', '测定浓度','样品浓度','硝酸盐氮含量平均值']
    
    def __init__(self):
        pass
    
    def handle_硝酸盐氮浓度(self, data, m):
        """处理硝酸盐氮浓度列的逻辑"""

        real_header, sample_data = self.get_standard_head_and_data(data, m)
        return real_header, sample_data
    
    def handle_A1(self, data, m):
        """处理A1列"""
        real_header, sample_data = self.get_standard_head_and_data(data, m)
        return real_header, sample_data
    
    def handle_A2(self, data, m):
        """处理A2列"""
        real_header, sample_data = self.get_standard_head_and_data(data, m)
        return real_header, sample_data
    
    def handle_A校准(self, data, m):
        """处理A校准列"""
        real_header, sample_data = self.get_standard_head_and_data(data, m)
        return real_header, sample_data
    

    def handle_样品编号(self, data, context):
        """处理样品编号列"""
        return 
    
    def handle_水样体积(self, data, context):
        """处理水样体积列"""
        return
    
    def handle_稀释倍数(self, data, context):
        """处理稀释倍数列"""
        return 
        
    def handle_吸光度A1(self, data, context):
        """处理吸光度A1列"""
        return
    
    def handle_吸光度A2(self, data, context):
        """处理吸光度A2列"""
        return
    
    def handle_校正吸光度(self, data, context):
        """处理校正吸光度列"""
        return
    
    def handle_测定浓度(self, data, context):
        """处理测定浓度列"""
        return
    
    def handle_样品浓度(self, data, context):
        """处理样品浓度列"""
        return
    
    def handle_硝酸盐氮含量平均值(self, data, context):
        """硝酸盐氮含量平均值列"""
        return


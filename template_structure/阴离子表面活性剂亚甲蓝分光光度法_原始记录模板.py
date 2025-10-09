# 模板字段定义
# fill_type: 0 表示从模板中提取的字段, fill_type: 1 表示表格截取的字段

# get_type: 0: 表示从通用数据中取, 1: 表示从接口中取 2: 表从数据库中取
from .common_data import BaseTableDataHandler
python_template_var = {
    "r": {"fill_type": 0},
    "温度": {"fill_type": 0},
    "湿度": {"fill_type": 0},
    "数据表格_rows": {"fill_type": 0},
    "分析日期": {"fill_type": 0},
    "备注": {"fill_type": 0},
    "标准溶液及编号": {"fill_type": 0},
    "仪器名称": {"fill_type": 0},
    "a": {"fill_type": 0},
    "回归方程": {"fill_type": 0},
    "b": {"fill_type": 0},
    "仪器编号": {"fill_type": 0},
    "前处理": {"fill_type": 0},
    "检测项目": {"fill_type": 0},
    "溶液浓度": {"fill_type": 0},
    "计算公式": {"fill_type": 0},
    "检测依据": {"fill_type": 0}
}

# 表格字段分组
table_jinja_values = {
    '质量': ['质量_0', '质量_1', '质量_2', '质量_3', '质量_4', '质量_5', '质量_6', '质量_7', '质量_8', '质量_9'],
    '校正吸光度': ['校正吸光度_0', '校正吸光度_1', '校正吸光度_2', '校正吸光度_3', '校正吸光度_4', '校正吸光度_5', '校正吸光度_6', '校正吸光度_7', '校正吸光度_8', '校正吸光度_9'],
    '吸光度': ['吸光度_0', '吸光度_1', '吸光度_2', '吸光度_3', '吸光度_4', '吸光度_5', '吸光度_6', '吸光度_7', '吸光度_8', '吸光度_9']
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
                "质量"
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
        "table_name": "表格",
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
                "试样吸光度",
                "由校准曲线上读取的表观LAS质量",
                "水样中亚甲蓝活性物的浓度",
                "平均值"
            ]
        ],
        "col_count": 7,
        "data_rows": [],
        "row_count": 0,
        "table_name": "数据表格",
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
        "质量": "Abs",  # 序号列
        "吸光度": "Abs",
        "校正吸光度": "sumAbs",

        "样品编号": "sampleNumber",
        "水样体积": "2191OJP",
        "空白吸光度": "2191OJP",
        "试样吸光度": "2191OJP",
        "由校准曲线上读取的表观LAS质量": "Abs",
        "水样中亚甲蓝活性物的浓度": "2191OJP",
        "平均值": "Abs"
    }
    TABLE_NAME_MAP_REVERSE = {
        '表格': ['质量', '吸光度', '校正吸光度'],
        '数据表格': ['样品编号', '水样体积', '空白吸光度', '试样吸光度', '由校准曲线上读取的表观LAS质量', '水样中亚甲蓝活性物的浓度', '平均值']
    }

    TEMPLATE_INFO_MAP = {
        '表格': {
            'tpl_type': 1,   # 1: 每个单元格一个tpl对象，就是横向表格那种 2: 通过docxtpl循环语法渲染
            'column_count': 10
        },        
        '数据表格': {
            'tpl_type': 2,   # 1: 每个单元格一个tpl对象，就是横向表格那种 2: 通过docxtpl循环语法渲染
            'column_count': 7
        }
    }

    standard = ['质量', '吸光度', '校正吸光度']
    unknown = ['样品编号', '水样体积', '空白吸光度', '试样吸光度', '由校准曲线上读取的表观LAS质量', '水样中亚甲蓝活性物的浓度', '平均值']
    
    def __init__(self):
        pass
    
    def handle_质量(self, data, m):
        """处理质量列的逻辑"""

        real_header, sample_data = self.get_standard_head_and_data(data, m)
        return real_header, sample_data
    
    def handle_吸光度(self, data, m):
        """处理吸光度列"""
        real_header, sample_data = self.get_standard_head_and_data(data, m)
        return real_header, sample_data
    
    def handle_校正吸光度(self, data, m):
        """处理校正吸光度列"""
        real_header, sample_data = self.get_standard_head_and_data(data, m)
        return real_header, sample_data
    
    

    def handle_样品编号(self, data, context):
        """处理样品编号列"""
        return 
    
    def handle_水样体积(self, data, context):
        """处理水样体积列"""
        return
    
    def handle_空白吸光度(self, data, context):
        """处理空白吸光度列"""
        return 
        
    def handle_试样吸光度(self, data, context):
        """处理试样吸光度列"""
        return
    
    def handle_由校准曲线上读取的表观LAS质量(self, data, context):
        """处理由校准曲线上读取的表观LAS质量列"""
        return
    
    def handle_水样中亚甲蓝活性物的浓度(self, data, context):
        """处理水样中亚甲蓝活性物的浓度列"""
        return
    
    def handle_平均值(self, data, context):
        """处理平均值列"""
        return
    
    def handle_样品浓度(self, data, context):
        """处理样品浓度列"""
        return
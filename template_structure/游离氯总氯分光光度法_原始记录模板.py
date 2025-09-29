# 模板字段定义
# fill_type: 0 表示从模板中提取的字段, fill_type: 1 表示表格截取的字段

# get_type: 0: 表示从通用数据中取, 1: 表示从接口中取 2: 表从数据库中取
from .common_data import BaseTableDataHandler
python_template_var = {
    "标准溶液及编号": {"fill_type": 0},
    "前处理": {"fill_type": 0},
    "检测项目": {"fill_type": 0},
    "温度": {"fill_type": 0},
    "分析日期": {"fill_type": 0},
    "仪器编号": {"fill_type": 0},
    "湿度": {"fill_type": 0},
    "r": {"fill_type": 0},
    "数据表格_rows": {"fill_type": 0},
    "b": {"fill_type": 0},
    "溶液浓度": {"fill_type": 0},
    "a": {"fill_type": 0},
    "仪器名称": {"fill_type": 0},
    "回归方程": {"fill_type": 0},
    "检测依据": {"fill_type": 0},
    "计算公式": {"fill_type": 0},
    "备注": {"fill_type": 0}
}

# 表格字段分组
table_jinja_values = {
    '校正吸光度': ['校正吸光度_0', '校正吸光度_1', '校正吸光度_2', '校正吸光度_3', '校正吸光度_4', '校正吸光度_5', '校正吸光度_6'],
    '吸光度': ['吸光度_0', '吸光度_1', '吸光度_2', '吸光度_3', '吸光度_4', '吸光度_5', '吸光度_6'],
    '氯质量浓度': ['氯质量浓度_0', '氯质量浓度_1', '氯质量浓度_2', '氯质量浓度_3', '氯质量浓度_4', '氯质量浓度_5', '氯质量浓度_6']
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
                "氯质量浓度"
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
            2779,
            2779,
            2779
        ],
        "structure_type": 1
    },
    {
        "has_tr": 1,
        "headers": [
            [
                "样品编号",
                "试样体积",
                "稀释倍数",
                "空白吸光度",
                "试样吸光度",
                "试样中游离氯质量浓度",
                "试样中总氯质量浓度",
                "测定氧化锰和六价铬干扰时相当于氯的质量浓度",
                "质量浓度",
                "平均值"
            ]
        ],
        "col_count": 10,
        "data_rows": [],
        "row_count": 0,
        "table_name": "表格2",
        "column_width": [
            2779,
            1408,
            1413,
            1393,
            1418,
            1398,
            1420,
            1398,
            1418,
            1411
        ],
        "structure_type": 0
    },
    {
        "has_tr": 1,
        "headers": [
            [
                "样品编号",
                "试样体积",
                "稀释倍数",
                "空白吸光度",
                "试样吸光度",
                "试样中游离氯质量浓度",
                "试样中总氯质量浓度",
                "测定氧化锰和六价铬干扰时相当于氯的质量浓度",
                "质量浓度",
                "平均值"
            ]
        ],
        "col_count": 10,
        "data_rows": [],
        "row_count": 0,
        "table_name": "数据表格",
        "column_width": [
            2781,
            1408,
            1413,
            1393,
            1418,
            1408,
            1408,
            1398,
            1418,
            1411
        ],
        "structure_type": 0
    }
]
class TableDataHandler(BaseTableDataHandler):
    """表格数据处理类，用于处理数据映射和处理逻辑"""
    
    # 简单字段映射：表头名称 -> 数据库字段名
    HEADER_M_MAPPING = {
        "氯质量浓度": "Abs",  # 序号列
        "吸光度": "Abs",
        "校正吸光度": "sumAbs",

        "样品编号": "sampleNumber",
        "试样体积": "2191OJP",
        "稀释倍数": "2191OJP",
        "空白吸光度": "2191OJP",
        "试样吸光度": "2191OJP",
        "试样中游离氯质量浓度": "Abs",
        "试样中总氯质量浓度": "2191OJP",
        "测定氧化锰和六价铬干扰时相当于氯的质量浓度": "Abs",
        "质量浓度": "2191OJP",
        "平均值": "Abs"
    }
    TABLE_NAME_MAP_REVERSE = {
        '表格1': ['氯质量浓度', '吸光度', '校正吸光度'],
        '表格2': ['样品编号', '试样体积','稀释倍数', '空白吸光度', '试样吸光度', '试样中游离氯质量浓度', '试样中总氯质量浓度', '测定氧化锰和六价铬干扰时相当于氯的质量浓度','质量浓度','平均值'],
        '数据表格': ['样品编号', '试样体积','稀释倍数', '空白吸光度', '试样吸光度', '试样中游离氯质量浓度', '试样中总氯质量浓度', '测定氧化锰和六价铬干扰时相当于氯的质量浓度','质量浓度','平均值']
    }

    TEMPLATE_INFO_MAP = {
        '表格1': {
            'tpl_type': 1,   # 1: 每个单元格一个tpl对象，就是横向表格那种 2: 通过docxtpl循环语法渲染
            'column_count': 7
        }, 
        '表格2': {
            'tpl_type': 2,   # 1: 每个单元格一个tpl对象，就是横向表格那种 2: 通过docxtpl循环语法渲染
            'column_count': 10
        },       
        '数据表格': {
            'tpl_type': 2,   # 1: 每个单元格一个tpl对象，就是横向表格那种 2: 通过docxtpl循环语法渲染
            'column_count': 10
        }
    }

    standard = ['氯质量浓度', '吸光度', '校正吸光度']
    unknown = ['样品编号', '试样体积','稀释倍数', '空白吸光度', '试样吸光度', '试样中游离氯质量浓度', '试样中总氯质量浓度', '测定氧化锰和六价铬干扰时相当于氯的质量浓度','质量浓度','平均值']
    
    def __init__(self):
        pass
    
    def handle_氯质量浓度(self, data, m):
        """处理氯质量浓度列的逻辑"""

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
    
    def handle_试样体积(self, data, context):
        """处理试样体积列"""
        return
    
    def handle_稀释倍数(self, data, context):
        """处理稀释倍数列"""
        return 
        
    def handle_空白吸光度(self, data, context):
        """处理空白吸光度列"""
        return
    
    def handle_试样吸光度(self, data, context):
        """处理试样吸光度列"""
        return
    
    def handle_试样中游离氯质量浓度(self, data, context):
        """处理试样中游离氯质量浓度列"""
        return
    
    def handle_试样中总氯质量浓度(self, data, context):
        """处理试样中总氯质量浓度列"""
        return
    
    def handle_测定氧化锰和六价铬干扰时相当于氯的质量浓度(self, data, context):
        """处理测定氧化锰和六价铬干扰时相当于氯的质量浓度列"""
        return
    
    def handle_质量浓度(self, data, context):
        """处理质量浓度列"""
        return
    
    def handle_平均值(self, data, context):
        """处理平均值列"""
        return

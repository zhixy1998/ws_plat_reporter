# 模板字段定义
# fill_type: 0 表示从模板中提取的字段, fill_type: 1 表示表格截取的字段

# get_type: 0: 表示从通用数据中取, 1: 表示从接口中取 2: 表从数据库中取
from .common_data import BaseTableDataHandler
python_template_var = {
    "温度": {"fill_type": 0},
    "a": {"fill_type": 0},
    "湿度": {"fill_type": 0},
    "溶液浓度": {"fill_type": 0},
    "检测依据": {"fill_type": 0},
    "表格2_rows": {"fill_type": 0},
    "回归方程": {"fill_type": 0},
    "仪器名称": {"fill_type": 0},
    "仪器编号": {"fill_type": 0},
    "样品前处理": {"fill_type": 0},
    "标准溶液及编号": {"fill_type": 0},
    "检测项目": {"fill_type": 0},
    "r": {"fill_type": 0},
    "检测日期": {"fill_type": 0},
    "b": {"fill_type": 0},
    "计算公式": {"fill_type": 0},
    "备注": {"fill_type": 0},
    "grouped_data": {"fill_type": 0}
}

# 表格字段分组
table_jinja_values = {
    '吸光度': ['吸光度_0', '吸光度_1', '吸光度_2', '吸光度_3', '吸光度_4', '吸光度_5', '吸光度_6', '吸光度_7'],
    '磷酸盐含量': ['磷酸盐含量_0', '磷酸盐含量_1', '磷酸盐含量_2', '磷酸盐含量_3', '磷酸盐含量_4', '磷酸盐含量_5', '磷酸盐含量_6', '磷酸盐含量_7']
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
                "磷酸盐含量"
            ],
            [
                "吸光度"
            ]
        ],
        "col_count": 2,
        "data_rows": [],
        "row_count": 0,
        "table_name": "表格1",
        "column_width": [
            2779,
            2779
        ],
        "structure_type": 1
    },
    {
        "has_tr": 1,
        "headers": [
            [
                "水样吸光度",
                "样品编号",
                "水样体积",
                "空白试验吸光度",
                "从标准曲线上查得的样品管中磷酸盐的含量",
                "水样中磷酸盐的质量浓度",
                "平均值"
            ]
        ],
        "col_count": 7,
        "data_rows": [],
        "row_count": 0,
        "table_name": "表格3",
        "column_width": [
            2781,
            2781,
            2112,
            2112,
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
        "磷酸盐含量": "normalConcentration",  # 序号列
        "吸光度": "Abs",

        "样品编号": "V5",  # 序号列
        "平均值":"V6",
        "空白试验吸光度":"V7", 
        "水样体积":"V6", 
        "水样吸光度":"V8", 
        "从标准曲线上查得的样品管中磷酸盐的含量":"V6", 
        "水样中磷酸盐的质量浓度":"V6",  
        
    }

    TABLE_NAME_MAP_REVERSE = {
        '表格1': ['磷酸盐含量', '吸光度'],
        '表格2': ['样品编号', '水样体积', '空白试验吸光度', '水样吸光度', '从标准曲线上查得的样品管中磷酸盐的含量', '水样中磷酸盐的质量浓度', '平均值'],
        '表格3':['样品编号', '水样体积', '空白试验吸光度', '水样吸光度', '从标准曲线上查得的样品管中磷酸盐的含量', '水样中磷酸盐的质量浓度', '平均值']
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
    
    standard = ['磷酸盐含量', '吸光度']
    unknown = ['样品编号', '水样体积', '空白试验吸光度', '水样吸光度', '从标准曲线上查得的样品管中磷酸盐的含量', '水样中磷酸盐的质量浓度', '平均值']

    def __init__(self):
        # TABLE_NAME_MAP_REVERSE = {'小表格': ['氨氮含量', '吸光度', '校正吸光度']}
        pass
    
    def handle_磷酸盐含量(self, data, m):
        """处理序号列的逻辑"""
        real_header, sample_data = self.get_standard_head_and_data(data, m)
        return real_header, sample_data
    
    def handle_吸光度(self, data, m):
        """处理检测时间和对应的吸光值列"""
        real_header, sample_data = self.get_standard_head_and_data(data, m)
        return real_header, sample_data
    
    def handle_样品编号(self, data, context, row_index=0):
        """处理序号列的逻辑"""
        return str(row_index + 1)

    def handle_水样体积(self, data, context):
        """处理取水样体积"""
        return data.get('m2', '')
    
    def handle_空白试验吸光度(self, data, context):
        """处理空白试验吸光度列"""
        return data.get('m3', '')

    def handle_水样吸光度(self, data, context):
        """处理水样吸光度列"""
        return data.get('m4', '')
    
    def handle_从标准曲线上查得的样品管中磷酸盐的含量(self, data, context):
        """校准曲线从标准曲线上查得的样品管中磷酸盐的含量"""
        return data.get('m8', '')

    def handle_水样中磷酸盐的质量浓度(self, data, context):
        """水样中磷酸盐的质量浓度"""
        return data.get('m9', '')
    
    def handle_平均值(self, data, context):
        """平均值"""
        return data.get('m10', '')
    
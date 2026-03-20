
# 模板字段定义
# fill_type: 0 表示从模板中提取的字段, fill_type: 1 表示表格截取的字段

# get_type: 0: 表示从通用数据中取, 1: 表示从接口中取 2: 表从数据库中取

from .common_data import BaseTableDataHandler

python_template_var = {
    "仪器编号": {"fill_type": 0},
    "a": {"fill_type": 0},
    "检测依据": {"fill_type": 0},
    "温度": {"fill_type": 0},
    "溶液浓度": {"fill_type": 0},
    "湿度": {"fill_type": 0},
    "分析日期": {"fill_type": 0},
    "前处理": {"fill_type": 0},
    "回归方程": {"fill_type": 0},
    "未知样表格2_rows": {"fill_type": 0},
    "检测项目": {"fill_type": 0},
    "计算公式": {"fill_type": 0},
    "r": {"fill_type": 0},
    "未知样表格1_rows": {"fill_type": 0},
    "b": {"fill_type": 0},
    "标准溶液及编号": {"fill_type": 0},
    "仪器名称": {"fill_type": 0},
    "备注": {"fill_type": 0}
}

# 表格字段分组
table_jinja_values = {
    '吸光值': ['吸光值_0', '吸光值_1', '吸光值_2', '吸光值_3', '吸光值_4', '吸光值_5'],
    '质量浓度': ['质量浓度_0', '质量浓度_1', '质量浓度_2', '质量浓度_3', '质量浓度_4', '质量浓度_5'],
    '校正吸光值': ['校正吸光值_0', '校正吸光值_1', '校正吸光值_2', '校正吸光值_3', '校正吸光值_4', '校正吸光值_5']
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
                "质量浓度"
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
            3987,
            3987,
            3987
        ],
        "structure_type": 1
    },
    {
        "has_tr": 1,
        "headers": [
            [
                "样品编号",
                "采样用吸收液体积",
                "采样体积",
                "稀释倍数",
                "空白A",
                "串联第一支样品",
                "串联第二支样品",
                "pNO2",
                "pNO",
                "primeNO",
                "pNOx"
            ]
        ],
        "col_count": 11,
        "data_rows": [],
        "row_count": 0,
        "table_name": "未知样表格1",
        "column_width": [
            2816,
            1171,
            1200,
            872,
            1243,
            1300,
            1385,
            1376,
            1376,
            1376,
            1377
        ],
        "structure_type": 0
    },
    {
        "has_tr": 1,
        "headers": [
            [
                "样品编号",
                "采样用吸收液体积",
                "采样体积",
                "稀释倍数",
                "空白A",
                "串联第一支样品",
                "串联第二支样品",
                "pNO2",
                "pNO",
                "perimeNO",
                "pNOx"
            ]
        ],
        "col_count": 11,
        "data_rows": [],
        "row_count": 0,
        "table_name": "未知样表格2",
        "column_width": [
            2816,
            1171,
            1200,
            872,
            1243,
            1300,
            1385,
            1376,
            1376,
            1376,
            1377
        ],
        "structure_type": 0
    }
]



class TableDataHandler(BaseTableDataHandler):
    """表格数据处理类，用于处理数据映射和处理逻辑"""
    
    # 简单字段映射：表头名称 -> 数据库字段名
    HEADER_M_MAPPING = {
        "吸光值": "Abs",
        "质量浓度": "normalConcentration",
        "校正吸光值": "sumAbs",
        "样品编号": "sampleNumber",
        "采样用吸收液体积": "2191OJP",
        "采样体积": "2191OJP",
        "稀释倍数": "2191OJP",
        "空白A": "2191OJP",
        "串联第一支样品": "2191OJP",
        "串联第二支样品": "2191OJP",
        "pNO2": "2191OJP",
        "pNO": "2191OJP",
        "primeNO": "2191OJP",
        "pNOx": "2191OJP",
    }

    TEMPLATE_INFO_MAP = {
            '已知样表格': {
             'tpl_type': 1,   # 1: 每个单元格一个tpl对象，就是横向表格那种 2: 通过docxtpl循环语法渲染
             'column_count': 3
            },
            '未知样表格1': {
             'tpl_type': 2,   # 1: 每个单元格一个tpl对象，就是横向表格那种 2: 通过docxtpl循环语法渲染
             'column_count': 12
            },
            '未知样表格2': {
             'tpl_type': 2,   # 1: 每个单元格一个tpl对象，就是横向表格那种 2: 通过docxtpl循环语法渲染
             'column_count': 12
            }
        }
    
    standard = ['质量浓度', '吸光值', '校正吸光值']

    TABLE_NAME_MAP_REVERSE = {
        '已知样表格': ['质量浓度', '吸光值', '校正吸光值'],
        '未知样表格1': ['样品编号', '采样用吸收液体积', '采样体积', '稀释倍数', '空白A', '串联第一支样品', '串联第二支样品', 'pNO2', 'pNO', 'primeNO', 'pNOx'],
        '未知样表格2': ['样品编号', '采样用吸收液体积', '采样体积', '稀释倍数', '空白A', '串联第一支样品', '串联第二支样品', 'pNO2', 'pNO', 'primeNO', 'pNOx']
    }
    
    def __init__(self):
        # TABLE_NAME_MAP_REVERSE = {'表格': ['样品编号', '水样体积', '空白吸光度', '水样吸光度', '标准曲线上氨氮质量', '从标准曲线上查得的甲醛量', '平均值']}
        # self.TABLE_NAME_MAP_REVERSE = {v: [k for k, v2 in self.TABLE_NAME_MAP.items() if v2 == v] for v in set(self.TABLE_NAME_MAP.values())}
        pass
    
    def handle_质量浓度(self, data, m):
        real_header, sample_data = self.get_standard_head_and_data(data, m)
        return real_header, sample_data
    
    def handle_吸光值(self, data, m):
        real_header, sample_data = self.get_standard_head_and_data(data, m)
        return real_header, sample_data

    def handle_校正吸光值(self, data, m):
        real_header, sample_data = self.get_standard_head_and_data(data, m)
        return real_header, sample_data
    
    # def handle_校正吸光度(self, data, m):
    #     """处理序号列的逻辑"""
    #     real_header, sample_data = self.get_standard_head_and_data(data, m)
    #     return real_header, sample_data
    
    # def handle_样品编号(self, data, context, row_index=0):
    #     """处理序号列的逻辑"""
    #     return
    
    # def handle_空白试验吸光度(self, data, context):
    #     """处理空白试验吸光度"""
    #     return
    
    # def handle_水样体积(self, data, context):
    #     """处理检测时间和对应的吸光值列"""
    #     return
    
    # def handle_稀释倍数(self, data, context):
    #     """处理T(min)列"""
    #     return

    # def handle_水样吸光度(self, data, context):
    #     """处理T(min)列"""
    #     return
    
    # def handle_水样中氨氮质量浓度(self, data, context):
    #     """处理T(min)列"""
    #     return
    
    # def handle_平均值(self, data, context):
    #     """处理T(min)列"""
    #     return
    





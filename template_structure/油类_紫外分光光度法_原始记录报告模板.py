# 模板字段定义
# fill_type: 0 表示从模板中提取的字段, fill_type: 1 表示表格截取的字段

# get_type: 0: 表示从通用数据中取, 1: 表示从接口中取 2: 表从数据库中取

python_template_var = {
    "检测依据": {"fill_type": 0},
    "备注": {"fill_type": 0},
    "温度": {"fill_type": 0},
    "仪器编号": {"fill_type": 0},
    "r": {"fill_type": 0},
    "仪器名称": {"fill_type": 0},
    "湿度": {"fill_type": 0},
    "b": {"fill_type": 0},
    "标准溶液浓度": {"fill_type": 0},
    "表格1_rows": {"fill_type": 0},
    "回归方程": {"fill_type": 0},
    "检测项目": {"fill_type": 0},
    "标准溶液及编号": {"fill_type": 0},
    "分析日期": {"fill_type": 0},
    "a": {"fill_type": 0},
    "计算公式": {"fill_type": 0},
    "样品前处理": {"fill_type": 0}
}

# 表格字段分组
table_jinja_values = {
    '吸光值': ['吸光值_0', '吸光值_1', '吸光值_2', '吸光值_3', '吸光值_4', '吸光值_5'],
    '油浓度': ['油浓度_0', '油浓度_1', '油浓度_2', '油浓度_3', '油浓度_4', '油浓度_5']
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
                "油浓度"
            ],
            [
                "吸光值"
            ]
        ],
        "col_count": 2,
        "data_rows": [],
        "row_count": 0,
        "table_name": "表格2",
        "column_width": [
            3278,
            3278
        ],
        "structure_type": 1
    }
]

class TableDataHandler:
    """表格数据处理类，用于处理数据映射和处理逻辑"""
    
    # 简单字段映射：表头名称 -> 数据库字段名
    HEADER_M_MAPPING = {
        "样品编号": "V5",  # 序号列
        "取样量": "V6",
        "稀释倍数": "V6",
        "油标准的回收量平均值": 'V7',
        "空白的平均值": 'V6',
        '油标准加入量': 'V7',        
        '萃取效率系数': 'V5' ,  
        '正己烷萃取液体积': 'V5' ,
        '含水率': 'V5' ,
        '空白0': 'V5' ,
        '空白1': 'V5' ,
        '油的浓度': 'V5' ,
        '空白2': 'V5' ,
        '油类的含量': 'V5' ,
        '平均值': 'V5' ,

        "油浓度": "V5",
        "吸光值": "V6",
    }

    


    TABLE_NAME_MAP = {
        "样品编号":'表格1',  # 序号列
        "取样量": "表格1",
        "稀释倍数": "表格1",
        "油标准的回收量平均值": '表格1',
        "空白的平均值": '表格1',
        '油标准加入量': '表格1',
        '萃取效率系数': '表格1' ,  
        '正己烷萃取液体积': '表格1' ,
        '含水率': '表格1' ,
        '空白0': '表格1' ,
        '空白1': '表格1' ,
        '油的浓度': '表格1' ,
        '空白2': '表格1' ,
        '油类的含量': '表格1' ,
        '平均值': '表格1',

        '油浓度':'表格2',
        '吸光值':'表格2',
    }

    TEMPLATE_INFO_MAP = {
        '表格1': {
            'tpl_type': 2,   # 1: 每个单元格一个tpl对象，就是横向表格那种 2: 通过docxtpl循环语法渲染
            'column_count': None
        },
        '表格2': {
            'tpl_type': 1,   # 1: 每个单元格一个tpl对象，就是横向表格那种 2: 通过docxtpl循环语法渲染
            'column_count': None
        }
    }
    
    standard =["油浓度","吸光值"]
    unknown =['样品编号','取样量','稀释倍数','油标准的回收量平均值'
    ,'空白的平均值','油标准加入量','萃取效率系数','正己烷萃取液体积',
    '含水率','空白0','空白1','空白2','油的浓度','油类的含量','平均值']

    def __init__(self):
        self.TABLE_NAME_MAP_REVERSE = {v: [k for k, v2 in self.TABLE_NAME_MAP.items() if v2 == v] for v in set(self.TABLE_NAME_MAP.values())}
        
    def handle_吸光值(self, data, context):
        """处理检测时间和对应的吸光值列"""
        return data.get('m2', '')
    
    def handle_油浓度(self, data, context):
        """处理检测时间和对应的吸光值列"""
        return data.get('m2', '')


    # def handle_样品编号(self, data, context, row_index=0):
    #     return str(row_index + 1)
    
    # def handle_取样量(self, data, context):
    #     return data.get('m2', '')
    
    # def handle_稀释倍数(self, data, context):
    #     return data.get('m3', '')
    
    # def handle_油标准的回收量平均值(self, data, context):
    #     return data.get('m2', '')
    
    # def handle_空白的平均值(self, data, context):
    #     return data.get('m3', '')
    
    # def handle_油标准加入量(self, data, context):
    #     return data.get('m4', '')
    
    # def handle_萃取效率系数(self, data, context):
    #     return data.get('m5', '')

    # def handle_正己烷萃取液体积(self, data, context):
    #     return data.get('m5', '')

    # def handle_含水率(self, data, context):
    #     return data.get('m5', '')

    # def handle_空白0(self, data, context):
    #     return data.get('m5', '')

    # def handle_空白1(self, data, context):
    #     return data.get('m5', '')

    # def handle_空白2(self, data, context):
    #     return data.get('m5', '')

    # def handle_油的浓度(self, data, context):
    #     return data.get('m5', '')

    # def handle_油类的含量(self, data, context):
    #     return data.get('m5', '')

    # def handle_平均值(self, data, context):
    #     return data.get('m5', '')
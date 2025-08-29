# 模板字段定义
# fill_type: 0 表示从模板中提取的字段, fill_type: 1 表示表格截取的字段

# get_type: 0: 表示从通用数据中取, 1: 表示从接口中取 2: 表从数据库中取

python_template_var = {
    "湿度": {"fill_type": 0},
    "标准溶液及编号": {"fill_type": 0},
    "r": {"fill_type": 0},
    "备注": {"fill_type": 0},
    "回归方程": {"fill_type": 0},
    "检测依据": {"fill_type": 0},
    "仪器名称": {"fill_type": 0},
    "样品前处理": {"fill_type": 0},
    "a": {"fill_type": 0},
    "表格2_rows": {"fill_type": 0},
    "仪器编号": {"fill_type": 0},
    "计算公式": {"fill_type": 0},
    "温度": {"fill_type": 0},
    "检测日期": {"fill_type": 0},
    "b": {"fill_type": 0},
    "溶液浓度": {"fill_type": 0},
    "检测项目": {"fill_type": 0}
}

# 表格字段分组
table_jinja_values = {
    '吸光度': ['吸光度_0', '吸光度_1', '吸光度_2', '吸光度_3', '吸光度_4', '吸光度_5'],
    '校正吸光度': ['校正吸光度_0', '校正吸光度_1', '校正吸光度_2', '校正吸光度_3', '校正吸光度_4', '校正吸光度_5'],
    '亚硝酸盐氮浓度': ['亚硝酸盐氮浓度_0', '亚硝酸盐氮浓度_1', '亚硝酸盐氮浓度_2', '亚硝酸盐氮浓度_3', '亚硝酸盐氮浓度_4', '亚硝酸盐氮浓度_5']
}
table_fields = [
    {
        "headers": [
            [
                "亚硝酸盐氮浓度"
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
            2096,
            2096,
            2096
        ],
        "structure_type": 1
    },
    {
        "has_tr": 1,
        "headers": [
            [
                "样品编号",
                "水样体积",
                "空白试验吸光度",
                "试份溶液吸光度",
                "亚硝酸盐氮含量",
                "平均值"
            ]
        ],
        "col_count": 6,
        "data_rows": [],
        "row_count": 0,
        "table_name": "表格2",
        "column_width": [
            2096,
            2560,
            2693,
            2980,
            2583,
            2544
        ],
        "structure_type": 0
    }
]


class TableDataHandler:
    """表格数据处理类，用于处理数据映射和处理逻辑"""
    
    # 简单字段映射：表头名称 -> 数据库字段名
    HEADER_M_MAPPING = {
        "校正吸光度": "A1",  # 序号列
        "吸光度": "V8",
        "亚硝酸盐氮浓度": "V6",

        "样品编号": "A1",  # 序号列
        "水样体积": "V8",
        "空白试验吸光度": "V6",
        "试份溶液吸光度": "A1",
        "亚硝酸盐氮含量": "A1",
        '平均值': 'A1'
    }
    TABLE_NAME_MAP = {
       '校正吸光度':'表格1',
       '吸光度':'表格1',
       '亚硝酸盐氮浓度':'表格1',

        "样品编号":'表格2',  # 序号列
        "水样体积": '表格2',
        "空白试验吸光度":'表格2',
        "试份溶液吸光度": '表格2',
        "亚硝酸盐氮含量": '表格2',
        '平均值': '表格2'      
    }

    TEMPLATE_INFO_MAP = {
        '表格1': {
            'tpl_type': 1,   # 1: 每个单元格一个tpl对象，就是横向表格那种 2: 通过docxtpl循环语法渲染
            'column_count': 7
        },
        '表格2':{
            'tpl_type': 2,   # 1: 每个单元格一个tpl对象，就是横向表格那种 2: 通过docxtpl循环语法渲染
            'column_count': 6
        }
    }
    
    def __init__(self):
        # TABLE_NAME_MAP_REVERSE = {'表格1': ['校正吸光度', '吸光度', '亚硝酸盐氮浓度'],
        # '表格2': ['样品编号', '水样体积', '空白试验吸光度', '试份溶液吸光度', '亚硝酸盐氮含量', '平均值']}
        self.TABLE_NAME_MAP_REVERSE = {v: [k for k, v2 in self.TABLE_NAME_MAP.items() if v2 == v] for v in set(self.TABLE_NAME_MAP.values())}
    
    def handle_氨氮含量(self, data, context, row_index=0):
        """处理序号列的逻辑"""
        return str(row_index + 1)
    
    def handle_吸光度(self, data, context):
        """处理检测时间和对应的吸光值列"""
        return data.get('m2', '')
    
    def handle_校正吸光度(self, data, context):
        """处理T(min)列"""
        return data.get('m3', '')
    

    def handle_样品编号(self, data, context, row_index=0):
        """处理序号列的逻辑"""
        return str(row_index + 1)    
    #表格二所有的handle
    def handle_水样体积(self, data, context):
        """处理检测时间和对应的吸光值列"""
        return data.get('m2', '')
    
    def handle_空白试验吸光度(self, data, context):
        """处理检测时间和对应的吸光值列"""
        return data.get('m2', '')
    
    def handle_试份溶液吸光度(self, data, context):
        """处理检测时间和对应的吸光值列"""
        return data.get('m2', '')
    
    def handle_亚硝酸盐氮含量(self, data, context):
        """处理检测时间和对应的吸光值列"""
        return data.get('m2', '')
    
    def handle_平均值(self, data, context):
        """处理检测时间和对应的吸光值列"""
        return data.get('m2', '')
    
    
# 模板字段定义
# fill_type: 0 表示从模板中提取的字段, fill_type: 1 表示表格截取的字段

# get_type: 0: 表示从通用数据中取, 1: 表示从接口中取 2: 表从数据库中取

python_template_var = {
    "表格1_rows": {"fill_type": 0},
    "备注": {"fill_type": 0}
}

# 字段渲染表格
custom_bookmark = {
    'project_name':'项目名称',
    'note':'备注',
}

table_fields = [
    {
        "has_tr": 1,
        "headers": [
            [
                "样品编号",
                "取样量",
                "稀释倍数",
                "油标准的回收量平均值",
                "空白的平均值",
                "油标准加入量",
                "萃取效率系数",
                "正己烷萃取液体积",
                "含水率",
                "油的浓度",
                "油类的含量",
                "平均值",
                "空白0",
                "空白1",
                "空白2"
            ]
        ],
        "col_count": 15,
        "data_rows": [],
        "row_count": 0,
        "table_name": "表格1",
        "column_width": [
            1408,
            1134,
            1134,
            1276,
            1130,
            925,
            925,
            989,
            861,
            900,
            950,
            1459,
            1123,
            727,
            925
        ],
        "structure_type": 0
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
        '平均值': 'V5'  
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
        '平均值': '表格1'  
    }

    TEMPLATE_INFO_MAP = {
        '表格1': {
            'tpl_type': 2,   # 1: 每个单元格一个tpl对象，就是横向表格那种 2: 通过docxtpl循环语法渲染
            'column_count': None
        }
    }
    


    def __init__(self):
        # TABLE_NAME_MAP_REVERSE = {'表格1': ['样品编号', '水样体积', '萃取液体积', 
        # '吸光度空白', '吸光度样品', '吸光度对比', '水中石油类的质量浓度', '平均值']}
        self.TABLE_NAME_MAP_REVERSE = {v: [k for k, v2 in self.TABLE_NAME_MAP.items() if v2 == v] for v in set(self.TABLE_NAME_MAP.values())}
    
    def handle_样品编号(self, data, context, row_index=0):
        return str(row_index + 1)
    
    def handle_取样量(self, data, context):
        return data.get('m2', '')
    
    def handle_稀释倍数(self, data, context):
        return data.get('m3', '')
    
    def handle_油标准的回收量平均值(self, data, context):
        return data.get('m2', '')
    
    def handle_空白的平均值(self, data, context):
        return data.get('m3', '')
    
    def handle_油标准加入量(self, data, context):
        return data.get('m4', '')
    
    def handle_萃取效率系数(self, data, context):
        return data.get('m5', '')
    def handle_正己烷萃取液体积(self, data, context):
        return data.get('m5', '')
    def handle_含水率(self, data, context):
        return data.get('m5', '')
    def handle_空白0(self, data, context):
        return data.get('m5', '')
    def handle_空白1(self, data, context):
        return data.get('m5', '')
    def handle_空白2(self, data, context):
        return data.get('m5', '')
    def handle_油的浓度(self, data, context):
        return data.get('m5', '')
    def handle_油类的含量(self, data, context):
        return data.get('m5', '')
    def handle_平均值(self, data, context):
        return data.get('m5', '')
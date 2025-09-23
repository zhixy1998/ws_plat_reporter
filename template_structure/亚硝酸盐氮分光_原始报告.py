# 模板字段定义
# fill_type: 0 表示从模板中提取的字段, fill_type: 1 表示表格截取的字段

# get_type: 0: 表示从通用数据中取, 1: 表示从接口中取 2: 表从数据库中取

from .common_data import BaseTableDataHandler

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
        "headers": [
            [
                "样品编号",
                "取试份体积",
                "空白试验吸光度",
                "色度校正吸光度",
                "试份溶液吸光度",
                "试份溶液校正吸光度",
                "亚硝酸盐氮含量",
                "平均值"
            ]
        ],
        "col_count": 8,
        "data_rows": [],
        "row_count": 0,
        "table_name": "表格1",
        "column_width": [
            1971,
            1700,
            2722,
            1799,
            1819,
            1811,
            1811,
            1823
        ],
        "structure_type": 0
    }
]

class TableDataHandler(BaseTableDataHandler):
    """表格数据处理类，用于处理数据映射和处理逻辑"""
    
    # 简单字段映射：表头名称 -> 数据库字段名
    HEADER_M_MAPPING = {
        "样品编号": "V5",  # 序号列
        "取试份体积": "V6",
        "空白试验吸光度": "V6",
        "色度校正吸光度": 'V5',
        "试份溶液吸光度": 'V5',
        '试份溶液校正吸光度': 'V5',
        '亚硝酸盐氮含量': 'V5' ,  
        '平均值': 'V5'  
    }

    TABLE_NAME_MAP = {
        "样品编号":'表格1',  # 序号列
        "取试份体积": "表格1",
        "空白试验吸光度": "表格1",
        "色度校正吸光度": '表格1',
        "试份溶液吸光度": '表格1',
        '试份溶液校正吸光度': '表格1',
        '亚硝酸盐氮含量': '表格1' ,  
        '平均值': '表格1'  
    }

    TEMPLATE_INFO_MAP = {
        '表格1': {
            'tpl_type': 2,   # 1: 每个单元格一个tpl对象，就是横向表格那种 2: 通过docxtpl循环语法渲染
            'column_count': None
        }
    }
    


    def __init__(self):
        self.TABLE_NAME_MAP_REVERSE = {v: [k for k, v2 in self.TABLE_NAME_MAP.items() if v2 == v] for v in set(self.TABLE_NAME_MAP.values())}
    
    def handle_样品编号(self, data, context, row_index=0):
        return str(row_index + 1)
    
    def handle_取试份体积(self, data, context):
        return data.get('m2', '')
    
    def handle_空白试验吸光度(self, data, context):
        return data.get('m3', '')
    
    def handle_色度校正吸光度(self, data, context):
        return data.get('m2', '')
    
    def handle_试份溶液吸光度(self, data, context):
        return data.get('m3', '')
    
    def handle_试份溶液校正吸光度(self, data, context):
        return data.get('m4', '')
    
    def handle_亚硝酸盐氮含量(self, data, context):
        return data.get('m5', '')
    
    def handle_平均值(self, data, context):
        return data.get('m5', '')
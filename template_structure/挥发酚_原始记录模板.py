# 模板字段定义
# fill_type: 0 表示从模板中提取的字段, fill_type: 1 表示表格截取的字段

# get_type: 0: 表示从通用数据中取, 1: 表示从接口中取 2: 表从数据库中取

from .common_data import BaseTableDataHandler

python_template_var = {
    "表格1_rows": {"fill_type": 0},
    "备注": {"fill_type": 0}
}
table_fields = [
    {
        "has_tr": 1,
        "headers": [
            [
                "样品编号",
                "水样体积",
                "稀释倍数",
                "空白吸光度",
                "水样吸光度",
                "校正吸光度",
                "挥发酚的质量",
                "挥发酚的浓度",
                "平均值"
            ]
        ],
        "col_count": 9,
        "data_rows": [],
        "row_count": 0,
        "table_name": "表格1",
        "column_width": [
            2781,
            1584,
            1584,
            1584,
            1584,
            1584,
            1584,
            2552,
            1057
        ],
        "structure_type": 0
    }
]


class TableDataHandler(BaseTableDataHandler):
    """表格数据处理类，用于处理数据映射和处理逻辑"""
    
    # 简单字段映射：表头名称 -> 数据库字段名
    HEADER_M_MAPPING = {

        "样品编号": "V6",# 序号列
        "水样体积":'V7',
        "稀释倍数": 'A1',
        "空白吸光度": 'A1',
        '水样吸光度': 'A1',
        '校正吸光度': 'V5' ,
        "挥发酚的质量": "A1",  
        '挥发酚的浓度': 'V5' ,  
        '平均值': 'V5'   

    }

    TABLE_NAME_MAP = {
        "样品编号":'表格1',  # 序号列
        "水样体积": '表格1',
        "稀释倍数":'表格1',
        "空白吸光度": '表格1',
        "水样吸光度": '表格1',
        '校正吸光度': '表格1',
        '挥发酚的质量': '表格1' ,  
        '挥发酚的浓度': '表格1' ,  
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

    def handle_挥发酚的质量(self, data, context):
        return data.get('m2', '') 
   
    def handle_样品编号(self, data, context):
        return data.get('m3', '')
    
    def handle_水样体积(self, data, context):
        return data.get('m3', '')
    
    def handle_稀释倍数(self, data, context):
        return data.get('m3', '')
    
    def handle_空白吸光度(self, data, context):
        return data.get('m3', '')
    
    def handle_水样吸光度(self, data, context):
        return data.get('m3', '')

    def handle_校正吸光度(self, data, context):
        return data.get('m1', '')
    
    def handle_挥发酚的浓度(self, data, context):
        return data.get('m1', '')
    
    def handle_平均值(self, data, context):
        return data.get('m3', '')
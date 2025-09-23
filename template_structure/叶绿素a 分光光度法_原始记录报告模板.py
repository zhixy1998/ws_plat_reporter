# 模板字段定义
# fill_type: 0 表示从模板中提取的字段, fill_type: 1 表示表格截取的字段

# get_type: 0: 表示从通用数据中取, 1: 表示从接口中取 2: 表从数据库中取

from .common_data import BaseTableDataHandler

python_template_var = {
    "湿度": {"fill_type": 0},
    "样品前处理2": {"fill_type": 0},
    "检测项目": {"fill_type": 0},
    "仪器编号": {"fill_type": 0},
    "检测依据": {"fill_type": 0},
    "计算公式": {"fill_type": 0},
    "表格1_rows": {"fill_type": 0},
    "备注": {"fill_type": 0},
    "温度": {"fill_type": 0},
    "分析日期": {"fill_type": 0},
    "仪器名称": {"fill_type": 0}
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
                "取样体积",
                "稀释倍数",
                "试样定容体积",
                "样品提取液体积",
                "平均值",
                "吸光值1",
                "吸光值2",
                "吸光值3",
                "吸光值4",
                "叶绿素试样",
                "叶绿素样品"
            ]
        ],
        "col_count": 12,
        "data_rows": [],
        "row_count": 0,
        "table_name": "表格1",
        "column_width": [
            2176,
            1843,
            1417,
            1200,
            1352,
            1151,
            1046,
            1110,
            1109,
            1110,
            1110,
            1177
        ],
        "structure_type": 0
    }
]



class TableDataHandler(BaseTableDataHandler):
    """表格数据处理类，用于处理数据映射和处理逻辑"""
    
    # 简单字段映射：表头名称 -> 数据库字段名
    HEADER_M_MAPPING = {
        "样品编号": "V6",  # 序号列
        "取样体积":"V6", 
        "稀释倍数":"V6", 
        "试样定容体积":"V6", 
        "样品提取液体积":"V6", 
        "吸光值":"V5",
        "吸光值1":"V5",  
        "吸光值2":"V6",
        "吸光值3":"V5",
        "吸光值4":"V5",
        "叶绿素a含量": "V5",
        "叶绿素试样":"V5",
        "叶绿素样品":"V7",
        "平均值":"V6"
    }

    TABLE_NAME_MAP = {
        '样品编号': '表格1',
        '取样体积': '表格1',
        '稀释倍数': '表格1',
        '试样定容体积': '表格1',
        '样品提取液体积': '表格1',
        "吸光值":"表格1",
        '吸光值1': '表格1',
        '吸光值2': '表格1',
        "吸光值3":"表格1",
        "吸光值4":"表格1",
        "叶绿素a含量": "表格1",
        "叶绿素试样":"表格1",
        "叶绿素样品":"表格1",
        "平均值":"表格1"
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
    
    def handle_取样体积(self, data, context):
        return data.get('m2', '')
    
    def handle_稀释倍数(self, data, context):
        return data.get('m3', '')
    
    def handle_吸光值2(self, data, context):
        return data.get('m3', '')
    
    def handle_吸光值3(self, data, context):
        return data.get('m3', '')
    
    def handle_吸光值4(self, data, context):
        return data.get('m3', '')
    
    def handle_叶绿素试样(self, data, context):
        return data.get('m3', '')
    
    def handle_叶绿素样品(self, data, context):
        return data.get('m3', '')
    
    def handle_平均值(self, data, context):
        return data.get('m3', '')
    def handle_试样定容体积(self, data, context):
        return data.get('m3', '')
    
    def handle_样品提取液体积(self, data, context):
        return data.get('m3', '')
    
    def handle_稀释倍数(self, data, context):
        return data.get('m3', '')
    
    def handle_吸光值1(self, data, context):
        return data.get
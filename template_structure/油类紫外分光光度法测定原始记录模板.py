# 模板字段定义
# fill_type: 0 表示从模板中提取的字段, fill_type: 1 表示表格截取的字段

# get_type: 0: 表示从通用数据中取, 1: 表示从接口中取 2: 表从数据库中取

from .common_data import BaseTableDataHandler

python_template_var = {
    "备注": {"fill_type": 0},
    "数据表格_rows": {"fill_type": 0}
}
table_fields = [
    {
        "has_tr": 1,
        "headers": [
            [
                "样品编号",
                "取样量",
                "稀释倍数",
                "本底加油标准的回收量平均值",
                "本底加分析空白的平均值",
                "油标准加入量",
                "萃取效率系数",
                "正己烷萃取液体积",
                "风干样的含水率",
                "从标准曲线查出油的浓度",
                "沉积物干样中油类的含量",
                "平均值",
                "吸光值空白",
                "吸光值样品",
                "吸光值平均"
            ]
        ],
        "col_count": 15,
        "data_rows": [],
        "row_count": 0,
        "table_name": "数据表格",
        "column_width": [
            2370,
            937,
            925,
            925,
            925,
            925,
            925,
            925,
            925,
            1014,
            836,
            938,
            925,
            925,
            925
        ],
        "structure_type": 0
    }
]
class TableDataHandler(BaseTableDataHandler):
    """表格数据处理类，用于处理数据映射和处理逻辑"""
    
    # 简单字段映射：表头名称 -> 数据库字段名
    HEADER_M_MAPPING = {
        "样品编号": "A1",  # 序号列
        "取样量": "V6",
        "稀释倍数":'V7',
        "本底加油标准的回收量平均值": 'A1',
        "本底加分析空白的平均值": 'A1',
        '油标准加入量': 'A1',
        '萃取效率系数': 'V5' ,  
        '正己烷萃取液体积': 'V5'  ,
        '风干样的含水率': 'V5',
        '吸光值空白': 'V5',
        '吸光值样品': 'V5',
        '吸光值平均': 'V5',
        '从标准曲线查出油的浓度': 'V5',
        '沉积物干样中油类的含量': 'V5',
        '平均值': 'V5'
    }

    TABLE_NAME_MAP = {
        "样品编号":'数据表格',  # 序号列
        "取样量": "数据表格",
        "稀释倍数":'数据表格',
        "本底加油标准的回收量平均值": '数据表格',
        "本底加分析空白的平均值": '数据表格',
        '油标准加入量': '数据表格',
        '萃取效率系数': '数据表格' ,  
        '正己烷萃取液体积': '数据表格'  ,
        '风干样的含水率': '数据表格',
        '吸光值空白': '数据表格',
        '吸光值样品': '数据表格',
        '吸光值平均': '数据表格',
        '从标准曲线查出油的浓度': '数据表格',
        '沉积物干样中油类的含量': '数据表格',
        '平均值': '数据表格'
    }

    TEMPLATE_INFO_MAP = {
        '数据表格': {
            'tpl_type': 2,   # 1: 每个单元格一个tpl对象，就是横向表格那种 2: 通过docxtpl循环语法渲染
            'column_count': None
        }
    }
    


    def __init__(self):
        # TABLE_NAME_MAP_REVERSE = {'数据表格': ['样品编号', '水样体积', '萃取液体积', 
        # '吸光度空白', '吸光度样品', '吸光度对比', '水中石油类的质量浓度', '平均值']}
        self.TABLE_NAME_MAP_REVERSE = {v: [k for k, v2 in self.TABLE_NAME_MAP.items() if v2 == v] for v in set(self.TABLE_NAME_MAP.values())}
    
    def handle_样品编号(self, data, context, row_index=0):
        return str(row_index + 1)
    
    def handle_取样量(self, data, context):
        return data.get('m2', '')
    
    def handle_稀释倍数(self, data, context):
        return data.get('m3', '')
    
    def handle_本底加油标准的回收量平均值(self, data, context):
        return data.get('m2', '')
    
    def handle_本底加分析空白的平均值(self, data, context):
        return data.get('m3', '')
    
    def handle_油标准加入量(self, data, context):
        return data.get('m4', '')
    
    def handle_萃取效率系数(self, data, context):
        return data.get('m5', '')
    
    def handle_正己烷萃取液体积(self, data, context):
        return data.get('m5', '')
    
    def handle_风干样的含水率(self, data, context):
        return data.get('m', '') 
    
    def handle_吸光值空白(self, data, context):
        return data.get('m5', '') 
    def handle_吸光值样品(self, data, context):
        return data.get('m6', '') 
    def handle_吸光值平均(self, data, context):
        return data.get('m5', '') 
    
    def handle_从标准曲线查出油的浓度(self, data, context):
        return data.get('m6', '') 
    
    def handle_沉积物干样中油类的含量(self, data, context):
        return data.get('m6', '') 
    
    def handle_平均值(self, data, context):
        return data.get('m3', '')

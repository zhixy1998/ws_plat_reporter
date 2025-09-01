# 模板字段定义
# fill_type: 0 表示从模板中提取的字段, fill_type: 1 表示表格截取的字段

# get_type: 0: 表示从通用数据中取, 1: 表示从接口中取 2: 表从数据库中取

python_template_var = {
    "数据表格_rows": {"fill_type": 0},
    "备注": {"fill_type": 0}
}
table_fields = [
    {
        "has_tr": 1,
        "headers": [
            [
                "样品编号", 
                "取样量", 
                "稀释倍数", 
                "试料的体积", 
                "校准曲线查得试料中六价铬的量", 
                "浸出液中六价铬的浓度",  
                "平均值",
                "吸光值空白_1",
                "吸光值空白_2",
                "吸光值空白_3"
            ]
        ],
        "col_count": 10,
        "data_rows": [],
        "row_count": 0,
        "table_name": "数据表格",
        "column_width": [
            2005,
            1842,
            1134,
            1985,
            1695,
            1725,
            1640,
            1108,
            1185,
            1140
        ],
        "structure_type": 0
    }
]
class TableDataHandler:
    """表格数据处理类，用于处理数据映射和处理逻辑"""
    
    # 简单字段映射：表头名称 -> 数据库字段名
    HEADER_M_MAPPING = {
        "样品编号": "A1",  # 序号列
        "取样量":"V6", 
        "稀释倍数":"V7", 
        "试料的体积":"V8", 
        "校准曲线查得试料中六价铬的量":"V5", 
        "浸出液中六价铬的浓度":"V5",  
        "平均值":"V6",
        "吸光值空白_1":"V5",
        "吸光值空白_2":"V5",
        "吸光值空白_3":"V5"
    }

    TABLE_NAME_MAP = {
        '样品编号': '数据表格',
        '取样量': '数据表格',
        '稀释倍数': '数据表格',
        '试料的体积': '数据表格',
        '校准曲线查得试料中六价铬的量': '数据表格',
        '浸出液中六价铬的浓度': '数据表格',
        '平均值': '数据表格',
        "吸光值空白_1":"数据表格",
        "吸光值空白_2":"数据表格",
        "吸光值空白_3":"数据表格"
    }

    TEMPLATE_INFO_MAP = {
            '数据表格': {
             'tpl_type': 2,   # 1: 每个单元格一个tpl对象，就是横向表格那种 2: 通过docxtpl循环语法渲染
             'column_count': None
            }
        }

    
    def __init__(self):
        # TABLE_NAME_MAP_REVERSE = {'数据表格': ['样品编号', '取样量', '稀释倍数', '试料的体积', '校准曲线查得试料中六价铬的量', '浸出液中六价铬的浓度', '平均值', '吸光值空白_1', '吸光值空白_2', '吸光值空白_3'试验吸光度', '水样吸光度', '标准曲线上氨氮质量', '水样氨氮质量浓度', '平均值']}
        self.TABLE_NAME_MAP_REVERSE = {v: [k for k, v2 in self.TABLE_NAME_MAP.items() if v2 == v] for v in set(self.TABLE_NAME_MAP.values())}
    
    def handle_样品编号(self, data, context, row_index=0):
        """处理序号列的逻辑"""
        return str(row_index + 1)
    
    def handle_取样量(self, data, context):
        """处理取样量列"""
        return data.get('m2', '')
    
    def handle_稀释倍数(self, data, context):
        """处理稀释倍数列"""
        return data.get('m3', '')

    def handle_试料的体积(self, data, context):
        """处理试料的体积列"""
        return data.get('m4', '')
    
    def handle_校准曲线查得试料中六价铬的量(self, data, context):
        """校准曲线查得试料中六价铬的量"""
        return data.get('m8', '')

    def handle_浸出液中六价铬的浓度(self, data, context):
        """浸出液中六价铬的浓度"""
        return data.get('m9', '')
    
    def handle_平均值(self, data, context):
        """平均值"""
        return data.get('m10', '')
    
    def handle_吸光值空白_1(self, data, context):
        """吸光值空白_1"""
        return data.get('m5', '')

    def handle_吸光值空白_2(self, data, context):
        """处理吸光值空白_2"""
        return data.get('m6', '')
    
    def handle_吸光值空白_3(self, data, context):
        """吸光值空白_3"""
        return data.get('m7', '')
    

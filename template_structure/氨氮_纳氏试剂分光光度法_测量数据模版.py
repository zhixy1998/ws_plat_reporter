# 模板字段定义
# fill_type: 0 表示从模板中提取的字段, fill_type: 1 表示表格截取的字段

# get_type: 0: 表示从通用数据中取, 1: 表示从接口中取 2: 表从数据库中取

python_template_var = {
    "数据表格_rows": {"fill_type": 0}
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
                "水样体积",
                "稀释倍数",
                "空白试验吸光度",
                "水样吸光度",
                "水样中氨氮质量浓度",
                "平均值"
            ]
        ],
        "col_count": 7,
        "data_rows": [],
        "row_count": 0,
        "table_name": "数据表格",
        "column_width": [
            2781,
            2217,
            2122,
            2112,
            2112,
            2112,
            2000
        ],
        "structure_type": 0
    }
]


class TableDataHandler:
    """表格数据处理类，用于处理数据映射和处理逻辑"""
    
    # 简单字段映射：表头名称 -> 数据库字段名
    HEADER_M_MAPPING = {
        "样品编号": "V5",  # 序号列
        "水样体积": "V6",
        "稀释倍数": "V7",
        "水样吸光度": "V8",
        "水样中氨氮质量浓度": "V5",
        "平均值": "V5",
        "空白试验吸光度": "V5"
    }

    TABLE_NAME_MAP = {
        '样品编号': '数据表格',
        '水样体积': '数据表格',
        '稀释倍数': '数据表格',
        '水样吸光度': '数据表格',
        '水样中氨氮质量浓度': '数据表格',
        '平均值': '数据表格',
        '空白试验吸光度': '数据表格'
    }

    TEMPLATE_INFO_MAP = {
            '数据表格': {
             'tpl_type': 2,   # 1: 每个单元格一个tpl对象，就是横向表格那种 2: 通过docxtpl循环语法渲染
             'column_count': None
            }
        }

    
    def __init__(self):
        # TABLE_NAME_MAP_REVERSE = {'数据表格': ['样品编号', '水样体积', '稀释倍数', '水样吸光度', '标准曲线上氨氮质量', '水样中氨氮质量浓度', '平均值']}
        self.TABLE_NAME_MAP_REVERSE = {v: [k for k, v2 in self.TABLE_NAME_MAP.items() if v2 == v] for v in set(self.TABLE_NAME_MAP.values())}
    
    def handle_样品编号(self, data, context, row_index=0):
        """处理序号列的逻辑"""
        return
    
    def handle_空白试验吸光度(self, data, context):
        """处理空白试验吸光度"""
        return
    
    def handle_水样体积(self, data, context):
        """处理检测时间和对应的吸光值列"""
        return
    
    def handle_稀释倍数(self, data, context):
        """处理T(min)列"""
        return

    def handle_水样吸光度(self, data, context):
        """处理T(min)列"""
        return
    
    def handle_水样中氨氮质量浓度(self, data, context):
        """处理T(min)列"""
        return
    
    def handle_平均值(self, data, context):
        """处理T(min)列"""
        return

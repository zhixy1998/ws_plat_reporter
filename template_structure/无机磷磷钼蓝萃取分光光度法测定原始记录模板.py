# 模板字段定义
# fill_type: 0 表示从模板中提取的字段, fill_type: 1 表示表格截取的字段

# get_type: 0: 表示从通用数据中取, 1: 表示从接口中取 2: 表从数据库中取

python_template_var = {
    "数据表格_rows": {"fill_type": 0},
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
                "样品总体积",
                "磷酸盐浓度",
                "平均值",
                "吸光值样品",
                "吸光值空白",
                "吸光值对比"
            ]
        ],
        "col_count": 7,
        "data_rows": [],
        "row_count": 0,
        "table_name": "数据表格",
        "column_width": [
            3436,
            2042,
            2043,
            2047,
            2043,
            2044,
            2043
        ],
        "structure_type": 0
    }
]

class TableDataHandler:
    """表格数据处理类，用于处理数据映射和处理逻辑"""
    
    # 简单字段映射：表头名称 -> 数据库字段名
    HEADER_M_MAPPING = {
        "样品编号": "A1",  # 序号列
        "样品总体积": "V6",
        "磷酸盐浓度":'V7',
        "平均值": 'A1',
        "吸光值样品": 'A1',
        '吸光度对比': 'A1',
        '吸光值空白': 'V5' 
    }

    TABLE_NAME_MAP = {
        "样品编号":'数据表格',  # 序号列
        "样品总体积": '数据表格',
        "磷酸盐浓度":'数据表格',
        "平均值": '数据表格',
        "吸光度样品": '数据表格',
        '吸光度对比': '数据表格',
        '吸光值空白': '数据表格'   
    }

    TEMPLATE_INFO_MAP = {
        '数据表格': {
            'tpl_type': 2,   # 1: 每个单元格一个tpl对象，就是横向表格那种 2: 通过docxtpl循环语法渲染
            'column_count': None
        }
    }
    


    def __init__(self):
        # TABLE_NAME_MAP_REVERSE = {'数据表格': ['样品编号', '样品总体积', '磷酸盐浓度', 
        # '平均值', '吸光度样品', '吸光度对比', '吸光值空白']}
        self.TABLE_NAME_MAP_REVERSE = {v: [k for k, v2 in self.TABLE_NAME_MAP.items() if v2 == v] for v in set(self.TABLE_NAME_MAP.values())}
    
    def handle_样品编号(self, data, context, row_index=0):
        return str(row_index + 1)
    
    def handle_样品总体积(self, data, context):
        return data.get('m2', '')
    
    def handle_磷酸盐浓度(self, data, context):
        return data.get('m3', '')
    def handle_吸光度空白(self, data, context):
        return data.get('m2', '')
    
    def handle_吸光度样品(self, data, context):
        return data.get('m3', '')
    
    def handle_吸光度对比(self, data, context):
        return data.get('m3', '')
    def handle_平均值(self, data, context):
        return data.get('m3', '')

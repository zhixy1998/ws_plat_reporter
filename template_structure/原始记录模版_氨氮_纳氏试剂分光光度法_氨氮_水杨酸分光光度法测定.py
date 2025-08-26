# 模板字段定义
# fill_type: 0 表示从模板中提取的字段, fill_type: 1 表示表格截取的字段

# get_type: 0: 表示从通用数据中取, 1: 表示从接口中取 2: 表从数据库中取

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
                "水样体积",
                "空白试验吸光度",
                "水样吸光度",
                "标准曲线上氨氮质量",
                "水样氨氮质量浓度",
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
        "样品编号": "m1",  # 序号列
        "水样体积": "m2",
        "空白试验吸光度": "m3",
        "水样吸光度": "m4",
        "标准曲线上氨氮质量": "m5",
        "水样氨氮质量浓度": "m6",
        "平均值": "m7"
    }

    TABLE_NAME = '数据表格'
    
    def __init__(self):
        pass
    
    def handle_样品编号(self, data, context, row_index=0):
        """处理序号列的逻辑"""
        return str(row_index + 1)
    
    def handle_水样体积(self, data, context):
        """处理检测时间和对应的吸光值列"""
        return data.get('m2', '')
    
    def handle_空白试验吸光度(self, data, context):
        """处理T(min)列"""
        return data.get('m3', '')

    def handle_水样吸光度(self, data, context):
        """处理T(min)列"""
        return data.get('m4', '')
    
    def handle_标准曲线上氨氮质量(self, data, context):
        """处理T(min)列"""
        return data.get('m5', '')

    def handle_水样氨氮质量浓度(self, data, context):
        """处理T(min)列"""
        return data.get('m6', '')
    
    def handle_平均值(self, data, context):
        """处理T(min)列"""
        return data.get('m7', '')
    
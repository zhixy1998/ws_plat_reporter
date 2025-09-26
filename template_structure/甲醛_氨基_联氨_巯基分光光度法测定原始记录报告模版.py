# 模板字段定义
# fill_type: 0 表示从模板中提取的字段, fill_type: 1 表示表格截取的字段

# get_type: 0: 表示从通用数据中取, 1: 表示从接口中取 2: 表从数据库中取
from .common_data import BaseTableDataHandler

python_template_var = {
    "b": {"fill_type": 0},
    "检测日期": {"fill_type": 0},
    "回归方程": {"fill_type": 0},
    "仪器编号": {"fill_type": 0},
    "检测依据": {"fill_type": 0},
    "前处理": {"fill_type": 0},
    "标准溶液及编号": {"fill_type": 0},
    "备注": {"fill_type": 0},
    "湿度": {"fill_type": 0},
    "计算公式": {"fill_type": 0},
    "溶液浓度": {"fill_type": 0},
    "温度": {"fill_type": 0},
    "表格2_rows": {"fill_type": 0},
    "a": {"fill_type": 0},
    "r": {"fill_type": 0},
    "表格_rows": {"fill_type": 0},
    "仪器名称": {"fill_type": 0},
    "检测项目": {"fill_type": 0}
}

# 表格字段分组
table_jinja_values = {
    '吸光度': ['吸光度_0', '吸光度_1', '吸光度_2', '吸光度_3', '吸光度_4', '吸光度_5', '吸光度_6', '吸光度_7'],
    '甲醛质量': ['甲醛质量_0', '甲醛质量_1', '甲醛质量_2', '甲醛质量_3', '甲醛质量_4', '甲醛质量_5', '甲醛质量_6', '甲醛质量_7']
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
                "甲醛质量"
            ],
            [
                "吸光度"
            ]
        ],
        "col_count": 2,
        "data_rows": [],
        "row_count": 0,
        "table_name": "表格1",
        "column_width": [
            2781,
            2781
        ],
        "structure_type": 1
    },
    {
        "has_tr": 1,
        "headers": [
            [
                "样品编号",
                "水样体积",
                "稀释倍数",
                "水样吸光度",
                "由标准曲线查得甲醛的质量",
                "水样中甲醛质量浓度",
                "平均值"
            ]
        ],
        "col_count": 7,
        "data_rows": [],
        "row_count": 0,
        "table_name": "表格2",
        "column_width": [
            2781,
            2112,
            2112,
            2112,
            2214,
            2010,
            2115
        ],
        "structure_type": 0
    },
    {
        "headers": [
            [
                "样品编号",
                "水样体积",
                "稀释倍数",
                "水样吸光度",
                "由标准曲线查得甲醛的质量",
                "水样中甲醛质量浓度",
                "平均值"
            ]
        ],
        "col_count": 7,
        "data_rows": [],
        "row_count": 0,
        "table_name": "表格",
        "column_width": [
            2781,
            2112,
            2112,
            2112,
            2245,
            1979,
            2115
        ],
        "structure_type": 0
    }
]


class TableDataHandler(BaseTableDataHandler):
    """表格数据处理类，用于处理数据映射和处理逻辑"""
    
    # 简单字段映射：表头名称 -> 数据库字段名
    HEADER_M_MAPPING = {
        "甲醛质量": "normalConcentration",  # 序号列
        "吸光度": "Abs",
        "样品编号": "sampleNumber",  # 序号列
        "水样体积": "2191OJP",
        "稀释倍数": "2191OJP",
        "水样吸光度": "Abs",
        "由标准曲线查得甲醛的质量": "V7",
        "水样中甲醛质量浓度": "2191OJP",
        "平均值": "2191OJP"
    }

    # TABLE_NAME_MAP = {
    #     '甲醛质量': '表格1',
    #     '吸光度': '表格1',

    #     '样品编号': '表格2',
    #     '水样体积': '表格2',
    #     '稀释倍数': '表格2',
    #     '水样吸光度': '表格2',
    #     '由标准曲线查得甲醛的质量': '表格2',
    #     '水样中甲醛质量浓度': '表格2',
    #     '平均值': '表格2',

    #     '样品编号': '表格',
    #     '水样体积': '表格',
    #     '稀释倍数': '表格',
    #     '水样吸光度': '表格',
    #     '由标准曲线查得甲醛的质量': '表格',
    #     '平均值': '表格',
    #     '水样中甲醛质量浓度': '表格'
    # }

    TEMPLATE_INFO_MAP = {
            '表格1': {
             'tpl_type': 1,   # 1: 每个单元格一个tpl对象，就是横向表格那种 2: 通过docxtpl循环语法渲染
             'column_count': 2
            },
            '表格2': {
             'tpl_type': 2,   # 1: 每个单元格一个tpl对象，就是横向表格那种 2: 通过docxtpl循环语法渲染
             'column_count': 7
            },
            '表格': {
             'tpl_type': 2,   # 1: 每个单元格一个tpl对象，就是横向表格那种 2: 通过docxtpl循环语法渲染
             'column_count': 7
            }
        }
    
    standard = ['甲醛质量', '吸光度']
    unknown = ['样品编号', '水样体积', '稀释倍数', '水样吸光度', '由标准曲线查得甲醛的质量', '水样中甲醛质量浓度', '平均值']

    TABLE_NAME_MAP_REVERSE = {
        '表格1': ['甲醛质量', '吸光度'],
        '表格2': ['样品编号', '水样体积', '稀释倍数', '水样吸光度', '由标准曲线查得甲醛的质量', '水样中甲醛质量浓度', '平均值'],
        '表格': ['样品编号', '水样体积', '稀释倍数', '水样吸光度', '由标准曲线查得甲醛的质量', '平均值', '水样中甲醛质量浓度']
    }

    
    def __init__(self):
        # TABLE_NAME_MAP_REVERSE = {'数据表格': ['样品编号', '水样体积', '由标准曲线查得甲醛的质量', '水样吸光度', '水样中甲醛质量浓度', '水样氨氮质量浓度', '平均值']}
        pass
    
    def handle_甲醛质量(self, data, m):
        real_header, sample_data = self.get_standard_head_and_data(data, m)
        return real_header, sample_data
    
    def handle_吸光度(self, data, m):
        real_header, sample_data = self.get_standard_head_and_data(data, m)
        return real_header, sample_data
    
    def handle_样品编号(self, data, m):
        """处理序号列的逻辑"""
        return
    
    def handle_水样体积(self, data, m):
        """处理检测时间和对应的吸光值列"""
        return
    
    def handle_稀释倍数(self, data, m):
        return
    
    def handle_空白试验吸光度(self, data, m):
        """处理T(min)列"""
        return

    def handle_水样吸光度(self, data, m):
        """处理T(min)列"""
        return
    
    def handle_标准曲线上氨氮质量(self, data, m):
        """处理T(min)列"""
        return

    def handle_平均值(self, data, m):
        """处理T(min)列"""
        return


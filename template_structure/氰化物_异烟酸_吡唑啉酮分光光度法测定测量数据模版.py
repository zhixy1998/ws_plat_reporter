# 模板字段定义
# fill_type: 0 表示从模板中提取的字段, fill_type: 1 表示表格截取的字段

# get_type: 0: 表示从通用数据中取, 1: 表示从接口中取 2: 表从数据库中取

from .common_data import BaseTableDataHandler

python_template_var = {
    "备注": {"fill_type": 0},
    "表格_rows": {"fill_type": 0}
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
                "预蒸馏的取样体积",
                "馏出液试样A的总体积V1",
                "测定所取试样A的体积V2",
                "试剂空白的吸光度",
                "试样的吸光度A",
                "氰化物质量浓度",
                "平均值"
            ]
        ],
        "col_count": 8,
        "data_rows": [],
        "row_count": 0,
        "table_name": "表格",
        "column_width": [
            2781,
            1810,
            1810,
            1810,
            1810,
            1810,
            1810,
            1815
        ],
        "structure_type": 0
    }
]



class TableDataHandler(BaseTableDataHandler):
    """表格数据处理类，用于处理数据映射和处理逻辑"""
    
    # 简单字段映射：表头名称 -> 数据库字段名
    HEADER_M_MAPPING = {
        "样品编号": "V5",  # 序号列
        "预蒸馏的取样体积": "V6",
        "馏出液试样A的总体积V1": "V7",
        "测定所取试样A的体积V2": "V8",
        "试剂空白的吸光度": "V5",
        "试样的吸光度A": "V5",
        "氰化物质量浓度": "V5",
        "平均值": "V5",
    }

    TABLE_NAME_MAP = {
        '样品编号': '表格',
        '预蒸馏的取样体积': '表格',
        '馏出液试样A的总体积V1': '表格',
        '测定所取试样A的体积V2': '表格',
        '试剂空白的吸光度': '表格',
        '试样的吸光度A': '表格',
        '氰化物质量浓度': '表格',
        '平均值': '表格'
    }

    TEMPLATE_INFO_MAP = {
            '表格': {
             'tpl_type': 2,   # 1: 每个单元格一个tpl对象，就是横向表格那种 2: 通过docxtpl循环语法渲染
             'column_count': 8
            }
        }

    
    def __init__(self):
        # TABLE_NAME_MAP_REVERSE = {'表格': ['样品编号', '预蒸馏的取样体积', '空白吸光度', '水样吸光度', '标准曲线上氨氮质量', '从标准曲线上查得的甲醛量', '平均值']}
        self.TABLE_NAME_MAP_REVERSE = {v: [k for k, v2 in self.TABLE_NAME_MAP.items() if v2 == v] for v in set(self.TABLE_NAME_MAP.values())}
    
    def handle_样品编号(self, data, context, row_index=0):
        """处理序号列的逻辑"""
        return
    
    def handle_预蒸馏的取样体积(self, data, context):
        """处理检测时间和对应的吸光值列"""
        return
    
    def handle_馏出液试样A的总体积V1(self, data, context):
        """处理T(min)列"""
        return

    def handle_测定所取试样A的体积V2(self, data, context):
        """处理T(min)列"""
        return
    
    def handle_试剂空白的吸光度(self, data, context):
        """处理T(min)列"""
        return
    
    def handle_试样的吸光度A(self, data, context):
        """处理T(min)列"""
        return
    
    def handle_氰化物质量浓度(self, data, context):
        """处理T(min)列"""
        return
    
    def handle_平均值(self, data, context):
        """处理T(min)列"""
        return


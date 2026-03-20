# 模板字段定义
# fill_type: 0 表示从模板中提取的字段, fill_type: 1 表示表格截取的字段

# get_type: 0: 表示从通用数据中取, 1: 表示从接口中取 2: 表从数据库中取

from .common_data import BaseTableDataHandler, checkbox
python_template_var = {
    "检测依据": {"fill_type": 0},
    "a": {"fill_type": 0},
    "检测项目": {"fill_type": 0},
    "未知样表格1_rows": {"fill_type": 0},
    "仪器名称": {"fill_type": 0},
    "计算公式": {"fill_type": 0},
    "未知样表格2_rows": {"fill_type": 0},
    "检测日期": {"fill_type": 0},
    "回归方程": {"fill_type": 0},
    "样品前处理": {"fill_type": 0},
    "b": {"fill_type": 0},
    "备注": {"fill_type": 0},
    "标准溶液及编号": {"fill_type": 0},
    "溶液浓度": {"fill_type": 0},
    "温度": {"fill_type": 0},
    "r": {"fill_type": 0},
    "仪器编号": {"fill_type": 0},
    "湿度": {"fill_type": 0}
}

# 表格字段分组
table_jinja_values = {
    '吸光度': ['吸光度_0', '吸光度_1', '吸光度_2', '吸光度_3', '吸光度_4', '吸光度_5', '吸光度_6'],
    '甲醛含量': ['甲醛含量_0', '甲醛含量_1', '甲醛含量_2', '甲醛含量_3', '甲醛含量_4', '甲醛含量_5', '甲醛含量_6']
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
                "甲醛含量"
            ],
            [
                "吸光度"
            ]
        ],
        "col_count": 2,
        "data_rows": [],
        "row_count": 0,
        "table_name": "已知样表格",
        "column_width": [
            2428,
            2428
        ],
        "structure_type": 1
    },
    {
        "has_tr": 1,
        "headers": [
            [
                "样品编号",
                "采样时体积",
                "分析时体积",
                "标准状况下的采样体积",
                "计算因子",
                "样品溶液吸光度",
                "试剂空白溶液吸光度",
                "甲醛浓度"
            ]
        ],
        "col_count": 8,
        "data_rows": [],
        "row_count": 0,
        "table_name": "未知样表格1",
        "column_width": [
            2428,
            1984,
            1985,
            1814,
            1810,
            1810,
            1810,
            1815
        ],
        "structure_type": 0
    },
    {
        "has_tr": 1,
        "headers": [
            [
                "样品编号",
                "采样时体积",
                "分析时体积",
                "标准状况下的采样体积",
                "计算因子",
                "样品溶液吸光度",
                "试剂空白溶液吸光度",
                "空气中甲醛浓度"
            ]
        ],
        "col_count": 8,
        "data_rows": [],
        "row_count": 0,
        "table_name": "未知样表格2",
        "column_width": [
            2570,
            2021,
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
        "甲醛含量": "Abs",
        "吸光度": "Abs",

        "样品编号": "V7",  # 序号列
        "采样时体积": "V7",
        "分析时体积": "V7",
        "标准状况下的采样体积": 'V7',
        "计算因子": 'V7',
        '样品溶液吸光度': 'V7',
        '试剂空白溶液吸光度': 'V7',
        '甲醛浓度': 'V7',
        '空气中甲醛浓度': 'V7',
    }

    TABLE_NAME_MAP_REVERSE = {
        '已知样表格': ['甲醛含量', '吸光度'],
        '未知样表格1': ['样品编号', '采样时体积', 
                '分析时体积', '标准状况下的采样体积', '计算因子',
                 '样品溶液吸光度','试剂空白溶液吸光度','甲醛浓度'],
        '未知样表格2': ['样品编号', '采样时体积', 
                '分析时体积', '标准状况下的采样体积', '计算因子',
                 '样品溶液吸光度','试剂空白溶液吸光度','空气中甲醛浓度'],   
    }

    TEMPLATE_INFO_MAP = {
        '已知样表格': {
            'tpl_type': 1,   # 1: 每个单元格一个tpl对象，就是横向表格那种 2: 通过docxtpl循环语法渲染
            'column_count': 7
        },
        '未知样表格1': {
            'tpl_type': 2,   # 1: 每个单元格一个tpl对象，就是横向表格那种 2: 通过docxtpl循环语法渲染
            'column_count': 8
        },
        '未知样表格2': {
            'tpl_type': 2,   # 1: 每个单元格一个tpl对象，就是横向表格那种 2: 通过docxtpl循环语法渲染
            'column_count': 8
        },
    }
    standard = ['甲醛含量', '吸光度']
    unknown = ['样品编号', '采样时体积', '分析时体积', '标准状况下的采样体积', '计算因子', 
                 '样品溶液吸光度','试剂空白溶液吸光度','甲醛浓度','空气中甲醛浓度']
    
    def __init__(self):
        pass
    
    def handle_甲醛含量(self, data, m):
        """处理甲醛含量"""
        real_header, sample_data = self.get_standard_head_and_data(data, m)
        return real_header, sample_data
    
    def handle_吸光度(self, data, m):
        """处理吸光度"""
        real_header, sample_data = self.get_standard_head_and_data(data, m)
        return real_header, sample_data
    
       
    #未知样表格
    def handle_样品编号(self, data, context, row_index=0):
        return str(row_index + 1)
    
    def handle_采样时体积(self, data, context):
        return data.get('m2', '')
    
    def handle_分析时体积 (self, data, context):
        return data.get('m3', '')
    
    def handle_标准状况下的采样体积(self, data, context):
        return data.get('m2', '')
    
    def handle_计算因子(self, data, context):
        return data.get('m3', '')
    
    def handle_样品溶液吸光度(self, data, context):
        return data.get('m4', '')

    def handle_试剂空白溶液吸光度(self, data, context):
        return data.get('m4', '')
    
    def handle_甲醛浓度(self, data, context):
        return data.get('m7', '')
    
    def handle_空气中甲醛浓度(self, data, context):
        return data.get('m8', '')
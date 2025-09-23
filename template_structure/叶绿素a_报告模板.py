# 模板字段定义
# fill_type: 0 表示从模板中提取的字段, fill_type: 1 表示表格截取的字段

# get_type: 0: 表示从通用数据中取, 1: 表示从接口中取 2: 表从数据库中取

from .common_data import BaseTableDataHandler

python_template_var = {
    "备注": {"fill_type": 0},
    "样品前处理2": {"fill_type": 0},
    "检测项目": {"fill_type": 0},
    "计算公式": {"fill_type": 0},
    "分析日期": {"fill_type": 0},
    "仪器编号": {"fill_type": 0},
    "仪器名称": {"fill_type": 0},
    "湿度": {"fill_type": 0},
    "温度": {"fill_type": 0},
    "检测依据": {"fill_type": 0}
}

# 字段渲染表格
custom_bookmark = {
    'project_name':'项目名称',
    'note':'备注',
}

table_fields = []




class TableDataHandler(BaseTableDataHandler):
    """表格数据处理类，用于处理数据映射和处理逻辑"""
    
    # 简单字段映射：表头名称 -> 数据库字段名
    HEADER_M_MAPPING = {

    }
    TABLE_NAME_MAP = {
 
    }

    TEMPLATE_INFO_MAP = {

    }
    


    def __init__(self):
        self.TABLE_NAME_MAP_REVERSE = {v: [k for k, v2 in self.TABLE_NAME_MAP.items() if v2 == v] for v in set(self.TABLE_NAME_MAP.values())}
    
    def handle_样品编号(self, data, context, row_index=0):
        return str(row_index + 1)
    
    def handle_水样体积(self, data, context):
        return data.get('m2', '')
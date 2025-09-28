# 模板字段定义
# fill_type: 0 表示从模板中提取的字段, fill_type: 1 表示表格截取的字段

# get_type: 0: 表示从通用数据中取, 1: 表示从接口中取 2: 表从数据库中取
from .common_data import BaseTableDataHandler
python_template_var = {
    "备注": {"fill_type": 0},
    "样品前处理": {"fill_type": 0},
    "a": {"fill_type": 0},
    "检测依据": {"fill_type": 0},
    "仪器名称": {"fill_type": 0},
    "grouped_data": {"fill_type": 0},
    "溶液浓度": {"fill_type": 0},
    "仪器编号": {"fill_type": 0},
    "回归方程": {"fill_type": 0},
    "b": {"fill_type": 0},
    "湿度": {"fill_type": 0},
    "标准溶液及编号": {"fill_type": 0},
    "计算公式": {"fill_type": 0},
    "温度": {"fill_type": 0},
    "检测日期": {"fill_type": 0},
    "r": {"fill_type": 0},
    "检测项目": {"fill_type": 0}
}

# 表格字段分组
table_jinja_values = {
    '吸光度': ['吸光度_0', '吸光度_1', '吸光度_2', '吸光度_3', '吸光度_4', '吸光度_5', '吸光度_6'],
    '硼含量': ['硼含量_0', '硼含量_1', '硼含量_2', '硼含量_3', '硼含量_4', '硼含量_5', '硼含量_6']
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
                "硼含量"
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
            2779,
            2779
        ],
        "structure_type": 1
    },
    {
        "has_tr": 1,
        "headers": [
            [
                "空白吸光度",
                "样品编号",
                "水样体积",
                "试样吸光度",
                "由校准曲线上查得的硼质量",
                "水样中硼的质量浓度",
                "平均值"
            ]
        ],
        "col_count": 7,
        "data_rows": [],
        "row_count": 0,
        "table_name": "表格2",
        "column_width": [
            2779,
            2779,
            2112,
            2112,
            2114,
            2112,
            2115
        ],
        "structure_type": 0
    },
    {
        "has_tr": 1,
        "headers": [
            [
                "样品编号",
                "水样体积",
                "空白吸光度",
                "试样吸光度",
                "由校准曲线上查得的硼质量",
                "水样中硼的质量浓度",
                "平均值"
            ]
        ],
        "col_count": 7,
        "data_rows": [],
        "row_count": 0,
        "table_name": "表格3",
        "column_width": [
            2781,
            2112,
            2112,
            2112,
            2112,
            2112,
            2115
        ],
        "structure_type": 0
    }
]

class TableDataHandler(BaseTableDataHandler):
    """表格数据处理类，用于处理数据映射和处理逻辑"""
    
    # 简单字段映射：表头名称 -> 数据库字段名
    HEADER_M_MAPPING = {
        "硼含量": "normalConcentration",  # 序号列
        "吸光度": "Abs",

        "样品编号": "V7",  # 序号列
        "平均值":"V7",
        "空白吸光度":"V7", 
        "水样体积":"V7", 
        "试样吸光度":"V8", 
        "由校准曲线上查得的硼质量":"V7", 
        "水样中硼的质量浓度":"V7",  
        
    }

    TABLE_NAME_MAP_REVERSE = {
        '表格1': ['硼含量', '吸光度'],
        '表格2': ['样品编号', '水样体积', '空白吸光度', '试样吸光度', '由校准曲线上查得的硼质量', '水样中硼的质量浓度', '平均值'],
        '表格3':['样品编号', '水样体积', '空白吸光度', '试样吸光度', '由校准曲线上查得的硼质量', '水样中硼的质量浓度', '平均值']
    }


    TEMPLATE_INFO_MAP = {
            '表格1': {
             'tpl_type': 1,   # 1: 每个单元格一个tpl对象，就是横向表格那种 2: 通过docxtpl循环语法渲染
             'column_count': 7
            },
            '表格2': {
             'tpl_type': 2,   # 1: 每个单元格一个tpl对象，就是横向表格那种 2: 通过docxtpl循环语法渲染
             'column_count': 7
            },
            '表格3': {
             'tpl_type': 2,   # 1: 每个单元格一个tpl对象，就是横向表格那种 2: 通过docxtpl循环语法渲染
             'column_count': 7
            },
        }
    
    standard = ['硼含量', '吸光度']
    unknown = ['样品编号', '水样体积', '空白吸光度', '试样吸光度', '由校准曲线上查得的硼质量', '水样中硼的质量浓度', '平均值']

    def __init__(self):
        # TABLE_NAME_MAP_REVERSE = {'小表格': ['氨氮含量', '吸光度', '校正吸光度']}
        pass
    
    def handle_硼含量(self, data, m):
        """处理序号列的逻辑"""
        real_header, sample_data = self.get_standard_head_and_data(data, m)
        return real_header, sample_data
    
    def handle_吸光度(self, data, m):
        """处理检测时间和对应的吸光值列"""
        real_header, sample_data = self.get_standard_head_and_data(data, m)
        return real_header, sample_data
    
    def handle_样品编号(self, data, context, row_index=0):
        """处理序号列的逻辑"""
        return str(row_index + 1)

    def handle_水样体积(self, data, context):
        """处理取水样体积"""
        return data.get('m2', '')
    
    def handle_空白吸光度(self, data, context):
        """处理空白吸光度列"""
        return data.get('m3', '')

    def handle_试样吸光度(self, data, context):
        """处理试样吸光度列"""
        return data.get('m4', '')
    
    def handle_由校准曲线上查得的硼质量(self, data, context):
        """校准曲线由校准曲线上查得的硼质量"""
        return data.get('m8', '')

    def handle_水样中硼的质量浓度(self, data, context):
        """水样中硼的质量浓度"""
        return data.get('m9', '')
    
    def handle_平均值(self, data, context):
        """平均值"""
        return data.get('m10', '')

    def group_table_data_for_merge(self, original_data, group_size=2):
        if not original_data:
            return {'grouped_data': [], 'original_data': []}

        grouped_data = []

        # 按group_size分组处理
        for i in range(0, len(original_data), group_size):
            group_rows = original_data[i:i + group_size]

            if not group_rows:
                continue
            
            # 从第一行提取需要合并的共同字段
            first_row = group_rows[0]

            # 构建分组信息
            group_info = {
                # 需要合并的三个字段：样品编号、稀释倍数、平均值
                '样品编号': first_row.get('样品编号', ''),
                '稀释倍数': first_row.get('稀释倍数', ''), 
                '平均值': first_row.get('平均值', ''),
                '水样体积': first_row.get('水样体积', ''),

                # 保留组内所有行的完整数据，供内层循环使用
                'rows': group_rows
            }

            grouped_data.append(group_info)

        return {
            'grouped_data': grouped_data,
            'original_data': original_data
        }


    def get_grouped_context_for_template(self, original_data, group_size=2):
        """
         为docxtpl模板准备分组上下文数据的便捷方法。
         此函数将原始数据按指定大小分组，并确保组内需要合并的字段值与第一个元素一致。
         Args:
             original_data (list): 原始单行数据列表，每个元素是一个字典。
             group_size (int): 分组大小，默认为2。
         Returns:
             dict: 可直接用于docxtpl.render()的上下文字典。
         """
        # key = ['表格2_rows','表格3rows']
        key = ['表格2_rows']
        if not original_data:
           return {
               'grouped_data': [],
               key: []
           }
        print(original_data)
        need_equal_filed =['样品编号', '水样体积', '平均值', '稀释倍数']
        for i in key:
            rows = original_data.get(i)
           # 1. 按 group_size 对数据进行分组
            grouped_list = [rows[i:i + group_size] for i in range(0, len(rows), group_size)]
           # 2. 遍历每个分组，统一需要合并的字段值
            for group in grouped_list:
               if not group:
                   continue
               
               # 获取该组的第一个元素作为参考
               first_item = group[0]
               # 从第二个元素开始遍历（如果存在）
               for i in range(1, len(group)):
                   current_item = group[i]
                   # 将需要统一的字段值设置成与第一个元素相同
                   for field in need_equal_filed:
                       if field in first_item:
                           current_item[field] = first_item[field]
           # 3. 调用现有的 group_table_data_for_merge 方法进行最终的结构转换
           # 注意：此时传入的 rows 列表已经被修改，其分组字段已对齐
            group_result = self.group_table_data_for_merge(rows, group_size)
            original_data['grouped_data'] = group_result['grouped_data']
            # original_data[f"{k}_grouped"] = group_result['grouped_data']
        print(original_data)
        return original_data 
    
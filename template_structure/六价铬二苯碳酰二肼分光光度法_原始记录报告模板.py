# 模板字段定义
# fill_type: 0 表示从模板中提取的字段, fill_type: 1 表示表格截取的字段

# get_type: 0: 表示从通用数据中取, 1: 表示从接口中取 2: 表从数据库中取

from .common_data import BaseTableDataHandler
python_template_var = {
    "r": {"fill_type": 0},
    "检测项目": {"fill_type": 0},
    "计算公式": {"fill_type": 0},
    "前处理": {"fill_type": 0},
    "a": {"fill_type": 0},
    "仪器名称": {"fill_type": 0},
    "标准溶液": {"fill_type": 0},
    "b": {"fill_type": 0},
    "备注": {"fill_type": 0},
    "仪器编号": {"fill_type": 0},
    "数据表格_rows": {"fill_type": 0},
    "湿度": {"fill_type": 0},
    "溶液浓度": {"fill_type": 0},
    "温度": {"fill_type": 0},
    "标准溶液及编号": {"fill_type": 0},
    "分析日期": {"fill_type": 0},
    "检测依据": {"fill_type": 0},
    "回归方程": {"fill_type": 0},
    "表格1_rows": {"fill_type": 0}
}

enable_table_grouping = True
# 表格字段分组
table_jinja_values = {
    '吸光值': ['吸光值_0', '吸光值_1', '吸光值_2', '吸光值_3', '吸光值_4', '吸光值_5', '吸光值_6', '吸光值_7', '吸光值_8']
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
                "吸光值"
            ]
        ],
        "col_count": 1,
        "data_rows": [],
        "row_count": 0,
        "table_name": "表格",
        "column_width": [
            3915
        ],
        "structure_type": 1
    },
    {
        "has_tr": 1,
        "headers": [
                "样品编号",            
                "取样量",            
                "稀释倍数",           
                "试料的体积",            
                "校准曲线查得试料中六价铬的量",            
                "浸出液中六价铬的浓度",            
                "平均值",            
                "吸光值空白",            
                "吸光值样品",            
                "吸光值平均"            
        ],
        "col_count": 10,
        "data_rows": [],
        "row_count": 0,
        "table_name": "表格1",
        "column_width": [
            1545,
            1546,
            1546,
            1546,
            1546,
            1546,
            1546,
            1546,
            1546,
            1546
        ],
        "structure_type": 0
    },
    {
        "has_tr": 1,
        "headers": [            
                "样品编号",            
                "取样量",           
                "稀释倍数",            
                "试料的体积",            
                "校准曲线查得试料中六价铬的量",            
                "浸出液中六价铬的浓度",           
                "平均值",            
                "吸光值空白",            
                "吸光值样品",
                "吸光值平均"            
        ],
        "col_count": 10,
        "data_rows": [],
        "row_count": 0,
        "table_name": "数据表格",
        "column_width": [
            2430,
            1417,
            1701,
            1418,
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


class TableDataHandler(BaseTableDataHandler):
    """表格数据处理类，用于处理数据映射和处理逻辑"""
    
    # 简单字段映射：表头名称 -> 数据库字段名
    HEADER_M_MAPPING = {
        "吸光值": "Abs",  
        "样品编号": "sampleNumber",  # 序号列
        "取样量":"2191OJP", 
        "稀释倍数":"2191OJP", 
        "试料的体积":"2191OJP", 
        "校准曲线查得试料中六价铬的量":"2191OJP", 
        "浸出液中六价铬的浓度":"fitConcentration",  
        "平均值":"2191OJP",
        "吸光值空白":"Abs",
        "吸光值样品":"2191OJP",
        "吸光值平均":"Abs"
    }

    TABLE_NAME_MAP_REVERSE = {
        '表格': ['吸光值'],
        '表格1': ['样品编号', '取样量', '稀释倍数', '试料的体积', '校准曲线查得试料中六价铬的量', '浸出液中六价铬的浓度',"吸光值空白", "吸光值样品","吸光值平均",'平均值'],
        '数据表格': ['样品编号', '取样量', '稀释倍数', '试料的体积', '校准曲线查得试料中六价铬的量', '浸出液中六价铬的浓度',"吸光值空白","吸光值样品", "吸光值平均",'平均值']
    }

    TEMPLATE_INFO_MAP = {
	  '数据表格': {
             'tpl_type': 2,   # 1: 每个单元格一个tpl对象，就是横向表格那种 2: 通过docxtpl循环语法渲染
             'column_count': 10
            },
      '表格1': {
             'tpl_type': 2,   # 1: 每个单元格一个tpl对象，就是横向表格那种 2: 通过docxtpl循环语法渲染
             'column_count': 10
            },
      '表格': {
            'tpl_type': 1,   # 1: 每个单元格一个tpl对象，就是横向表格那种 2: 通过docxtpl循环语法渲染
            'column_count': 9
        }
    }

    standard = ['吸光值']
    unknown = ['样品编号', '取样量', '稀释倍数', '试料的体积', '校准曲线查得试料中六价铬的量', '浸出液中六价铬的浓度',"吸光值空白", "吸光值样品","吸光值平均",'平均值']
    
    def __init__(self):
        # TABLE_NAME_MAP_REVERSE = {'表格': ['吸光值']}
        pass
    
    def handle_吸光值(self, data, m):
        """处理检测时间和对应的吸光值列"""
        real_header, sample_data = self.get_standard_head_and_data(data, m)
        return real_header, sample_data     
    
  
    def handle_样品编号(self, data, context):
        """处理样品编号列的逻辑"""
        return
    
    def handle_取样量(self, data, context):
        """处理取样量列"""
        return 
    
    def handle_稀释倍数(self, data, context):
        """处理稀释倍数列"""
        return 

    def handle_试料的体积(self, data, context):
        """处理试料的体积列"""
        return
    
    def handle_校准曲线查得试料中六价铬的量(self, data, context):
        """校准曲线查得试料中六价铬的量"""
        return 

    def handle_浸出液中六价铬的浓度(self, data, context):
        """浸出液中六价铬的浓度"""
        return
    
    def handle_平均值(self, data, context):
        """平均值"""
        return
    
    def handle_吸光值空白(self, data, context):
        """吸光值空白"""
        return
    
    def handle_吸光值样品(self, data, context):
        """吸光值样品"""
        return
    
    def handle_吸光值平均(self, data, context):
        """吸光值平均"""
        return
    
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
    #     为docxtpl模板准备分组上下文数据的便捷方法。
    #     此函数将原始数据按指定大小分组，并确保组内需要合并的字段值与第一个元素一致。
 
    #     Args:
    #         original_data (list): 原始单行数据列表，每个元素是一个字典。
    #         group_size (int): 分组大小，默认为2。
 
    #     Returns:
    #         dict: 可直接用于docxtpl.render()的上下文字典。
    #     """
         key = ['表格1_rows','数据表格_rows']
         if not original_data:
            return {
                'grouped_data': [],
                key: []
            }
         print(original_data)
         need_equal_filed = ['样品编号', '稀释倍数', '平均值']
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
         print(original_data)
         return original_data 
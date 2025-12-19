# 模板字段定义
# fill_type: 0 表示从模板中提取的字段, fill_type: 1 表示表格截取的字段

# get_type: 0: 表示从通用数据中取, 1: 表示从接口中取 2: 表从数据库中取

from .common_data import BaseTableDataHandler, checkbox
python_template_var = {
    "t10_t": {"fill_type": 0},
    "solution_concentration": {"fill_type": 0},
    "project": {"fill_type": 0},
    "r": {"fill_type": 0},
    "t11_t": {"fill_type": 0},
    "detection_basis_t": {"fill_type": 0},
    "sample_status_t": {"fill_type": 0},
    "calculation_formula_t": {"fill_type": 0},
    "standard_solution_number_t": {"fill_type": 0},
    "storage_condition": {"fill_type": 0},
    "regression_equation": {"fill_type": 0},
    "regression_equation_t": {"fill_type": 0},
    "project_t": {"fill_type": 0},
    "sample_status": {"fill_type": 0},
    "sample_preparation": {"fill_type": 0},
    "sample_preparation_t": {"fill_type": 0},
    "remark_t": {"fill_type": 0},
    "t2_t": {"fill_type": 0},
    "instrument_num": {"fill_type": 0},
    "calculation_formula": {"fill_type": 0},
    "rh": {"fill_type": 0},
    "t6_t": {"fill_type": 0},
    "b": {"fill_type": 0},
    "detection_basis": {"fill_type": 0},
    "known_sample_sub_table": {"fill_type": 0},
    "detection_time": {"fill_type": 0},
    "solution_concentration_t": {"fill_type": 0},
    "t3_t": {"fill_type": 0},
    "t9_t": {"fill_type": 0},
    "t4_t": {"fill_type": 0},
    "t": {"fill_type": 0},
    "storage_condition_t": {"fill_type": 0},
    "grouped_data": {"fill_type": 0},
    "standard_solution_number": {"fill_type": 0},
    "instrument_name": {"fill_type": 0},
    "t8_t": {"fill_type": 0},
    "remark": {"fill_type": 0},
    "instrument_name_t": {"fill_type": 0},
    "t7_t": {"fill_type": 0},
    "instrument_num_t": {"fill_type": 0},
    "a": {"fill_type": 0},
    "detection_time_t": {"fill_type": 0},
    "trh_t": {"fill_type": 0},
    "t1_t": {"fill_type": 0},
    "t5_t": {"fill_type": 0}
}

# 字段渲染表格
custom_bookmark = {
    'project_name':'项目名称',
    'note':'备注',
}

class TableDataHandler(BaseTableDataHandler):
    """表格数据处理类，用于处理数据映射和处理逻辑"""
    
    # 简单字段映射：表头名称 -> 数据库字段名
    HEADER_M_MAPPING = {
        "t1": "sampleNumber",  
        "t2":"2191OJP", 
        "t3":"2191OJP", 
        "t4":"2191OJP", 
        "t9":"2191OJP", 
        "t10":"fitConcentration",  
        "t11":"2191OJP",
        "t6":"Abs",
        "t7":"2191OJP",
        "t8":"Abs"
    }

    jinja_title_mapping = {
        't1_t': '样品编号',
        't2_t': '取样量M（   ）',
        't3_t': '稀释倍数f',
        't4_t': '试料的体积V（   ）',
        't5_t': '吸光值',
        't6_t': '空白A0（   ）',
        't7_t': '样品A（   ）',
        't8_t': 'A－A0（   ）',
        't9_t': '校准曲线查得试料中六价铬的量m（   ）',
        't10_t': '浸出液中六价铬的浓度c（   ）',
        't11_t': '平均值C\u0305（   ）'
    }

    
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
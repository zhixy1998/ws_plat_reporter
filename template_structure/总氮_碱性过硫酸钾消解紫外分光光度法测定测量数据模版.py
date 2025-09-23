# 模板字段定义
# fill_type: 0 表示从模板中提取的字段, fill_type: 1 表示表格截取的字段

# get_type: 0: 表示从通用数据中取, 1: 表示从接口中取 2: 表从数据库中取

from .common_data import BaseTableDataHandler

python_template_var = {
    "表格_rows": {"fill_type": 0},
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
                "试样体积",
                "稀释倍数",
                "空白试样吸光度",
                "试样吸光度",
                "试样中总氮的含量",
                "试样中总氮的质量浓度",
                "平均值",
                "空白试样吸光度_Ab1",
                "空白试样吸光度_Ab2",
                "空白试样吸光度_Ab",
                "试样吸光度_As1",
                "试样吸光度_As2",
                "试样吸光度_As"
            ]
        ],
        "col_count": 14,
        "data_rows": [],
        "row_count": 0,
        "table_name": "表格",
        "column_width": [
            2781,
            1267,
            1267,
            2931,
            2934,
            1425,
            1425,
            1426,
            977,
            977,
            977,
            977,
            977,
            980
        ],
        "structure_type": 0
    }
]




class TableDataHandler(BaseTableDataHandler):
    """表格数据处理类，用于处理数据映射和处理逻辑"""
    
    # 简单字段映射：表头名称 -> 数据库字段名
    HEADER_M_MAPPING = {
        "样品编号": "V5",  # 序号列
        "试样体积": "V6",
        "稀释倍数": "V7",
        "空白试样吸光度": "V8",
        "试样吸光度": "V5",
        "试样中总氮的含量": "V5",
        "试样中总氮的质量浓度": "V5",
        "平均值": "V5",
        "空白试样吸光度_Ab1": "V5",
        "空白试样吸光度_Ab2": "V5",
        "空白试样吸光度_Ab": "V5",
        "试样吸光度_As1": "V5",
        "试样吸光度_As2": "V5",
        "试样吸光度_As": "V5",
    }

    TABLE_NAME_MAP = {
        '样品编号': '表格',
        '试样体积': '表格',
        '稀释倍数': '表格',
        '空白试样吸光度': '表格',
        '试样吸光度': '表格',
        '试样中总氮的含量': '表格',
        '试样中总氮的质量浓度': '表格',
        '平均值': '表格',
        '空白试样吸光度_Ab1': '表格',
        '空白试样吸光度_Ab2': '表格',
        '空白试样吸光度_Ab': '表格',
        '试样吸光度_As1': '表格',
        '试样吸光度_As2': '表格',
        '试样吸光度_As': '表格',
    }

    TEMPLATE_INFO_MAP = {
            '表格': {
             'tpl_type': 2,   # 1: 每个单元格一个tpl对象，就是横向表格那种 2: 通过docxtpl循环语法渲染
             'column_count': 14
            }
        }

    
    def __init__(self):
        # TABLE_NAME_MAP_REVERSE = {'表格': ['样品编号', '试样体积', '空白吸光度', '水样吸光度', '标准曲线上氨氮质量', '从标准曲线上查得的甲醛量', '平均值']}
        self.TABLE_NAME_MAP_REVERSE = {v: [k for k, v2 in self.TABLE_NAME_MAP.items() if v2 == v] for v in set(self.TABLE_NAME_MAP.values())}
    
    def handle_样品编号(self, data, context, row_index=0):
        """处理序号列的逻辑"""
        return
    
    def handle_试样体积(self, data, context):
        """处理检测时间和对应的吸光值列"""
        return

    def handle_稀释倍数(self, data, context):
        """处理检测时间和对应的吸光值列"""
        return
    
    def handle_空白试样吸光度(self, data, context):
        """处理检测时间和对应的吸光值列"""
        return    
    
    def handle_试样吸光度(self, data, context):
        """处理检测时间和对应的吸光值列"""
        return    

    def handle_试样中总氮的含量(self, data, context):
        """处理检测时间和对应的吸光值列"""
        return    
    
    def handle_试样中总氮的质量浓度(self, data, context):
        """处理检测时间和对应的吸光值列"""
        return    
    
    def handle_平均值(self, data, context):
        """处理T(min)列"""
        return
    
    def handle_空白试样吸光度_Ab1(self, data, context):
        """处理T(min)列"""
        return
    
    def handle_空白试样吸光度_Ab2(self, data, context):
        """处理T(min)列"""
        return    
    
    def handle_空白试样吸光度_Ab(self, data, context):
        """处理T(min)列"""
        return    
    
    def handle_试样吸光度_As1(self, data, context):
        """处理T(min)列"""
        return    
    
    def handle_试样吸光度_As2(self, data, context):
        """处理T(min)列"""
        return    
    
    def handle_试样吸光度_As(self, data, context):
        """处理T(min)列"""
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
            # 需要合并的字段（组级别字段）
            '空白试样吸光度_Ab1': first_row.get('空白试样吸光度_Ab1', ''),
            '空白试样吸光度_Ab2': first_row.get('空白试样吸光度_Ab2', ''),
            '空白试样吸光度_Ab': first_row.get('空白试样吸光度_Ab', ''),
            # 组内所有行
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
        key = '表格_rows'
        if not original_data:
            return {
                'grouped_data': [],
                key: []
            }

        need_equal_filed = ['空白试样吸光度_Ab1', '空白试样吸光度_Ab2', '空白试样吸光度_Ab']
        rows = original_data.get(key)
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
        return original_data


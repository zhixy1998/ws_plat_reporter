# 模板字段定义
# fill_type: 0 表示从模板中提取的字段, fill_type: 1 表示表格截取的字段

# get_type: 0: 表示从通用数据中取, 1: 表示从接口中取 2: 表从数据库中取

python_template_var = {
    "数据表格_rows": {"fill_type": 0},
    "备注": {"fill_type": 0}
}
enable_table_grouping = True

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
                "水样体积",
                "稀释倍数",
                "测定值",
                "平均值",
                "吸光值空白",
                "吸光值样品",
                "吸光值水样平均",
                "吸光值浊度"
            ]
        ],
        "col_count": 9,
        "data_rows": [],
        "row_count": 0,
        "table_name": "数据表格",
        "column_width": [
            3434,
            1520,
            1275,
            1695,
            1695,
            1563,
            1516,
            1516,
            1484
        ],
        "structure_type": 1
    }
]

class TableDataHandler:
    """表格数据处理类，用于处理数据映射和处理逻辑"""
    
    # 简单字段映射：表头名称 -> 数据库字段名
    HEADER_M_MAPPING = {
        "样品编号": "A1",  # 序号列
        "水样体积":"V6", 
        "稀释倍数":"V7", 
        "测定值":"V8", 
        "平均值":"V5", 
        "吸光值空白":"V5",  
        "吸光值样品":"V5",
        "吸光值水样平均":"V5",
        "吸光值浊度":"V5"
    }

    TABLE_NAME_MAP = {
        '样品编号': '数据表格',
        '水样体积': '数据表格',
        '稀释倍数': '数据表格',
        '测定值': '数据表格',
        '平均值': '数据表格',
        '吸光值空白': '数据表格',
        "吸光值样品":"数据表格",
        "吸光值水样平均":"数据表格",
        "吸光值浊度":"数据表格"
    }

    TEMPLATE_INFO_MAP = {
            '数据表格': {
             'tpl_type': 2,   # 1: 每个单元格一个tpl对象，就是横向表格那种 2: 通过docxtpl循环语法渲染
             'column_count': None
            }
        }

    
    def __init__(self):
        # TABLE_NAME_MAP_REVERSE = {'数据表格': ['样品编号', '水样体积', '稀释倍数', '测定值', '平均值', '吸光值空白',  "吸光值样品","吸光值水样平均","吸光值浊度"]}
        self.TABLE_NAME_MAP_REVERSE = {v: [k for k, v2 in self.TABLE_NAME_MAP.items() if v2 == v] for v in set(self.TABLE_NAME_MAP.values())}
    
    def handle_样品编号(self, data, context, row_index=0):
        """处理序号列的逻辑"""
        return str(row_index + 1)
    
    def handle_水样体积(self, data, context):
        """处理水样体积列"""
        return data.get('m2', '')
    
    def handle_稀释倍数(self, data, context):
        """处理稀释倍数列"""
        return data.get('m3', '')

    def handle_测定值(self, data, context):
        """处理测定值"""
        return data.get('m4', '')
    
    def handle_平均值(self, data, context):
        """平均值"""
        return data.get('m8', '')

    def handle_吸光值空白(self, data, context):
        """土壤样品的干物质含量"""
        return data.get('m9', '')
    
    def handle_吸光值样品(self, data, context):
        """吸光值样品"""
        return data.get('m5', '')
    
    def handle_吸光值水样平均(self, data, context):
        """吸光值水样平均"""
        return data.get('m7', '')
    
    def handle_吸光值浊度(self, data, context):
        """吸光值浊度"""
        return data.get('m6', '')
    
    def group_table_data_for_merge(self, original_data, group_size=2):
        """
        将单行数据按指定大小分组，用于docxtpl模板中的单元格合并
        
        功能说明：
        - 将原始的单行数据列表按group_size分组（默认3行一组）
        - 提取每组中相同的字段（样品编号、稀释倍数、平均值）用于合并显示
        - 保留每行独特的字段（取样量、各种吸光值、测定值）用于正常显示        
       
        
        使用场景：
        - 在docxtpl模板中使用 {%tr for group in grouped_data %} 进行外层循环
        - 使用 {%tr for row in group.rows %} 进行内层循环
        - 使用 {% if loop.first %}{{ group.样品编号 }}{% else %}{% vm %}{% endif %} 实现合并
        
        示例：
            原始数据6行 -> 分为2组，每组3行
            第1组：A001样品的3次测定
            第2组：B002样品的3次测定
            样品编号、稀释倍数、平均值在每组内合并显示
        """
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
                # 需要合并的三个字段：样品编号、稀释倍数、吸光值水样平均、测定值、平均值
                '样品编号': first_row.get('样品编号', ''),
                '稀释倍数': first_row.get('稀释倍数', ''), 
                '吸光值水样平均': first_row.get('吸光值水样平均', ''), 
                '测定值': first_row.get('测定值', ''), 
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
        为docxtpl模板准备分组上下文数据的便捷方法
        
        Args:
            original_data (list): 原始单行数据列表
            group_size (int): 分组大小，默认3行一组
            
        Returns:
            dict: 可直接用于docxtpl.render()的上下文字典
        """
        original_data = [
            # 第1组 (行1-2) - 样品A001
            {'样品编号': 'A001', '水样体积': '10ml', '稀释倍数': '1:10', '吸光值空白': '1','吸光值样品': '1','吸光值水样平均': '1','吸光值浊度': '0.001', '测定值': '0.123', '平均值': '1.25'},
            {'样品编号': 'A001', '水样体积': '20ml', '稀释倍数': '1:10', '吸光值空白': '2','吸光值样品': '1','吸光值水样平均': '1','吸光值浊度': '0.003', '测定值': '0.145', '平均值': '1.25'},

            # 第1组 (行3-4) - 样品A002
            {'样品编号': 'A002', '水样体积': '15ml', '稀释倍数': '1:20', '吸光值空白': '3','吸光值样品': '1','吸光值水样平均': '1','吸光值浊度': '0.002', '测定值': '0.134', '平均值': '1.8'},
            {'样品编号': 'A002', '水样体积': '12ml', '稀释倍数': '1:20', '吸光值空白': '4','吸光值样品': '1','吸光值水样平均': '1','吸光值浊度': '0.002', '测定值': '0.189', '平均值': '1.8'},

            # 第2组 (行5-6) - 样品B001
            {'样品编号': 'B001', '水样体积': '18ml', '稀释倍数': '1:30', '吸光值空白': '5','吸光值样品': '1','吸光值水样平均': '1','吸光值浊度': '0.004', '测定值': '0.201', '平均值': '2.5'},
            {'样品编号': 'B001', '水样体积': '25ml', '稀释倍数': '1:30', '吸光值空白': '6','吸光值样品': '1','吸光值水样平均': '1','吸光值浊度': '0.003', '测定值': '0.195', '平均值': '2.5'},

        ]
        group_result = self.group_table_data_for_merge(original_data, group_size)
        print(group_result['grouped_data'])
        return {
            # docxtpl模板中使用的变量名
            'grouped_data': group_result['grouped_data'],
            '数据表格_rows': group_result['original_data']  # 保持原有变量名兼容性
        }


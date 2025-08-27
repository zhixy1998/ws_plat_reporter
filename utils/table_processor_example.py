"""
表格数据处理器使用示例
演示如何使用 TableDataProcessor 来处理表格数据
"""
from utils.table_data_processor import TableDataProcessor


def example_usage():
    """使用示例"""
    
    # 1. 创建表格数据处理器实例
    processor = TableDataProcessor('光度测量报告模版_test')
    
    # 2. 模拟一些测试数据
    test_data = [
        {
            'm1': '1',
            'm2': '2023-08-22 10:00:00',
            'm3': '5.0',
            'm4': '0.85',
            'm5': '0.82',
            'm6': '0.83'
        },
        {
            'm1': '2', 
            'm2': '2023-08-22 10:05:00',
            'm3': '10.0',
            'm4': '0.87',
            'm5': '0.84',
            'm6': '0.85'
        }
    ]
    
    # 3. 处理表格数据
    table_name = "光度测量表格"
    processed_data = processor.process_table_data(table_name, test_data)
    
    # 4. 输出结果
    print("处理后的表格数据:")
    for row in processed_data:
        print(row)
    
    # 5. 查看可用的处理方法
    print("\n可用的处理方法:")
    handlers = processor.list_available_handlers()
    for handler in handlers:
        print(f"  - {handler}")
    
    # 6. 查看列映射配置
    print("\n列映射配置:")
    mapping = processor.get_HEADER_M_MAPPING()
    for header, field in mapping.items():
        print(f"  '{header}' -> '{field}'")


if __name__ == "__main__":
    example_usage()

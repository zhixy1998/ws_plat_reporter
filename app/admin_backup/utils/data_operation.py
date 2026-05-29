import json
from datetime import datetime

from app.db import execute_safe_sql_classic, execute_safe_sql
db_name = 'classic_db'

class DataOperation():

    method_key = None 

    def __init__(self, task_id):
        self.task_id = task_id
        self.sample_key_list = []
        self.project_item_key = None

    @staticmethod
    def build_measure_table_name(table_prefix, table_suffix):
        return f'{table_prefix}measure_{table_suffix}'

    async def get_measure_task_info(self, table_prefix='f_t_', sql_executor=execute_safe_sql_classic):
        table_name = self.build_measure_table_name(table_prefix, 'task')
        sql_text = """
            select * from {table_name} where id = %s and is_delete = 0;
        """.format(table_name=table_name)
        sql_result = await sql_executor(sql_text, [self.task_id], return_dict=True)
        if len(sql_result) == 1:
            self.method_key = sql_result[0].get('method_key')
            self.project_item_key = sql_result[0].get('project_item_key')
            if sql_result[0].get('sample_key'):
                sample_key = json.loads(sql_result[0].get('sample_key'))
                for item in sample_key:
                    self.sample_key_list.append(item.get('specimenKey'))
        return sql_result

    async def get_measure_analysis_data_info(self, table_prefix='f_t_', sql_executor=execute_safe_sql_classic):
        table_name = self.build_measure_table_name(table_prefix, 'analysis_data')
        sql_text = """
            select * from {table_name} where task_id = %s and is_delete = 0;
        """.format(table_name=table_name)
        sql_result = await sql_executor(sql_text, [self.task_id], return_dict=True)
        return sql_result

    async def get_measure_data_info(self, table_prefix='f_t_', sql_executor=execute_safe_sql_classic):
        table_name = self.build_measure_table_name(table_prefix, 'data')
        sql_text = """
            select * from {table_name} where task_id = %s and is_delete = 0;
        """.format(table_name=table_name)
        sql_result = await sql_executor(sql_text, [self.task_id], return_dict=True)
        return sql_result
    
    async def get_measure_method_info(self, table_prefix='f_t_', sql_executor=execute_safe_sql_classic):
        table_name = self.build_measure_table_name(table_prefix, 'method')
        sql_text = """
            select * from {table_name} where id = %s;
        """.format(table_name=table_name)
        sql_result = await sql_executor(sql_text, [self.method_key], return_dict=True)
        return sql_result
    
    async def get_measure_sample_info(self, table_prefix='f_t_', sql_executor=execute_safe_sql_classic):
        if not self.sample_key_list:
            return []

        table_name = self.build_measure_table_name(table_prefix, 'sample')
        placeholders = ','.join(['%s'] * len(self.sample_key_list))
        sql_text = f"select * from {table_name} where id in ({placeholders});"
        sql_result = await sql_executor(sql_text, self.sample_key_list, return_dict=True)
        return sql_result
    
    async def get_measure_task_attachment_info(self, table_prefix='f_t_', sql_executor=execute_safe_sql_classic):
        table_name = self.build_measure_table_name(table_prefix, 'task_attachment')
        sql_text = """
            select * from {table_name} where task_id = %s;
        """.format(table_name=table_name)
        sql_result = await sql_executor(sql_text, [self.task_id], return_dict=True)
        return sql_result   
    
    async def get_measure_project_info(self, table_prefix='f_t_', sql_executor=execute_safe_sql_classic):
        table_name = self.build_measure_table_name(table_prefix, 'project')
        sql_text = """
            select * from {table_name} where id = %s and is_delete = 0;
        """.format(table_name=table_name)
        sql_result = await sql_executor(sql_text, [self.project_item_key], return_dict=True)
        return sql_result
    
    @staticmethod
    async def insert_data(decrypt_data, user_name, user_id):
        task_data = decrypt_data.get('task_data', {})
        method_data = decrypt_data.get('method_data', {})

        if task_data:
            for _task_id, database_data_mapping in decrypt_data.get('task_data').items():
                for database_name, data_list in database_data_mapping.items():
                    if database_name == 'f_t_measure_task' and data_list:
                        data_list[0]['user_id'] = user_id
                    sql, all_params, data_ids = DataOperation.insert_data_sql(database_name, data_list)
                    if not sql:
                        continue
                    print(f"Executing: INSERT/UPDATE into {database_name} with ID: {data_ids}")
                    for params in all_params:
                        await execute_safe_sql_classic(sql, params)
        if method_data: 
            for database_name, data_list in decrypt_data.get('method_data').items():
                for data in data_list:
                    data['method_creator'] = user_name
                sql, all_params, data_ids = DataOperation.insert_data_sql(database_name, data_list)
                print(f"Executing: INSERT/UPDATE into {database_name} with ID: {data_ids}")
                if not sql:
                    continue
                for params in all_params:
                    await execute_safe_sql_classic(sql, params)
        return True
    
    @staticmethod
    async def insert_data_guide(decrypt_data):
        method_data = decrypt_data.get('method_data', {})
        task_data = decrypt_data.get('task_data', {})
        if task_data:
            for _task_id, database_data_mapping in task_data.items():
                for database_name, data_list in database_data_mapping.items():
                    sql, all_params, data_ids = DataOperation.insert_data_sql(database_name, data_list)
                    if not sql:
                        continue
                    print(f"Executing: INSERT/UPDATE into {database_name} with ID: {data_ids}")
                    for params in all_params:
                        await execute_safe_sql(sql, params)
        if method_data:
            for database_name, data_list in method_data.items():
                sql, all_params, data_ids = DataOperation.insert_data_sql(database_name, data_list)
                if not sql:
                    continue
                print(f"Executing: INSERT/UPDATE into {database_name} with ID: {data_ids}")
                for params in all_params:
                    await execute_safe_sql(sql, params)
        return True
        
        
    
    @staticmethod
    def insert_data_sql(database_name, data_list):
        data_ids = []
        all_params_list = []
        if not data_list:
            return None, [], []
        
        # 假设所有行字典的键是相同的 (即字段名)
        first_row = data_list[0]
        
        # 1. 提取字段名 (Keys)
        fields = first_row.keys()
        
        # 2. 构造 SQL 语句的各个部分
        field_list_sql = ", ".join(f"`{f}`" for f in fields) # 字段名列表 (用反引号确保字段名合法)
        placeholder_list = ", ".join(["%s"] * len(fields)) # %s 占位符列表
        
        # 构造 ON DUPLICATE KEY UPDATE 部分
        update_clauses = []
        for f in fields:
            if f.lower() != 'id': # 假设 ID 是主键，跳过更新 ID 自身
                update_clauses.append(f"`{f}` = VALUES(`{f}`)") # VALUES() 获取新值
        
        update_clause_sql = ", ".join(update_clauses)
        
        # 构造最终的 SQL
        # 注意：此处假设您的数据库支持 INSERT ... ON DUPLICATE KEY UPDATE (如 MySQL)
        sql = f"""
            INSERT INTO `{database_name}` ({field_list_sql}) 
            VALUES ({placeholder_list})
            ON DUPLICATE KEY UPDATE {update_clause_sql}
        """
        
        # 3. 准备执行参数 (逐行插入)
        
        # Tortoise ORM 的 execute_query 一次只能执行一条 SQL 语句
        for data_base_dict in data_list:
            # 提取参数值，并进行格式化处理 (尤其是 datetime)
            params = []
            for field in fields:
                value = data_base_dict.get(field)

                # 1. 处理 None
                if value is None:
                    params.append(None)
    
                # 2. 核心修复：如果是字典或列表，必须转为 JSON 字符串 (双引号)
                elif isinstance(value, (dict, list)):
                    # ensure_ascii=False 保证中文不乱码
                    # default=str 兜底处理里面可能包含的特殊对象
                    params.append(json.dumps(value, ensure_ascii=False, default=str))
        
                # 3. 处理时间类型 (转为字符串)
                elif isinstance(value, datetime):
                    params.append(value.strftime('%Y-%m-%d %H:%M:%S'))
        
                # 4. 处理布尔值 (MySQL 有时需要转为 0/1，视驱动而定，通常直接传也可以)
                elif isinstance(value, bool):
                    params.append(int(value))
        
                # 5. 其他类型 (str, int, float) 直接添加
                else:
                    params.append(value)
            all_params_list.append(params)
            data_ids.append(data_base_dict.get('id'))
            
                # 4. 执行 SQL
        return sql, all_params_list, data_ids
        
    
    
    @staticmethod
    async def static_method_get_measure_method_info(method_key_list, table_prefix='f_t_', sql_executor=execute_safe_sql_classic):
        if not method_key_list:
            return []

        table_name = DataOperation.build_measure_table_name(table_prefix, 'method')
        placeholders = ','.join(['%s'] * len(method_key_list))
        sql_text = f"""
            select * from {table_name} where id in ({placeholders});
        """
        sql_result = await sql_executor(sql_text, method_key_list, return_dict=True)
        return sql_result
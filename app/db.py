import os
from dotenv import load_dotenv
from tortoise import Tortoise
from config import config
"""
# 第一次初始化
aerich init -t app.db.TORTOISE_ORM

# 初始建表
aerich init-db

# 修改模型后
aerich migrate 生成迁移文件
aerich upgrade 应用迁移文件

"""

load_dotenv(override=True)


TORTOISE_ORM = {
    "connections": {
        "default": config.database_url, 
        "classic_db": config.classic_database_url
    },
    
    "apps": {
        "models": {  # 只需要一套模型，用 .using_db() 来区分数据库
            "models": [
                "app.template_doc.model",   # 一套模型，两个数据库都用
                "aerich.models"             # Aerich 迁移系统必需
            ],
            "default_connection": "default"
        }
    }
}

async def init_db():
    await Tortoise.init(config=TORTOISE_ORM)
    await Tortoise.generate_schemas()


async def execute_safe_sql(sql: str, params: list = None, return_dict: bool = False, connection=None):
    """
    安全执行 SQL，支持参数绑定防止 SQL 注入

    :param sql: SQL 语句，参数用 %s 占位
    :param params: 参数列表
    :param return_dict: 是否返回字段名对应的 dict（用于 SELECT）
    :return: 查询类返回 (rows, description)，其他返回 None

    # 查询
    sql = "SELECT * FROM template_bookmark WHERE template_doc_id = %s"
    result = await execute_safe_sql(sql, [19], return_dict=True)
    print(result)

    # 删除
    sql = "DELETE FROM template_bookmark WHERE template_doc_id = %s"
    await execute_safe_sql(sql, [19])

    # 插入
    sql = "INSERT INTO template_bookmark (template_doc_id, name) VALUES (%s, %s)"
    await execute_safe_sql(sql, [19, "新书签"])

    """
    conn = connection
    if conn is None:
        conn = Tortoise.get_connection("default")
    if params is None:
        params = []

    if sql.strip().lower().startswith("select"):
        if return_dict:
            return await conn.execute_query_dict(sql, params)
        else:
            return await conn.execute_query(sql, params)
    else:
        await conn.execute_query(sql, params)
        return None


async def execute_safe_sql(sql: str, params: list = None, return_dict: bool = False, connection=None):
    """
    安全执行 SQL，支持参数绑定防止 SQL 注入

    :param sql: SQL 语句，参数用 %s 占位
    :param params: 参数列表
    :param return_dict: 是否返回字段名对应的 dict（用于 SELECT）
    :return: 查询类返回 (rows, description)，其他返回 None

    # 查询
    sql = "SELECT * FROM template_bookmark WHERE template_doc_id = %s"
    result = await execute_safe_sql(sql, [19], return_dict=True)
    print(result)

    # 删除
    sql = "DELETE FROM template_bookmark WHERE template_doc_id = %s"
    await execute_safe_sql(sql, [19])

    # 插入
    sql = "INSERT INTO template_bookmark (template_doc_id, name) VALUES (%s, %s)"
    await execute_safe_sql(sql, [19, "新书签"])

    """
    conn = connection
    if conn is None:
        conn = Tortoise.get_connection("default")
    if params is None:
        params = []

    if sql.strip().lower().startswith("select"):
        if return_dict:
            return await conn.execute_query_dict(sql, params)
        else:
            return await conn.execute_query(sql, params)
    else:
        await conn.execute_query(sql, params)
        return None


async def execute_safe_sql_classic(sql: str, params: list = None, return_dict: bool = False, conn=None):
    """
    专门用于 classic_db 数据库的安全 SQL 执行函数
    
    :param sql: SQL 语句，参数用 %s 占位
    :param params: 参数列表
    :param return_dict: 是否返回字段名对应的 dict（用于 SELECT）
    :return: 查询类返回 (rows, description)，其他返回 None
    
    使用示例：
    # 查询 classic_db
    result = await execute_safe_sql_classic("SELECT * FROM template_doc WHERE id = %s", [1], return_dict=True)
    
    # 插入 classic_db
    await execute_safe_sql_classic("INSERT INTO template_doc (name) VALUES (%s)", ["测试模板"])
    """
    if conn is None:
        conn = Tortoise.get_connection("classic_db")
    if params is None:
        params = []

    if sql.strip().lower().startswith("select"):
        if return_dict:
            return await conn.execute_query_dict(sql, params)
        else:
            return await conn.execute_query(sql, params)
    else:
        await conn.execute_query(sql, params)
        return None
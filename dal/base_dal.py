# -*- coding: utf-8 -*-
from tortoise import Tortoise
from pydantic import BaseModel
from tortoise.exceptions import DoesNotExist, MultipleObjectsReturned
from tortoise import connections
from app.db import execute_safe_sql, execute_safe_sql_classic



class BaseDal(object):
    def __init__(self, model):
        self.model = model

    async def create_one_obj(self, create_info, db_select=None,** kwargs):
        """
        创建数据
        :param create_info:
        :return: dict
        """
        create_info = create_info if isinstance(create_info, dict) else dict()
        if not create_info:
            return None
        db_con=connections.get(db_select) if db_select else connections.get('default')
        try:
            k_obj = await self.model.create(**create_info,using_db=db_con)
            # k_obj = await self.model.create(**create_info).using_db(db_con)
        except Exception as e:
            print(e)
            k_obj = None
        return k_obj

    async def bulk_create(self, create_infos, db_select=None):
        """
        批量创建数据
        :param create_infos: list tuple
        :param db_select: 数据库连接名称
        :return: list
        """
        if not create_infos or not isinstance(create_infos, (tuple, list, set)):
            return []

        db_con = connections.get(db_select) if db_select else  connections.get('default')
        data_dal=[self.model(**create_info) for create_info in create_infos]
        # print(models)
        try:
            # 使用链式调用方式指定数据库连接，与get_by_id方法保持一致
            objs = await self.model.bulk_create(data_dal,using_db=db_con)
            inserted_objs = await self.model.filter(name__in=[i['name'] for i in create_infos])
        except Exception as e:
            print(f"Bulk create error: {e}")
            inserted_objs = None
        return inserted_objs

    async def get_by_id(self, o_id, db_select=None):
        """
        base dal 根据id获得数据
        :param o_id: id值进查询
        :param db_select: 数据库连接名称
        :return:
        """
        db_con = connections.get(db_select) if db_select else  connections.get('default')
        try:
            # obj = await self.model.get(pk=o_id,using_db=db_con)
            obj = await self.model.get(pk=o_id).using_db(db_con)
        except DoesNotExist:
            obj = None
        except Exception as e:
            print(e)
            obj = None
        return obj

    async def update_by_id(self, o_id, update_info=None, db_select=None,** kwargs):
        """
        base dal 根据id更新信息
        :param o_id: 数据的id   限制id为主键id
        :param db_select: 数据库连接名称
        :param update_info: 更新的数据
        :return: 返回的是影响的行数或者None
        """
        update_info = update_info if isinstance(update_info, dict) else dict()
        if not update_info:
            return None
        db_con = connections.get(db_select) if db_select else  connections.get('default')
        try:
            # obj = await self.model.filter(pk=o_id,using_db=db_con).update(** update_info,using_db=db_con)
            obj = await self.model.filter(pk=o_id).using_db(db_con).update(** update_info)
        except Exception as e:
            print(e)
            obj = None
        return obj

    async def update_by_filters(self, filters=None, excludes=None, update_info=None, db_select=None,** kwargs):
        """
        base dal 根据查询条件更新数据的信息
        :param filters: 获取符合条件的信息 dict
        :param excludes: 获取符合条件之外的信息 dict
        :param db_select: 读写分离数据库连接
        :param update_info: 更新数据的更新信息 k=v
        :return:
        """
        filters = filters if isinstance(filters, dict) else dict()
        excludes = excludes if isinstance(excludes, dict) else dict()
        update_info = update_info if isinstance(update_info, dict) else dict()
        db_con = connections.get(db_select) if db_select else  connections.get('default')

        try:
            query = self.model.filter(**filters).using_db(db_con)
            if excludes:
                query = query.exclude(** excludes)
            obj = await query.update(**update_info)
        except Exception as e:
            print(e)
            obj = None
        return obj

    def get_model_field_name(self):
        """
        获取模型字段名字
        :return:
        """
        # Tortoise ORM 获取字段名
        return [field_name for field_name in self.model._meta.fields_map.keys() if field_name != 'id']

    async def get_info_filters(self, filters=None, excludes=None, order_by=('-id',), db_select=None,** kwargs):
        """
        Base DAL 查询多条数据方法
        当查询条件为空时返回全部信息
        
        :param filters: 查询条件字典，返回符合条件的数据
        :param excludes: 排除条件字典，返回符合条件之外的数据
        :param order_by: 排序方式，数据类型为元组 (tuple)
        :param db_select: 数据库连接名称
        :param kwargs: 其他可选参数
        :return: 查询结果列表，包含符合条件的模型实例
        """
        filters = filters if isinstance(filters, dict) else dict()
        excludes = excludes if isinstance(excludes, dict) else dict()
        db_con = connections.get(db_select) if db_select else  connections.get('default')
        try:
            query = self.model.filter(**filters).using_db(db_con)
            if excludes:
                query = query.exclude(** excludes)

            # 处理排序
            if order_by:
                query = query.order_by(*order_by)

            # 处理关联查询
            select_related = kwargs.pop('select_related', None)
            if select_related:
                # 支持字符串或列表、元组形式
                if isinstance(select_related, (list, tuple)):
                    query = query.select_related(*select_related)
                elif isinstance(select_related, str):
                    query = query.select_related(select_related)

            # 处理字段筛选
            values = kwargs.get('values', [])
            if values:
                query = query.values(*values)
                results = await query
            else:
                results = await query
            return results
        except Exception as e:
            print(e)


    async def get_one_by_condition(self, condition, db_select=None,** kwargs):
        """
        根据条件查询单条记录

        :param condition: 查询条件字典，例如 {'id': 1, 'name': 'test'}
        :type condition: dict
        :param db_select: 数据库连接名称，默认为'default'
        :type db_select: str, optional
        :param kwargs: 额外参数
        :type kwargs: dict
        :return: 查询到的记录字典，查询失败或无结果返回None
        :rtype: dict or None

        异常处理:
        - DoesNotExist: 未找到记录时返回None
        - MultipleObjectsReturned: 找到多条记录时返回None
        - 其他异常: 打印异常信息并返回None
        """
        db_con = connections.get(db_select) if db_select else  connections.get('default')
        try:
            dict_info = await self.model.get(** condition).using_db(db_con)
        except DoesNotExist:
            dict_info = None
        except MultipleObjectsReturned:
            dict_info = None
        except Exception as e:
            print(e)
            dict_info = None
        return dict_info

    async def execute_raw_sql(self, sql_text, params=None, db_select=None):
        """执行sql"""
        db_con = connections.get(db_select) if db_select else  connections.get('default')
        if db_con == connections.get('default'):
            return await execute_safe_sql(sql_text, params or [], return_dict=True)
        else:
            return await execute_safe_sql_classic(sql_text, params or [], return_dict=True)

    async def execute_prevent_injection_raw_sql(self, sql_text, sql_param, db_select=None):
        """
        执行防注入sql
        :param sql_text: select * from `order` where order_id = %s
        :param sql_param: 参数列表 ["ET123"]
        :param db_select: 数据库连接名称
        :return:
        """
        if not isinstance(sql_param, (dict, list, tuple)):
            return None

        # 统一参数格式为列表
        params = sql_param if isinstance(sql_param, (list, tuple)) else list(sql_param.values())
        db_con = connections.get(db_select) if db_select else  connections.get('default')

        if db_con == connections.get('default'):
            return await execute_safe_sql(sql_text, params, return_dict=True)
        else:
            return await execute_safe_sql_classic(sql_text, params, return_dict=True)

    async def get_filter_and_fuzzy_queries_list(self, filters=None, q_objs=None, e_q_objs=None, excludes=None, order_by=None, db_select=None,** kwargs):
        """
        条件查询方法：结合筛选条件、Q对象和排除条件查询数据并返回结果
        工作流程：先应用filters字典筛选基础条件，再通过q_objs元组的Q对象构建复杂查询，
        同时支持e_q_objs和excludes参数排除数据，最后按order_by指定条件排序（默认主键排序）
        :param filters: dict - 筛选条件字典，格式为{字段名: 值}
        :param q_objs: tuple - Tortoise Q对象元组，用于构建复杂查询条件
        :param e_q_objs: tuple - 排除条件的Q对象元组
        :param order_by: 排序条件，可指定字段名或字段名元组
        :param db_select: str - 数据库连接名称，指定查询使用的数据库
        :param kwargs: 其他关键字参数
        :return: list - 查询结果对象列表
        """
        filters = filters if isinstance(filters, dict) else dict()
        excludes = excludes if isinstance(excludes, dict) else dict()
        q_objs = tuple(q_objs) if isinstance(q_objs, (tuple, list, set)) else tuple()
        e_q_objs = tuple(e_q_objs) if isinstance(e_q_objs, (tuple, list, set)) else tuple()
        order_by = tuple(order_by) if isinstance(order_by, (tuple, list, set)) else ('-id',)

        db_con = connections.get(db_select) if db_select else  connections.get('default')
        try:
            query = self.model.filter(*q_objs, **filters).using_db(db_con)
            if e_q_objs or excludes:
                query = query.exclude(*e_q_objs,** excludes)
            obj_list = await query.order_by(*order_by)
            print(obj_list)
            # obj_list = [ORMBaseModel.model_validate(obj).model_dump() for obj in obj_list]
        except Exception as e:
            print(e)
            obj_list = None
        return obj_list

    async def delete_mul_obj(self, filters=None, excludes=None, db_select=None,** kwargs):
        """
        批量删除数据
        :param filters: 查询条件 dict
        :param excludes: 排除条件 dict
        :param db_select: 数据库连接名称
        :return: 删除的记录数
        """
        filters = filters if isinstance(filters, dict) else dict()
        excludes = excludes if isinstance(excludes, dict) else dict()

        if not filters:
            return None

        db_con = connections.get(db_select) if db_select else  connections.get('default')
        try:
            query = self.model.filter(**filters).using_db(db_con)
            if excludes:
                query = query.exclude(** excludes)
            result = await query.delete()
        except Exception as e:
            print(e)
            result = None
        return result
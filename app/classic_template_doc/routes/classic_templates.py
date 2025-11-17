
from typing import List, Optional

from tortoise import connections
from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

from exceptions.error import ErrorCode
from utils.log_decorator import log_response
from constants.template_constant import TemplateType
from exceptions.command_exception import APIException
from app.template_doc.model.template_doc import TemplateDoc

router = APIRouter()

class TemplateItem(BaseModel):
    id: int = Field(..., description='模板id')
    name: str = Field(..., description='模板名称')
    type_decs: str = Field(..., description='模板类型')
    create_datetime: str = Field(..., description='创建时间')
    update_datetime: str = Field(..., description='更新时间')
    thumbnail_base64: str = Field(None, description='缩略图 base64')


class DataSchema(BaseModel):
    sum_count: int = Field(0, description='模板总数')
    template_list: List[TemplateItem] = Field([], description='模板列表')
    page: int = Field(1, description='页码')
    page_size: int = Field(10, description='每页条数')


class OutSchema(BaseModel):
    code: int = Field(0, description='状态码')
    message: str = Field('获取成功', description='返回信息')
    data: DataSchema = Field(..., description='返回数据')


@router.get('/get_total_template')
@log_response
async def get_total_template(
    desc: Optional[int] = Query(0, description='0: 升序，1: 降序'),
    sort_field: Optional[int] = Query(None, description='排序字段 0: id, 1: 创建时间, 2: 更新时间'),
    page: int = Query(1, ge=1, description='页码，从1开始'),
    page_size: int = Query(10, ge=1, le=100, description='每页条数，默认10，最大100'),
    experiment_type: Optional[int] = Query(None, description='实验类型 0: 光谱扫描, 1: 时间扫描, 2: 定量测定, 3: 光度测量'),
    ):
    class_db_con = connections.get('classic_db')
    # 排序字段映射
    sort_map = {
        0: 'id',
        1: 'create_datetime',
        2: 'update_datetime'
    }
    sort_key = sort_map.get(sort_field, 'id')
    if desc == 0:
        sort_key =('order',f'{sort_key}') 
          # 升序排序，Tortoise ORM语法
    else:
        sort_key =('-order',f'-{sort_key}')   # 降序排序，Tortoise ORM语法

    # 构建基础查询（如果 name 存在就加筛选）
    if experiment_type is not None:
        query = TemplateDoc.filter(is_del=0, experiment_type=experiment_type).using_db(class_db_con)
    else:
        query = TemplateDoc.filter(is_del=0).using_db(class_db_con)
    sum_count = await query.count()

    # 排序 + 分页
    query = query.order_by(*sort_key).offset((page - 1) * page_size).limit(page_size)

    # 执行查询
    template_list = await query.values('id', 'name', 'type', 'create_datetime', 'update_datetime', 'thumbnail_base64')
    template_list = [
    {
        **{k: v for k, v in item.items() if k not in ['type', 'create_datetime', 'update_datetime', 'thumbnail_base64']},
        'type_decs': TemplateType.get_name_desc_by_value(item['type']),
        'create_datetime': item['create_datetime'].strftime('%Y-%m-%d %H:%M:%S') if item['create_datetime'] else None,
        'update_datetime': item['update_datetime'].strftime('%Y-%m-%d %H:%M:%S') if item['update_datetime'] else None,
        'thumbnail_base64': f"data:image/png;base64,{item['thumbnail_base64']}" if item.get('thumbnail_base64') else None,
    }
    for item in template_list
    ]

    return {'code': 200, 
            'message': '获取成功', 
            'data': {
                'sum_count': sum_count, 
                'page': page,
                'page_size': page_size,
                'template_list': template_list
                }
            }    
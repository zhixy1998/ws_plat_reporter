
from typing import List, Optional
from fastapi import APIRouter, Query
from ..model.template_doc import TemplateDoc
from pydantic import BaseModel, Field

from tortoise import connections
from exceptions.error import ErrorCode
from constants.template_constant import TemplateType, MeasureMode
from exceptions.command_exception import APIException
from utils.log_decorator import log_response

router = APIRouter()

class TemplateItem(BaseModel):
    id: int = Field(..., description='模板id')
    name: str = Field(..., description='模板名称')
    type_decs: str = Field(..., description='模板类型')
    measure_mode: int = Field(..., description='测量模式：0经典 1向导')
    create_datetime: str = Field(..., description='创建时间')
    update_datetime: str = Field(..., description='更新时间')


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
    name: Optional[str]= Query(None, description='模板名称'), 
    desc: Optional[int] = Query(0, description='0: 升序，1: 降序'),
    sort_field: Optional[int] = Query(None, description='排序字段 0: id, 1: 创建时间, 2: 更新时间'),
    page: int = Query(1, ge=1, description='页码，从1开始'),
    page_size: int = Query(10, ge=1, le=100, description='每页条数，默认10，最大100'),
    with_classic: bool = Query(False, description='是否包含经典模板')
    ):

    # 排序字段映射
    sort_map = {
        0: 'id',
        1: 'create_datetime',
        2: 'update_datetime'
    }
    sort_key = sort_map.get(sort_field, 'id')
    if desc == 0:
        sort_key = f'{sort_key}'  # 升序排序，Tortoise ORM语法
    else:
        sort_key = f'-{sort_key}'  # 降序排序，Tortoise ORM语法

    # 构建向导模式查询
    guide_query = TemplateDoc.filter(is_del=0)
    guide_sum_count = await guide_query.count()
    if name:
        guide_query = guide_query.filter(name__contains=name)
    
    guide_total = await guide_query.count()
    
    # 构建经典模式查询（如果需要）
    classic_query = None
    classic_sum_count = 0
    classic_total = 0
    if with_classic:
        class_db_con = connections.get('classic_db')
        classic_query = TemplateDoc.filter(is_del=0).using_db(class_db_con)
        classic_sum_count = await classic_query.count()
        if name:
            classic_query = classic_query.filter(name__contains=name)
        classic_total = await classic_query.count()
    
    # 计算总数
    sum_count = guide_sum_count + classic_sum_count
    total = guide_total + classic_total
    
    # 计算分页偏移量
    offset = (page - 1) * page_size
    
    # 合并结果列表
    template_list = []
    
    # 如果 offset 在向导模式范围内
    if offset < guide_total:
        # 从向导模式获取数据
        guide_limit = min(page_size, guide_total - offset)
        guide_query = guide_query.order_by(sort_key).offset(offset).limit(guide_limit)
        guide_results = await guide_query.values('id', 'name', 'type', 'create_datetime', 'update_datetime')
        
        for item in guide_results:
            template_list.append({
                **{k: v for k, v in item.items() if k not in ['type', 'create_datetime', 'update_datetime']},
                'type_decs': TemplateType.get_name_desc_by_value(item['type']),
                'measure_mode': MeasureMode.guide.value,
                'create_datetime': item['create_datetime'].strftime('%Y-%m-%d %H:%M:%S') if item['create_datetime'] else None,
                'update_datetime': item['update_datetime'].strftime('%Y-%m-%d %H:%M:%S') if item['update_datetime'] else None,
            })
        
        # 如果还需要经典模式数据来填满 page_size
        remaining = page_size - len(template_list)
        if with_classic and remaining > 0 and classic_total > 0:
            classic_query = classic_query.order_by(sort_key).offset(0).limit(remaining)
            classic_results = await classic_query.values('id', 'name', 'type', 'create_datetime', 'update_datetime')
            
            for item in classic_results:
                template_list.append({
                    **{k: v for k, v in item.items() if k not in ['type', 'create_datetime', 'update_datetime']},
                    'type_decs': TemplateType.get_name_desc_by_value(item['type']),
                    'measure_mode': MeasureMode.classic.value,
                    'create_datetime': item['create_datetime'].strftime('%Y-%m-%d %H:%M:%S') if item['create_datetime'] else None,
                    'update_datetime': item['update_datetime'].strftime('%Y-%m-%d %H:%M:%S') if item['update_datetime'] else None,
                })
    
    # 如果 offset 超出向导模式范围，只从经典模式获取
    elif with_classic and classic_total > 0:
        classic_offset = offset - guide_total
        classic_limit = min(page_size, classic_total - classic_offset)
        classic_query = classic_query.order_by(sort_key).offset(classic_offset).limit(classic_limit)
        classic_results = await classic_query.values('id', 'name', 'type', 'create_datetime', 'update_datetime')
        
        for item in classic_results:
            template_list.append({
                **{k: v for k, v in item.items() if k not in ['type', 'create_datetime', 'update_datetime']},
                'type_decs': TemplateType.get_name_desc_by_value(item['type']),
                'measure_mode': MeasureMode.classic.value,
                'create_datetime': item['create_datetime'].strftime('%Y-%m-%d %H:%M:%S') if item['create_datetime'] else None,
                'update_datetime': item['update_datetime'].strftime('%Y-%m-%d %H:%M:%S') if item['update_datetime'] else None,
            })

    return {'code': 200, 
            'message': '获取成功', 
            'data': {
                'sum_count': sum_count, 
                'page': page,
                'page_size': page_size,
                'template_list': template_list
                }
            }    
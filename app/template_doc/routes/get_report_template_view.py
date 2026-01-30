from typing import List, Optional, Union
from fastapi import APIRouter, Query
from ..model.template_doc import TemplateDoc
from pydantic import BaseModel, Field

from exceptions.error import ErrorCode
from constants.template_constant import ExperimentType, TemplateType, TemplateOriginType
from exceptions.command_exception import APIException
from utils.log_decorator import log_response

router = APIRouter()

class TemplateItem(BaseModel):
    id: int = Field(..., description='模板id')
    name: str = Field(..., description='模板名称')
    type_decs: str = Field(..., description='模板类型')
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


@router.get('/get_report_template')
@log_response
async def get_report_template(
    name: Optional[str]= Query(None, description='模板名称'), 
    industry: Optional[str]= Query(None, description='行业类型'),
    origin_type: Optional[int]= Query(None, description='模板来源类型'),
    experiment_type: Optional[Union[int, str]]= Query(None, description='实验类型'),
    template_type: Optional[int]= Query(None, description='模板类型'),
    desc: Optional[int] = Query(0, description='0: 升序，1: 降序'),
    sort_field: Optional[int] = Query(None, description='排序字段 0: id, 1: 创建时间, 2: 更新时间'),
    page: int = Query(1, ge=1, description='页码，从1开始'),
    page_size: int = Query(10, ge=1, le=100, description='每页条数，默认10，最大100'),
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

    # if type not in [0, 1]:
    #     raise APIException(ErrorCode.REPORT_TEMPLATE_TYPE_ERROR)

    # 构建基础查询（如果 name 存在就加筛选）
    query = TemplateDoc.filter(is_del=0)
    sum_count = await query.count()
    if name:
        query = query.filter(name__contains=name)
    if industry:
        query = query.filter(industry_type=industry)
    if origin_type is not None:
        query = query.filter(origin_type=origin_type)
    if experiment_type is not None:
        if isinstance(experiment_type, str):
            try:
                experiment_type = int(experiment_type)
            except:
                experiment_type = ExperimentType.generate_decs_value_map().get(experiment_type)
        query = query.filter(experiment_type=experiment_type)
    if template_type is not None:
        query = query.filter(type=template_type)

    total = await query.count()
    # 排序 + 分页
    query = query.order_by(sort_key).offset((page - 1) * page_size).limit(page_size)

    # 执行查询
    template_list = await query.values('id', 'name', 'type', 'create_datetime', 'update_datetime', 'industry_type', 'experiment_type', 'origin_type')
    template_list = [
    
    {
        **{k: v for k, v in item.items() if k not in ['type', 'create_datetime', 'update_datetime']},
        'type_decs': TemplateType.get_name_desc_by_value(item['type']),
        'create_datetime': item['create_datetime'].strftime('%Y-%m-%d %H:%M:%S') if item['create_datetime'] else None,
        'update_datetime': item['update_datetime'].strftime('%Y-%m-%d %H:%M:%S') if item['update_datetime'] else None,
        'experiment_type_decs': ExperimentType.get_name_desc_by_value(item['experiment_type']),
        'origin_type_decs': TemplateOriginType.get_name_desc_by_value(item['origin_type']),
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
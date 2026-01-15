from typing import Dict, Optional
from fastapi import APIRouter

from exceptions.error import ErrorCode
from exceptions.command_exception import APIException
from ..model.template_doc import TemplateDoc
from pydantic import BaseModel, Field
from app.db import execute_safe_sql
from utils.log_decorator import log_response
from scripts.one_time.change_industry_type import run
from constants.template_constant import TemplateOriginType, TemplateType

router = APIRouter()

class OutSchema(BaseModel):
    code: int = Field(0, description='状态码')
    message: str = Field('获取成功', description='返回信息')
    data: Optional[Dict[str, Dict[str, int]]] = Field(..., description="{'名字': '数量'}", json_schema_extra={
            "example": {
                "环境监测": 4,
                "食品检测": 2
            }
        })

@router.get('/get_template_industry', response_model=OutSchema)
@log_response
async def get_template_industry():
    return_dict = {}

    sql_text = """
    select industry_type, count(*) as count from template_doc where is_del=0 group by industry_type
    """
    sql_result = await execute_safe_sql(sql_text, return_dict=True)
    # if len(sql_result) == 1 and sql_result[0]['industry_type'] is None:
    #     await run()
    #     return OutSchema(code=200, message='获取成功', data={})
    industry_dict = {}
    for item in sql_result:
        if item['industry_type'] is not None:
            industry_dict[item['industry_type']] = item['count']
    return_dict['industry_type'] = industry_dict


    sql_text = """
    select origin_type, count(*) as count from template_doc where is_del=0 group by origin_type
    """
    sql_result = await execute_safe_sql(sql_text, return_dict=True)
    # if len(sql_result) == 1 and sql_result[0]['industry_type'] is None:
    #     await run()
    #     return OutSchema(code=200, message='获取成功', data={})
    origin_dict = {}
    for item in sql_result:
        if item['origin_type'] is not None:
            origin_dict[TemplateOriginType.get_name_desc_by_value(item['origin_type'])] = item['count']
    return_dict['origin_type'] = origin_dict

    sql_text = """
    select type, count(*) as count from template_doc where is_del=0 group by type
    """
    sql_result = await execute_safe_sql(sql_text, return_dict=True)
    # if len(sql_result) == 1 and sql_result[0]['industry_type'] is None:
    #     await run()
    #     return OutSchema(code=200, message='获取成功', data={})
    template_type_dict = {}
    for item in sql_result:
        if item['type'] is not None:
            template_type_dict[TemplateType.get_name_desc_by_value(item['type'])] = item['count']
    return_dict['template_type'] = template_type_dict
    return OutSchema(code=200, message='获取成功', data=return_dict)
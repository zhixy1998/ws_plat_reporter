import os
import base64
from pydoc import describe
from random import choice
from re import S
import tempfile
import subprocess
from io import BytesIO
from typing import List, Optional
from pathlib import Path

from jinja2.utils import F
from tortoise import connections
from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from exceptions.error import ErrorCode
from utils.log_decorator import log_response
from constants.template_constant import TemplateType
from exceptions.command_exception import APIException
from app.template_doc.model.template_doc import TemplateDoc
from utils.template_utils import get_doc_name_and_doc_stream_obj
from utils.doc_converter import get_libreoffice_command
from utils.classic_fille_template_utils_simple import ClassicFillDataUtils
from .classic_export_original_data_doc_view import get_measure_type
from dal.base_dal import BaseDal
from app.template_doc.model.template_bookmark import TemplateBookmark
from dal.template_doc_dal import template_doc_dal
from dal.template_bookmark_dal import template_bookmark_dal


router = APIRouter()

@router.post('/test_dal')
@log_response
async def test_dal():
    # sample_data = {
    #     # id 数据库自增，无需手动写
    #     "parent_id": 0,
    #     "template_doc_id": 12,
    #     "name": "测试书签",
    #     "type": 0,  # 0:text
    #     "description": "这是一个测试书签，用于接口和单元测试",
    #     "sort_order": 1,
    #     "font": "宋体",
    #     "font_size": 12,
    #     "img_size": 1.5,
    #     "is_del": 0
    # }
    # result=await template_bookmark_dal.create_one_obj(sample_data)
    test_data_list = [
        {
            "parent_id": 0,
            "template_doc_id": 1,
            "name": "书签A",
            "type": 0,
            "description": "测试书签A",
            "sort_order": 1,
            "font": "宋体",
            "font_size": 12,
            "img_size": 1.0,
            "is_del": 0
        },
        {
            "parent_id": 0,
            "template_doc_id": 1,
            "name": "书签B",
            "type": 1,
            "description": "测试书签B",
            "sort_order": 2,
            "font": "微软雅黑",
            "font_size": 14,
            "img_size": 1.2,
            "is_del": 0
        },
        {
            "parent_id": 1,
            "template_doc_id": 2,
            "name": "书签C",
            "type": 2,
            "description": "测试书签C",
            "sort_order": 3,
            "font": "黑体",
            "font_size": 16,
            "img_size": 2.0,
            "is_del": 0
        }
    ]
    result=await template_bookmark_dal.bulk_create(test_data_list)
    # result=await template_bookmark_dal.get_by_id(o_id= 13606)
    # result=await template_bookmark_dal.update_by_id(o_id=13606,update_info={'name':'驾驾驾'})
    # result=await template_bookmark_dal.update_by_filters(filters={'id':'13609'},update_info={'name':'ss驾驾驾ss'})#,excludes={'id':'13609'})
    # result=template_bookmark_dal.get_model_field_name()
    # result=await template_bookmark_dal.get_info_filters(
    #     filters={},
    #     excludes={'id__lte': 13300, 'template_doc_id__lte': 5},
    #     # select_related='template_doc_id'
    # )
    # result=await template_bookmark_dal.get_one_by_condition(
    #    condition= {'id': 13609}
    # )
    # result=await template_bookmark_dal.execute_prevent_injection_raw_sql(
    #     sql_text='select * from template_bookmark where id >= %s',
    #     sql_param=[13400]
    # )
    # result=await template_bookmark_dal.get_filter_and_fuzzy_queries_list(
    #     filters={
    #          'id__gt': 13000, 
    #     }
    # )
    # result=await template_bookmark_dal.delete_mul_obj(
    #     filters={
    #         'id':'13609'
    #     }
    # )
    return result
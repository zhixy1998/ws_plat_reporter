import importlib
import requests
import os, urllib
from fastapi import APIRouter
from pydantic import BaseModel, Field
from utils.log_decorator import log_response
from config import config
from app.template_doc.model.template_doc import TemplateDoc
from utils.fille_template_utils import FillDataUtils
from constants.template_constant import ExperimentType

router = APIRouter()

@router.get('/get_m')
@log_response
async def get_m(template_id, task_id: str = None, sample_id: str = None, measurement_type_decs: str = ''):
    task_id = '61aa663028192bcc8d73b54562af000d'
    template_common_url = config.guide_template_table_head_data_url + '?taskId=' + urllib.parse.quote(str(task_id), safe='') + '&sampleId=' + urllib.parse.quote(str(sample_id), safe='')
    print(template_common_url)
    response = requests.get(template_common_url)
    res_json = response.json()
    # print(res_json)
    
    template = await TemplateDoc.get_or_none(id=template_id)
    if not template:
        return {'code':400, 'message':'模板不存在'}
    

    module_name = "template_structure." + template.name
    try:
        private_mod = importlib.import_module(module_name)
    except Exception as e:
        private_mod = None
    
    if measurement_type_decs == ExperimentType.quantitative_determination.decs:
        stand_head_list = res_json.get('data').get('standHeadList')
        unknow_head_list = res_json.get('data').get('unknowHeadList')

        fill_data_utils = FillDataUtils(template.name, template_id, fake=True)
        HEADER_M_MAPPING_LIST = fill_data_utils.table_data_processor.handler_instance.HEADER_M_MAPPING_LIST  # 每个私有文件都要声明的
        TABLE_HEADER_MAP  = fill_data_utils.table_data_processor.handler_instance.TABLE_HEADER_MAP
        STAND = fill_data_utils.table_data_processor.handler_instance.STAND
        exist_stand = {i.get("identity"): i.get('printTitle') for i in stand_head_list }
        exist_unknown = {i.get("identity"): i.get('printTitle') for i in unknow_head_list }

        now_stand = []
        for s in STAND:
            now_stand.append({
                "identity": s,
                "printTitle": exist_stand.get(s),
            })
        now_unknown = []
        for header_map in HEADER_M_MAPPING_LIST:
            for key, value in header_map.items():
                now_unknown.append({
                    'mark': key,
                    "identity": value,
                    "printTitle": exist_unknown.get(value),
                })

    else:
        pass
    
    
    return {'code':200, 'message':'success', 'data':{'now_stand': now_stand, 'now_unknown': now_unknown, 'exist_stand': exist_stand, 'exist_unknown': exist_unknown}}
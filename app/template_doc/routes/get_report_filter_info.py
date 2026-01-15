
from fastapi import APIRouter
from pydantic import BaseModel, Field
from utils.log_decorator import log_response
from app.template_doc.model.template_doc import TemplateDoc
from constants.template_constant import TemplateType, ExperimentType, TemplateOriginType

router = APIRouter()

class InputSchema(BaseModel):
    task_id: str = Field(..., description='任务id')
    sample_id: str = Field(None, description='样品id')

@router.get('/get_report_filter_info')
@log_response
async def get_m():
    all_template = await TemplateDoc.filter(is_del=0).all()
    industry_list = []
    origin_type_list = [{'value': i, 'label': desc} for i, desc in TemplateOriginType.generate_value_desc_map().items()]
    experiment_type_list = [{'value': i, 'label': desc} for i, desc in ExperimentType.generate_value_desc_map().items()]
    template_type_list = [{'value': i, 'label': desc} for i, desc in TemplateType.generate_value_desc_map().items()]

    for template in all_template:
        if template.industry_type not in industry_list:
            industry_list.append(template.industry_type) 

    return {'code':200, 'message':'success', 'data': {'industry': industry_list, 
        'origin_type': origin_type_list, 'experiment_type': 
        experiment_type_list, 'template_type': template_type_list, }}
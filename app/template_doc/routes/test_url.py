from fastapi import APIRouter
from utils.template_utils import GetDataFromDatabase

router = APIRouter()

@router.get('/test_url')
async def test_url(task_id: str):
    data = GetDataFromDatabase(task_id)
    original_data = await data.get_original_data()
    print(original_data)
    print(data.measure_data_id)
    print(data.sample_key)
    analysis_data = await data.get_analysis_data()
    print(analysis_data)
    return {'code': 200, 'message': 'test_url'}

from .base_dal import BaseDal
from app.admin_backup.model.backup_model import FTMeasureAnalysisData


class FTMeasureAnalysisDataDal(BaseDal):
    
    def __init__(self):
        super().__init__(model=FTMeasureAnalysisData)



f_t_measure_analysis_data_dal = FTMeasureAnalysisDataDal()
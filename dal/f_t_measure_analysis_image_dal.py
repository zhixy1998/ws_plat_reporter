from .base_dal import BaseDal
from app.admin_backup.model.backup_model import FTMeasureAnalysisImage


class FTMeasureAnalysisImageDal(BaseDal):
    
    def __init__(self):
        super().__init__(model=FTMeasureAnalysisImage)



f_t_measure_analysis_image_dal = FTMeasureAnalysisImageDal()
from .base_dal import BaseDal
from app.admin_backup.model.backup_model import FTMeasureSampleHead


class FTMeasureSampleHeadDal(BaseDal):
    
    def __init__(self):
        super().__init__(model=FTMeasureSampleHead)


f_t_measure_sample_head_dal = FTMeasureSampleHeadDal()
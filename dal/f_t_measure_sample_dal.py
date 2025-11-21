
from .base_dal import BaseDal
from app.admin_backup.model.backup_model import FTMeasureSample


class FTMeasureSampleDal(BaseDal):
    
    def __init__(self):
        super().__init__(model=FTMeasureSample)


f_t_measure_sample_dal = FTMeasureSampleDal()
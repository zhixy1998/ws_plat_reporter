from .base_dal import BaseDal
from app.admin_backup.model.backup_model import FTMeasureEqualSample


class FTMeasureEqualSampleDal(BaseDal):
    
    def __init__(self):
        super().__init__(model=FTMeasureEqualSample)


f_t_measure_equal_sample_dal = FTMeasureEqualSampleDal()
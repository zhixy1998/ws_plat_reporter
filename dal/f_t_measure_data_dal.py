from .base_dal import BaseDal
from app.admin_backup.model.backup_model import FTMeasureData


class FTMeasureDataDal(BaseDal):
    
    def __init__(self):
        super().__init__(model=FTMeasureData)


f_t_measure_data_dal = FTMeasureDataDal()
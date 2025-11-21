from .base_dal import BaseDal
from app.admin_backup.model.backup_model import FTMeasureMethod


class FTMeasureMethodDal(BaseDal):
    
    def __init__(self):
        super().__init__(model=FTMeasureMethod)



f_t_measure_method_dal = FTMeasureMethodDal()
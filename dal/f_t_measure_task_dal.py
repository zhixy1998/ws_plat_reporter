from .base_dal import BaseDal
from app.admin_backup.model.backup_model import FTMeasureTask


class FTMeasureTaskDal(BaseDal):
    
    def __init__(self):
        super().__init__(model=FTMeasureTask)


f_t_measure_task_dal = FTMeasureTaskDal()
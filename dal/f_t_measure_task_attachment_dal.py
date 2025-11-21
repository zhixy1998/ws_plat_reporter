from .base_dal import BaseDal
from app.admin_backup.model.backup_model import FTMeasureTaskAttachment


class FTMeasureTaskAttachmentDal(BaseDal):
    
    def __init__(self):
        super().__init__(model=FTMeasureTaskAttachment)


f_t_measure_task_attachment_dal = FTMeasureTaskAttachmentDal()
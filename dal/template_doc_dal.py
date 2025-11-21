from .base_dal import BaseDal
from app.template_doc.model.template_doc import TemplateDoc


class TemplateDocDal(BaseDal):
    
    def __init__(self):
        super().__init__(model=TemplateDoc)



template_doc_dal = TemplateDocDal()
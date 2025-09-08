import base64, json
from io import BytesIO
from docx import Document
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

from app.template_doc.model.template_doc import TemplateDoc
from app.db import execute_safe_sql


async def get_doc_obj_by_template_id(template_id: int):
    template = await TemplateDoc.get_or_none(id=template_id)
    if not template:
        return {'code': 1, 'message': '模板不存在'}
    # 2. base64 解码成二进制
    content_bytes = base64.b64decode(template.template_content)
    doc_stream = BytesIO(content_bytes)
    doc = Document(doc_stream)
    return doc

async def get_doc_name_and_doc_stream_obj(template_id: int):

    template = await TemplateDoc.get_or_none(id=template_id)
    if not template:
        return {'code': 1, 'message': '模板不存在'}
    # 2. base64 解码成二进制
    content_bytes = base64.b64decode(template.template_content)
    doc_stream = BytesIO(content_bytes)
    return template.name, doc_stream


def add_section_page_break(document):
    """
    在文档最后加一个分页的 section break，避免空白页。
    """
    # 添加一个空段落
    p = document.add_paragraph()
    
    # 设置段落为 section break (next page)
    p._p.get_or_add_pPr()
    sectPr = OxmlElement('w:sectPr')
    # 设置分页类型
    type_ = OxmlElement('w:type')
    type_.set(qn('w:val'), 'nextPage')
    sectPr.append(type_)
    p._p.get_or_add_pPr().append(sectPr)


def remove_empty_paragraphs_at_end(doc):
    """
    移除文档末尾的空段落，避免产生多余的空白页
    """
    # 获取文档的所有段落
    paragraphs = doc.paragraphs
    
    # 从后往前遍历，移除末尾的空段落
    while paragraphs and (not paragraphs[-1].text.strip() or paragraphs[-1].text == ''):
        # 获取最后一个段落的XML元素
        last_para = paragraphs[-1]
        # 从父元素中移除这个段落
        last_para._element.getparent().remove(last_para._element)
        # 重新获取段落列表
        paragraphs = doc.paragraphs

def remove_last_section_break(doc):
    """
    移除文档末尾的分节符，避免产生空白页
    """
    # 获取文档的最后一个段落
    if doc.paragraphs:
        last_para = doc.paragraphs[-1]
        # 检查段落是否包含分节符
        pPr = last_para._p.get_or_add_pPr()
        sectPr = pPr.find(qn('w:sectPr'))
        if sectPr is not None:
            # 移除分节符
            pPr.remove(sectPr)

def clean_document_for_merge(doc):
    """
    清理文档以便合并，移除可能导致空白页的元素
    """
    # 移除末尾的空段落
    remove_empty_paragraphs_at_end(doc)
    
    # 移除末尾的分节符
    remove_last_section_break(doc)
    
    return doc


class GetDataFromDatabase:
    def __init__(self, task_id):
        self.task_id = task_id
        self.sample_key_list = []
        self.original_calculation_data_list = []
        self.measure_data_id_list = []
    
    async def get_original_data(self):
        measure_task_sql = "SELECT sample_key FROM t_measure_task WHERE id = %s"
        measure_task_sql_result = await execute_safe_sql(measure_task_sql, [self.task_id], return_dict=True)
        if measure_task_sql_result:
            sample_key_list_json = measure_task_sql_result[0].get('sample_key')
            if sample_key_list_json:
                sample_key_list = json.loads(sample_key_list_json)
                for sample_key_dict in sample_key_list:
                    if sample_key_dict.get('isTested') == '1' and sample_key_dict.get('deleteType') == '0':
                        self.sample_key_list.append(sample_key_dict.get('specimenKey'))
        if self.sample_key_list:
            for sample_key in self.sample_key_list:
                measure_data_sql = "SELECT id, original_calculation_data, serial_number FROM t_measure_data WHERE task_id = %s and sample_key = %s order by serial_number desc limit 1"
                measure_data_sql_result = await execute_safe_sql(measure_data_sql, [self.task_id, sample_key], return_dict=True)
                if measure_data_sql_result:
                    original_calculation_data = measure_data_sql_result[0].get('original_calculation_data')
                    self.original_calculation_data_list.append(json.loads(original_calculation_data))
                self.measure_data_id_list.append(measure_data_sql_result[0].get('id'))
        return self.original_calculation_data_list
    
    async def get_analysis_data(self):
        analysis_data_sql = "select analysis_result from t_measure_analysis_data where task_id = %s and measure_data_id = %s and sample_key = %s order by data_version desc limit 1"
        analysis_data_sql_result = await execute_safe_sql(analysis_data_sql, [self.task_id, self.measure_data_id, self.sample_key], return_dict=True)
        if analysis_data_sql_result:
            analysis_result = analysis_data_sql_result[0].get('analysis_result')
            self.analysis_result = analysis_result
            return analysis_result
            
        


         

        


import io
import requests
from fastapi import APIRouter
from pydantic import BaseModel, Field
from utils.log_decorator import log_response
from config import config
from app.template_doc.model.template_doc import TemplateDoc
from utils.template_utils import get_doc_name_and_doc_stream_obj
from utils.verification_calibration_utils.verification_calibration_handle import _remove_outer_borders_only, _set_cell_margins
from docxtpl import DocxTemplate
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt, Cm
from io import BytesIO
import urllib.parse
from fastapi.responses import StreamingResponse
from exceptions.command_exception import APIException
from exceptions.error import ErrorCode
from utils.template_utils import convert_docx_to_pdf_bytes

router = APIRouter()

def create_seamless_subdoc_table(tpl, rows):
    if not rows:
        return tpl.new_subdoc()
        
    subdoc = tpl.new_subdoc()
    table_rows = len(rows)
    table_cols = max(len(row) for row in rows) if rows else 0
    
    if table_rows == 0 or table_cols == 0:
        return subdoc
        
    t = subdoc.add_table(rows=table_rows, cols=table_cols)
    # t.style = "Table Grid"
    
    for paragraph in subdoc.paragraphs:
        pPr = paragraph._element.get_or_add_pPr()
        spacing = OxmlElement('w:spacing')
        spacing.set(qn('w:before'), '0')
        spacing.set(qn('w:after'), '0')
        spacing.set(qn('w:line'), '240')
        spacing.set(qn('w:lineRule'), 'auto')
        for s in pPr.findall(qn('w:spacing')):
            pPr.remove(s)
        pPr.append(spacing)
        
        ind = OxmlElement('w:ind')
        ind.set(qn('w:left'), '0')
        ind.set(qn('w:right'), '0')
        ind.set(qn('w:hanging'), '0')
        ind.set(qn('w:firstLine'), '0')
        for i in pPr.findall(qn('w:ind')):
            pPr.remove(i)
        pPr.append(ind)
        
        jc = OxmlElement('w:jc')
        jc.set(qn('w:val'), 'center')
        for j in pPr.findall(qn('w:jc')):
            pPr.remove(j)
        pPr.append(jc)

    # 移除外圈边框，只保留内部网格线
    _remove_outer_borders_only(t)
    # 设置单元格内外边距为0
    _set_cell_margins(t, margin=0)
    
    tbl = t._tbl
    tblPr = tbl.tblPr
    if tblPr is None:
        tblPr = OxmlElement('w:tblPr')
        tbl.insert(0, tblPr)
        
    tblMar = OxmlElement('w:tblMar')
    for margin_name in ['top', 'left', 'bottom', 'right']:
        mar = OxmlElement(f'w:{margin_name}')
        mar.set(qn('w:w'), '0')
        mar.set(qn('w:type'), 'dxa')
        tblMar.append(mar)
    for m in tblPr.findall(qn('w:tblMar')):
        tblPr.remove(m)
    tblPr.append(tblMar)
    
    tblLayout = OxmlElement('w:tblLayout')
    tblLayout.set(qn('w:type'), 'autofit')
    for layout in tblPr.findall(qn('w:tblLayout')):
        tblPr.remove(layout)
    tblPr.append(tblLayout)
    
    tblW = OxmlElement('w:tblW')
    tblW.set(qn('w:w'), '5000')  # 100%
    tblW.set(qn('w:type'), 'pct')
    for w in tblPr.findall(qn('w:tblW')):
        tblPr.remove(w)
    tblPr.append(tblW)
    
    for r, row_data in enumerate(rows):
        tr = t.rows[r]._tr
        trPr = tr.get_or_add_trPr()
        trHeight = OxmlElement('w:trHeight')
        trHeight.set(qn('w:val'), str(int(Cm(0.7).twips)))
        trHeight.set(qn('w:hRule'), 'atLeast')
        for h in trPr.findall(qn('w:trHeight')):
            trPr.remove(h)
        trPr.append(trHeight)

        for c in range(table_cols):
            cell = t.cell(r, c)
            cell_text = str(row_data[c]) if c < len(row_data) and row_data[c] is not None else ""
            cell.text = cell_text
            
            tc = cell._element
            tcPr = tc.get_or_add_tcPr()
            vAlign = OxmlElement('w:vAlign')
            vAlign.set(qn('w:val'), 'center')
            for v in tcPr.findall(qn('w:vAlign')):
                tcPr.remove(v)
            tcPr.append(vAlign)
            
            for paragraph in cell.paragraphs:
                pPr = paragraph._element.get_or_add_pPr()
                jc = OxmlElement('w:jc')
                jc.set(qn('w:val'), 'center')
                for j in pPr.findall(qn('w:jc')):
                    pPr.remove(j)
                pPr.append(jc)
                for run in paragraph.runs:
                    run.font.name = '宋体'
                    run._element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
                    run.font.size = Pt(9)
                    
    return subdoc

class InputSchema(BaseModel):
    task_id: str = Field(..., description='任务id')
    template_id: int = Field(..., description='模板id')

@router.post('/installation_acceptance_export', response_class=StreamingResponse, responses={200: {"content": {"application/pdf": {}}}})
@log_response
async def installation_acceptance_export_view(input: InputSchema):
    """
    wavelength_mpe: 波长最大允许误差值
    wl_rep: 波长重复性
    bsl_stab: 基线稳定性
    stab: 稳定性
    noise: 噪声
    stray_lt: 杂散光
    photo_acc: 光度准确度
    """
    java_domain_url = config.java_domain + '/com/persee/workstation/uv-inexus/factory-inspection/open-box-check/acceptanceReport'
    url = java_domain_url + '?taskId=' + input.task_id
    reponse = requests.get(url)
    r_json = reponse.json()
    res_data = r_json.get('data') or {}
    contexts = {}
    
    table_data = []
    k_list = ['wavelength_mpe', 'wl_rep', 'bsl_stab', 'stab', 'noise', 'stray_lt', 'photo_acc']
    
    # 获取动态列数（要求最少3列，最大扩展到5列）
    max_len = 3
    for k in ['wavelength_mpe', 'wl_rep']:
        k_info = res_data.get(k) or {}
        m_val = k_info.get('measuredValue')
        if isinstance(m_val, list) and len(m_val) > max_len:
            max_len = len(m_val)
    val_count = min(max_len, 5)
    contexts['val_count'] = val_count
    
    for k in k_list:
        k_info = res_data.get(k) or {}

        contexts[k+'_standard'] = k_info.get('standardValue')
        if k not in ['wavelength_mpe', 'wl_rep']:
            contexts[k+'_value'] = k_info.get('measuredValue')
        else:
            m_val = k_info.get('measuredValue') or []
            padded_vals = []
            for i in range(val_count):
                if i < len(m_val):
                    padded_vals.append(m_val[i])
                else:
                    padded_vals.append("")
            contexts[k+'_values'] = padded_vals
            
            # 为了兼容保留旧的v0, v1, v2给word模版以防其仍然访问
            for i in range(3):
                if i < len(padded_vals):
                    contexts[k+'_v'+str(i)] = padded_vals[i]
                else:
                    contexts[k+'_v'+str(i)] = ""
                
    
    
    try:
        # print(f"[installation_acceptance_export] start task_id={input.task_id}, template_id={input.template_id}")
        # ---- 临时测试代码：写死读取本地 HTML 模板 ----
        template_name, doc_stream = await get_doc_name_and_doc_stream_obj(input.template_id)
        doc_bytes = doc_stream.read()
        is_html = doc_bytes.strip().startswith(b'<')
        # print(f"[installation_acceptance_export] template_name={template_name}, is_html={is_html}, template_size={len(doc_bytes)}")
        
        # is_html = True
        # template_name = "测试_本地安装验收"

        if is_html:
            from utils.verification_calibration_utils.html_report.installation_html_builder import InstallationHtmlBuilder

            template_html = doc_bytes.decode('utf-8')
            # print(f"[installation_acceptance_export] using database html template, html_size={len(template_html)}")
            builder = InstallationHtmlBuilder(context_data=contexts, template_html=template_html)
            pdf_out_stream = builder.run()
            pdf_out_stream.seek(0)
            pdf_bytes = pdf_out_stream.read()
            # print(f"[installation_acceptance_export] html->pdf done, pdf_size={len(pdf_bytes)}")

        else:
            doc_stream.seek(0)
            tpl = DocxTemplate(doc_stream)
            
            # 将表格转换为紧贴边框的无边框sub_doc
            contexts['sub_table'] = create_seamless_subdoc_table(tpl, table_data)

            tpl.render(contexts)
            output_stream = BytesIO()
            tpl.save(output_stream)
            output_stream.seek(0)

            # Debug: Save the word document
            # with open(f'debug_{input.task_id}.docx', 'wb') as f:
            #     f.write(output_stream.getvalue())

            pdf_bytes = convert_docx_to_pdf_bytes(output_stream)
            # print(f"[installation_acceptance_export] docx->pdf done, pdf_size={len(pdf_bytes) if pdf_bytes else 0}")

        # Debug logs can go here
        #     # Debug: Save the converted PDF document
        #     with open(f'debug_{input.task_id}.pdf', 'wb') as f:
        #         f.write(pdf_bytes)

        if not pdf_bytes:
            # print(f"[DEBUG export_docx] !! pdf_bytes 为空，抛出异常")
            raise APIException(ErrorCode.INTERNAL_ERROR, "PDF转换失败")

        from urllib.parse import quote
        filename = f"{template_name}_{input.task_id}.pdf"
        encoded_filename = quote(filename)
        # print(f"[DEBUG export_docx] 准备返回 StreamingResponse, filename={filename}, pdf_size={len(pdf_bytes)}")
    
        # 返回文件下载
        return StreamingResponse(
            BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}",
                "Content-Length": str(len(pdf_bytes)),
            }
        )
        
    except Exception as e:
        import traceback
        print(f"[installation_acceptance_export] failed: {e}")
        traceback.print_exc()
        empty_stream = io.BytesIO(b'')
        return StreamingResponse(
            empty_stream, 
            media_type="application/pdf", 
            headers={
                "Content-Disposition": "attachment; filename=original.pdf",
                "Content-Length": "0" 
            }
        )
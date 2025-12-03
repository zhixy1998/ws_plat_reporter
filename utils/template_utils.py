import os
import tempfile
import base64, json
import subprocess
import threading
import time
import platform
from io import BytesIO
from typing import List
from docx import Document
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from docx2pdf import convert

from app.db import execute_safe_sql
from utils.doc_converter import get_libreoffice_command
from app.template_doc.model.template_doc import TemplateDoc


async def get_doc_obj_by_template_id(template_id: int, classic_db=None):
    if classic_db:
        template = await TemplateDoc.get_or_none(id=template_id, using_db=classic_db)
    else:
        template = await TemplateDoc.get_or_none(id=template_id)
    if not template:
        return {'code': 1, 'message': '模板不存在'}
    # 2. base64 解码成二进制
    content_bytes = base64.b64decode(template.template_content)
    doc_stream = BytesIO(content_bytes)
    doc = Document(doc_stream)
    return doc

async def get_doc_name_and_doc_stream_obj(template_id: int, conn=None):
    if conn is None:
        template = await TemplateDoc.get_or_none(id=template_id)
    else:
        template = await TemplateDoc.get_or_none(id=template_id, using_db=conn)
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

import threading
import time
import platform

# 全局锁：控制 LibreOffice 并发
_libreoffice_lock = threading.Lock()

def convert_docx_to_pdf_bytes(file_stream) -> bytes:
    """
    将 Word 文档转换为 PDF，返回字节流（用于文件下载）
    使用 LibreOffice 转换，支持所有页面
    
    Windows 优化版本：
    - 加并发锁，防止多个 LibreOffice 进程冲突
    - 增加超时时间到 60 秒
    - 加重试机制
    - 强制清理 LibreOffice 进程
    """
    # 重置流指针到开头（如果可能）
    try:
        file_stream.seek(0)
    except:
        pass
    
    doc_raw_bytes = file_stream.read()
    
    # 使用锁保证同一时间只有一个 LibreOffice 进程
    with _libreoffice_lock:
        return _do_convert_docx_to_pdf_bytes(doc_raw_bytes)


def _do_convert_docx_to_pdf_bytes(doc_raw_bytes: bytes) -> bytes:
    """
    实际的转换逻辑（在锁内执行）
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        docx_path = os.path.join(tmpdir, "input.docx")
        pdf_path = os.path.join(tmpdir, "input.pdf")

        # 保存 docx 文件
        with open(docx_path, "wb") as f:
            f.write(doc_raw_bytes)

        system = platform.system()
        if system in ['Windows'] and has_ms_word():
            try:
                convert(docx_path, pdf_path)
                return open(pdf_path, "rb").read()
            except Exception as e:
                print(f"docx2pdf 转换失败: {e}，尝试使用 LibreOffice")

        # 如果 docx2pdf 不可用或失败，使用 LibreOffice
        for attempt in range(2):
            try:
                print(f" [DEBUG] DOCX → PDF 转换开始（尝试 {attempt + 1}/2）...")
                cmd = get_libreoffice_command(tmpdir, docx_path, 'pdf')

                # Windows 上增加超时时间到 60 秒，其他系统 30 秒
                timeout = 30 if platform.system() == 'Windows' else 30
                print('cmd======', cmd)
                result = subprocess.run(
                    cmd, 
                    check=True, 
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.PIPE, 
                    timeout=timeout
                )

                # 给系统一点时间确保文件写入完成
                time.sleep(0.5)

                # 检查 PDF 是否生成
                if not os.path.exists(pdf_path):
                    print(f" PDF 生成失败（文件不存在）")
                    if attempt == 0:
                        # 第一次失败，继续重试
                        _kill_libreoffice_processes()
                        time.sleep(1)
                        continue
                    return b""

                # 读取 PDF 文件
                with open(pdf_path, "rb") as pdf_file:
                    pdf_bytes = pdf_file.read()

                if len(pdf_bytes) == 0:
                    print(f" PDF 文件为空")
                    if attempt == 0:
                        _kill_libreoffice_processes()
                        time.sleep(1)
                        continue
                    return b""

                print(f" [DEBUG] PDF 生成成功: {len(pdf_bytes)} bytes")
                return pdf_bytes

            except subprocess.TimeoutExpired as e:
                print(f" LibreOffice 转换超时（{timeout} 秒）- 尝试 {attempt + 1}/2")
                if attempt == 0:
                    # 第一次超时，强制杀死进程并重试
                    _kill_libreoffice_processes()
                    time.sleep(2)  # 等待进程清理
                    continue
                print(f" 重试失败，放弃")
                return b""

            except subprocess.CalledProcessError as e:
                print(f" LibreOffice 转换失败（返回码 {e.returncode}）: {e.stderr.decode() if e.stderr else 'unknown error'}")
                if attempt == 0:
                    _kill_libreoffice_processes()
                    time.sleep(1)
                    continue
                return b""

            except Exception as e:
                print(f" 转换过程出错: {e}")
                import traceback
                traceback.print_exc()
                if attempt == 0:
                    _kill_libreoffice_processes()
                    time.sleep(1)
                    continue
                return b""

        return b""


def _kill_libreoffice_processes():
    """
    强制关闭所有 LibreOffice 进程（Windows 和 Linux/Mac）
    防止进程卡住或占用资源
    """
    try:
        system = platform.system()
        if system == 'Windows':
            # Windows: 使用 taskkill 命令
            subprocess.run(
                ['taskkill', '/F', '/IM', 'soffice.exe'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=5
            )
            subprocess.run(
                ['taskkill', '/F', '/IM', 'soffice.bin'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=5
            )
            subprocess.run(
                ['taskkill', '/F', '/IM', 'LibreOffice.exe'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=5
            )
            print(f" [清理] LibreOffice Windows 进程已清理")
        else:
            # Linux/Mac: 使用 pkill
            subprocess.run(
                ['pkill', '-9', 'soffice'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=5
            )
            print(f" [清理] LibreOffice 进程已清理")
    except Exception as e:
        print(f" [清理] 清理 LibreOffice 进程失败: {e}")


def convert_docx_to_pdf_base64(file_stream) -> str:
    """
    将 Word 文档转换为 PDF，返回 base64 编码
    使用 LibreOffice 转换，支持所有页面
    """
    # 重置流指针到开头（如果可能）
    try:
        file_stream.seek(0)
    except:
        pass
    
    # 复用 convert_docx_to_pdf_bytes 逻辑
    pdf_bytes = convert_docx_to_pdf_bytes(file_stream)
    
    if not pdf_bytes:
        return ""
    
    # 转换为 base64
    pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')
    return f"data:application/pdf;base64,{pdf_base64}"


def convert_pdf_to_images_imagemagick(pdf_path: str, tmpdir: str) -> List[str]:
    """
    使用 ImageMagick 将 PDF 转换为图片（备用方案）
    """
    try:
        # 使用 ImageMagick 的 convert 命令
        output_pattern = os.path.join(tmpdir, "page.png")
        cmd = [
            'convert',
            '-density', '200',  # DPI
            pdf_path,
            '-quality', '90',
            output_pattern
        ]
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30)
        
        # 收集生成的图片
        image_base64_list = []
        png_files = sorted([f for f in os.listdir(tmpdir) if f.startswith('page') and f.endswith('.png')])
        
        for filename in png_files:
            img_path = os.path.join(tmpdir, filename)
            with open(img_path, "rb") as img_file:
                img_base64 = base64.b64encode(img_file.read()).decode('utf-8')
                image_base64_list.append(f"data:image/png;base64,{img_base64}")
        
        print(f" ImageMagick 转换完成: {len(image_base64_list)} 张图片")
        return image_base64_list
        
    except FileNotFoundError:
        print(f" ImageMagick 未安装")
        return []
    except Exception as e:
        print(f" ImageMagick 转换失败: {e}")
        return []

def has_ms_word():
    try:
        import win32com.client
        word = win32com.client.Dispatch("Word.Application")
        word.Quit()
        return True
    except Exception:
        return False
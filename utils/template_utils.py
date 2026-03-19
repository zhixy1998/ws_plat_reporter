import os
import time
import tempfile
import platform
import threading
import importlib
import subprocess
import shutil
import base64, json
import typing
from io import BytesIO
from typing import List
from docx import Document
from docx.oxml.ns import qn
from docx2pdf import convert
from fastapi import UploadFile
from docx.oxml import OxmlElement
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError

try:
    import pywintypes  # type: ignore
except Exception:  # pragma: no cover
    pywintypes = None

from config import config
from app.db import execute_safe_sql
from utils.doc_converter import get_libreoffice_command, get_libreoffice_subprocess_kwargs, explain_libreoffice_returncode, get_libreoffice_timeout_seconds
from app.template_doc.model.template_doc import TemplateDoc
from constants.template_constant import MeasureMode


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

# 避免重复触发 Word COM 异常导致的卡死；一旦检测到 COM RPC 失败，本进程内禁用 docx2pdf
_docx2pdf_disabled = False

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


def _call_docx2pdf_with_com(docx_path: str, pdf_path: str) -> None:
    """调用 docx2pdf，必要时在线程内初始化 COM。"""
    pythoncom = None
    try:
        try:
            import pythoncom  # type: ignore
            pythoncom.CoInitialize()
        except Exception:
            pythoncom = None
        convert(docx_path, pdf_path)
    finally:
        try:
            if pythoncom:
                pythoncom.CoUninitialize()
        except Exception:
            pass


def _is_com_rpc_error(exc: BaseException) -> bool:
    """判断是否为 Windows COM RPC 失败（HRESULT 0x800706be = -2147023170）。"""
    # pywintypes.com_error typically has hresult attr
    hresult = getattr(exc, "hresult", None)
    if hresult is None and hasattr(exc, "args") and exc.args:
        # docx2pdf bubbles tuple (-2147023170, 'msg', None, None)
        first = exc.args[0]
        if isinstance(first, int):
            hresult = first
    return hresult == -2147023170


def _try_convert_with_docx2pdf(docx_path: str, pdf_path: str, timeout: int = 10) -> bool:
    """尝试在限定时间内通过 docx2pdf 转换，失败或超时返回 False。"""
    global _docx2pdf_disabled

    if _docx2pdf_disabled:
        return False

    try:
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(_call_docx2pdf_with_com, docx_path, pdf_path)
            future.result(timeout=timeout)

        if not os.path.exists(pdf_path):
            print("docx2pdf 转换失败：未生成 PDF 文件")
            return False

        if os.path.getsize(pdf_path) == 0:
            print("docx2pdf 转换失败：PDF 文件为空")
            return False

        return True

    except FuturesTimeoutError:
        print(f"docx2pdf 转换超过 {timeout} 秒，自动跳过")
    except Exception as exc:
        if _is_com_rpc_error(exc):
            print("docx2pdf 检测到 COM RPC 失败，禁用后续 docx2pdf 尝试，改用 LibreOffice")
            _docx2pdf_disabled = True
            return False
        print(f"docx2pdf 转换异常: {exc}")

    return False


def _try_convert_with_wps(docx_path: str, pdf_path: str, timeout: int = 15) -> bool:
    """尝试在限定时间内通过 WPS 转换，失败或超时返回 False。"""
    try:
        def wps_convert():
            import pythoncom
            pythoncom.CoInitialize()
            try:
                import win32com.client
                # KWPS.Application 表示 WPS 文字
                wps = win32com.client.DispatchEx("KWPS.Application")
                wps.Visible = False
                doc = wps.Documents.Open(os.path.abspath(docx_path), ReadOnly=True)
                # 17 是导出成 PDF 的格式代码
                doc.SaveAs(os.path.abspath(pdf_path), FileFormat=17)
                doc.Close(0)
                wps.Quit()
            finally:
                pythoncom.CoUninitialize()

        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(wps_convert)
            future.result(timeout=timeout)

        if not os.path.exists(pdf_path) or os.path.getsize(pdf_path) == 0:
            print("WPS 转换失败：PDF 文件为空或未生成")
            return False

        print("WPS 转换成功")
        return True
    except FuturesTimeoutError:
        print(f"WPS 转换超过 {timeout} 秒，自动跳过")
        return False
    except Exception as exc:
        print(f"WPS 转换异常: {exc}")
        return False

def _try_convert_docx_with_libreoffice(tmpdir, docx_path, pdf_path) -> bytes:
    print("调试：开始LibreOffice转换")
    
    # 检查文件和目录
    if not os.path.exists(docx_path):
        print("调试：DOCX文件不存在：" + docx_path)
        return b""
    
    print("调试：DOCX文件大小：" + str(os.path.getsize(docx_path)) + "字节")
    
    system = platform.system()
    if system == 'Windows':
        libreoffice_path = os.path.abspath(config.libre_office_path)
        if not os.path.exists(libreoffice_path):
            print("调试：LibreOffice可执行文件不存在：" + libreoffice_path)
            return b""
        print("调试：使用Windows LibreOffice：" + libreoffice_path)
    else:
        libreoffice_cmd = shutil.which('libreoffice') or shutil.which('soffice')
        if not libreoffice_cmd:
            print("调试：未找到 libreoffice/soffice 命令")
            return b""
        print("调试：找到LibreOffice命令：" + libreoffice_cmd)
    
    for attempt in range(2):
        try:
            print("调试：尝试转换，第" + str(attempt + 1) + "次")
            cmd = get_libreoffice_command(tmpdir, docx_path, 'pdf')
            print("调试：执行命令：" + str(cmd))

            result = subprocess.run(
                cmd, 
                check=True, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, 
                timeout=get_libreoffice_timeout_seconds(),
                **get_libreoffice_subprocess_kwargs(cmd)
            )

            stdout_text = result.stdout.decode('utf-8', errors='ignore').strip()
            stderr_text = result.stderr.decode('utf-8', errors='ignore').strip()
            if stdout_text:
                print("调试：LibreOffice输出：" + stdout_text)
            if stderr_text:
                print("调试：LibreOffice错误：" + stderr_text)

            time.sleep(0.5)

            # 检查PDF是否生成
            if not os.path.exists(pdf_path):
                print("调试：PDF文件未生成")
                if attempt == 0:
                    _kill_libreoffice_processes()
                    time.sleep(1)
                    continue
                return b""

            # 读取PDF文件
            with open(pdf_path, "rb") as pdf_file:
                pdf_bytes = pdf_file.read()

            if len(pdf_bytes) == 0:
                print("调试：PDF文件为空")
                if attempt == 0:
                    _kill_libreoffice_processes()
                    time.sleep(1)
                    continue
                return b""

            print("调试：PDF生成成功，大小：" + str(len(pdf_bytes)) + "字节")
            return pdf_bytes

        except subprocess.TimeoutExpired:
            print("调试：LibreOffice超时，第" + str(attempt + 1) + "次尝试")
            if attempt == 0:
                _kill_libreoffice_processes()
                time.sleep(2)
                continue
            return b""

        except subprocess.CalledProcessError as e:
            print("调试：LibreOffice执行失败，返回码：" + str(e.returncode))
            detail = explain_libreoffice_returncode(e.returncode)
            if detail:
                print("调试：" + detail)
            if e.stderr:
                print("调试：错误信息：" + e.stderr.decode('utf-8', errors='ignore'))
            if attempt == 0:
                _kill_libreoffice_processes()
                time.sleep(1)
                continue
            return b""

        except FileNotFoundError:
            print("调试：LibreOffice命令未找到")
            return b""

        except Exception as e:
            print("调试：转换异常：" + str(e))
            if attempt == 0:
                _kill_libreoffice_processes()
                time.sleep(1)
                continue
            return b""
    
    print("调试：所有尝试都失败了")
    return b""


def _do_convert_docx_to_pdf_bytes(doc_raw_bytes: bytes) -> bytes:
    """
    实际的转换逻辑（在锁内执行）
    """
    print("调试：开始转换，输入文件大小：" + str(len(doc_raw_bytes) if doc_raw_bytes else 0) + "字节")
    
    custom_tmp_root = config.deploy_python_path
    if custom_tmp_root is None:
        custom_tmp_root = tempfile.gettempdir()
    
    print("调试：使用临时目录：" + str(custom_tmp_root))
    
    try:
        os.makedirs(custom_tmp_root, exist_ok=True)
    except Exception as e:
        print("调试：创建临时目录失败：" + str(e))
        return b""
    
    if not os.access(custom_tmp_root, os.W_OK):
        print("调试：临时目录不可写")
        return b""
    
    try:
        with tempfile.TemporaryDirectory(dir=custom_tmp_root) as tmpdir:
            print("调试：创建临时目录：" + str(tmpdir))
            docx_path = os.path.join(tmpdir, "input.docx")
            pdf_path = os.path.join(tmpdir, "input.pdf")

            # 保存docx文件
            try:
                with open(docx_path, "wb") as f:
                    f.write(doc_raw_bytes)
                print("调试：DOCX文件写入成功")
            except Exception as e:
                print("调试：DOCX文件写入失败：" + str(e))
                return b""
            
            # 调用LibreOffice转换
            pdf_bytes = _try_convert_docx_with_libreoffice(tmpdir, docx_path, pdf_path)

            if pdf_bytes:
                print("调试：转换成功，返回PDF数据")
                return pdf_bytes
            
            print("调试：LibreOffice转换失败")
            system = platform.system()
            if system == 'Windows':
                print("调试：尝试Windows备用方案")
                if has_wps():
                    print("调试：检测到WPS，尝试使用WPS转换")
                    if _try_convert_with_wps(docx_path, pdf_path, timeout=15):
                        return open(pdf_path, "rb").read()
                
                if has_ms_word():
                    print("调试：没WPS或WPS失败，尝试使用MS Word转换")
                    if _try_convert_with_docx2pdf(docx_path, pdf_path, timeout=10):
                        return open(pdf_path, "rb").read()

            print("调试：所有转换方案都失败了")
            return b""
            
    except Exception as e:
        print("调试：临时目录创建失败：" + str(e))
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
    print("调试：开始转换DOCX到PDF，系统：" + platform.system())
    
    # 重置流指针到开头
    try:
        file_stream.seek(0)
    except Exception as e:
        print("调试：文件流重置失败：" + str(e))
    
    # 调用转换函数
    try:
        pdf_bytes = convert_docx_to_pdf_bytes(file_stream)
        print("调试：转换完成，PDF字节长度：" + str(len(pdf_bytes) if pdf_bytes else 0))
    except Exception as e:
        print("调试：转换异常：" + str(e))
        return ""
    
    if not pdf_bytes:
        print("调试：PDF转换失败，返回空字符串")
        return ""
    
    # 转换为 base64
    pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')
    print("调试：Base64编码完成，长度：" + str(len(pdf_base64)))
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


def has_wps():
    try:
        import win32com.client
        wps = win32com.client.Dispatch("KWPS.Application")
        wps.Quit()
        return True
    except Exception:
        return False

def get_title_mapping(template_name, measure_mode=None):
    common_title_mapping = {}
    private_title_mapping = {}
    
    # 再尝试加载私有 title_mapping（优先级更高）
    try:
        if measure_mode == MeasureMode.classic.value:
            private_module_path = config.classic_structure_module + "." + template_name
        else:
            private_module_path = config.structure_module + "." + template_name
        private_mod = importlib.import_module(private_module_path)
        if hasattr(private_mod, 'title_mapping'):
            private_title_mapping = private_mod.title_mapping
    except Exception as e:
        print(f"加载私有 title_mapping 失败: {e}")

    # 合并映射：私有的优先级更高
    # title_mapping = {**common_title_mapping, **private_title_mapping}
    return private_title_mapping


async def validate_python_file(content: str) -> tuple:
    """
    验证Python代码是否符合语法要求
    
    Args:
        content: Python代码字符串
        
    Returns:
        (is_valid, error_msg) 的元组
    """
    try:
        compile(content, '<string>', 'exec')
        return (True, '')
    except SyntaxError as e:
        error_msg = f'语法错误: {e.msg} (第{e.lineno}行)'
        return (False, error_msg)
    except Exception as e:
        return (False, f'验证失败: {str(e)}')
    except Exception as e:
        return {'valid': False, 'error': f'验证失败: {str(e)}'}



def remove_marker_rows(doc_stream: BytesIO, marker: str) -> BytesIO:
    """
    删除 Word 文档中包含指定标记的段落（文字行）。
        
    适用于左右分栏/分页场景：标记可能出现在左侧或右侧，
    只删除标记所在的那个段落，另一侧不受影响，下方内容自动上移。
        
    遍历文档中所有段落（包括表格单元格内的段落），
    找到包含 marker 的段落后直接从 XML 树中移除该段落元素。

    Args:
        doc_stream: Word文档流
        marker: 要查找的标记字符串

    Returns:
        BytesIO: 处理后的文档流
    """
    try:
        from docx import Document
        from lxml import etree
        doc_stream.seek(0)
        doc = Document(doc_stream)

        # 在整个文档 XML 中查找所有包含 marker 的段落元素 (w:p)
        # 这样无论段落在 body、表格单元格、页眉页脚中都能覆盖到
        nsmap = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
        body = doc.element.body
        # 查找所有 w:p 元素（递归）
        all_paragraphs = body.findall('.//w:p', nsmap)
            
        removed_count = 0
        for p_elem in all_paragraphs:
            # 拼出该段落的纯文本
            texts = p_elem.findall('.//w:t', nsmap)
            full_text = ''.join(t.text or '' for t in texts)
            if marker in full_text:
                parent = p_elem.getparent()
                if parent is not None:
                    parent.remove(p_elem)
                    removed_count += 1

        print(f"DEBUG remove_marker_rows: 共删除 {removed_count} 个包含标记的段落")

        output_stream = BytesIO()
        doc.save(output_stream)
        output_stream.seek(0)
        return output_stream

    except Exception as e:
        print(f"ERROR remove_marker_rows: {e}")
        doc_stream.seek(0)
        return doc_stream
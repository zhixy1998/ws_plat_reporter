import os
import tempfile
import platform
import threading
import importlib
import subprocess
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
from exceptions.error import ErrorCode
from exceptions.command_exception import APIException
from app.db import execute_safe_sql
from utils.doc_converter import get_libreoffice_command, get_libreoffice_timeout_seconds
from app.template_doc.model.template_doc import TemplateDoc
from constants.template_constant import MeasureMode, TemplateFootAndHeaderType


# ==================== 左中右页眉页脚 ====================

HEADER_KEYS = ['left_header', 'mid_header', 'right_header']
FOOTER_KEYS = ['left_footer', 'mid_footer', 'right_footer']

# TemplateFootAndHeaderType: left=2 center=1 right=0
_POS_VALUE_TO_CSS = {0: 'right', 1: 'center', 2: 'left'}


def normalize_position(position) -> str:
    """把各种 position 表示统一成 'left'/'center'/'right'。

    兼容：CSS 字符串（'left'）、描述文本（'左边展示'）、int value（0右/1中/2左）。
    无法识别返回空字符串。
    """
    if position is None:
        return ''
    if isinstance(position, bool):
        return ''
    if isinstance(position, int):
        return _POS_VALUE_TO_CSS.get(position, '')
    if isinstance(position, str):
        s = position.strip()
        if s in ('left', 'center', 'right'):
            return s
        decs_map = TemplateFootAndHeaderType.generate_decs_value_map()
        if s in decs_map:
            return _POS_VALUE_TO_CSS.get(decs_map[s], '')
    return ''


def resolve_header_footer_items(configs: dict, side: str, contexts: dict = None, name_to_var: dict = None, for_docx: bool = False) -> list:
    """
    把 6 个页眉页脚配置（left/mid/right）组装成渲染 list。

    side: 'header' | 'footer'
    contexts: 渲染上下文。type=0（关联字段）时从 contexts 取真实值；
              contexts=None 表示预览模式，取不到真实值就用 [字段名] 占位。
    name_to_var: {'字段名': '模板变量名'} 映射（如 {'样品状态': 'sample_status'}）。
    for_docx: True 时 type=0 关联字段写成 jinja 变量（{{ 变量 }}），供 DOCX 模板渲染时替换真实值。

    返回: [{'value': str, 'font': str, 'font_size': float, 'position': str}, ...]
    空配置/空值不返回。
    """
    items = []
    keys = HEADER_KEYS if side == 'header' else FOOTER_KEYS
    for key in keys:
        cfg = (configs or {}).get(key)
        if not isinstance(cfg, dict):
            continue
        value = cfg.get('value')
        if not value:
            continue
        _type = cfg.get('type')
        _type = 1 if _type is None else int(_type)
        if _type == 0:
            if for_docx and name_to_var and value in name_to_var:
                # DOCX 模板：写 jinja 变量，导出渲染时替换真实值
                display = '{{ ' + str(name_to_var[value]) + ' }}'
            else:
                # 从 contexts 取真实值，取不到用 [字段名] 占位（预览模式）
                real = (contexts or {}).get(value)
                display = str(real) if real not in (None, '') else f'[{value}]'
        else:
            display = str(value)
        if not display:
            continue
        default_pos = 'left' if 'left' in key else ('center' if 'mid' in key else 'right')
        pos = normalize_position(cfg.get('position'))
        items.append({
            'value': display,
            'font': cfg.get('font') or '宋体',
            'font_size': cfg.get('font_size') or 10,
            'position': pos or default_pos,
        })
    return items


def build_header_footer_context(extra_info: dict, side: str, contexts: dict = None) -> dict:
    """
    从 extra_info 构建 __header__ / __footer__ 渲染配置，兼容新旧两种格式。

    - 新格式：extra_info 有 left/mid/right 六个字段（list 形式渲染左中右三段）
    - 旧格式：只有单个 header/footer dict
    """
    configs = extra_info or {}
    items = resolve_header_footer_items(configs, side, contexts=contexts)
    if items:
        return {'value': '', 'font': '宋体', 'font_size': 10, 'position': 'left', 'items': items}
    # 旧格式回退
    old_key = 'header' if side == 'header' else 'footer'
    old_cfg = configs.get(old_key)
    if isinstance(old_cfg, dict) and old_cfg.get('value'):
        return dict(old_cfg)
    return {}


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
    try:
        doc = Document(doc_stream)
    except Exception as e:
        print(f"ERROR get_doc_obj_by_template_id: 模板 {template_id} 无法作为docx打开: {e}, content前100字节: {content_bytes[:100]}")
        raise APIException(ErrorCode.TEMPLATE_NOT_FOUND, f"模板文件已损坏或格式不正确，请联系管理员重新上传。模板ID: {template_id}")
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


def decode_template_html(template) -> str:
    """从 TemplateDoc 记录提取 HTML 模板字符串（base64 → 按常见编码解码）。"""
    content_b64 = template.template_content if template else None
    if not content_b64:
        return ''
    raw_bytes = base64.b64decode(content_b64)
    for enc in ('utf-8', 'gbk', 'gb2312', 'gb18030', 'latin-1'):
        try:
            return raw_bytes.decode(enc)
        except (UnicodeDecodeError, UnicodeError):
            continue
    return raw_bytes.decode('utf-8', errors='replace')


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

    if not os.path.exists(docx_path):
        print("调试：DOCX文件不存在：" + docx_path)
        return b""

    print("调试：DOCX文件大小：" + str(os.path.getsize(docx_path)) + "字节")

    cmd = get_libreoffice_command(tmpdir, docx_path, 'pdf')
    if not cmd:
        print("调试：未生成 LibreOffice 命令")
        return b""

    system = platform.system()
    if system == 'Windows':
        cmd[0] = os.path.abspath(cmd[0])
        if not os.path.exists(cmd[0]):
            print("调试：LibreOffice可执行文件不存在：" + cmd[0])
            return b""
        print("调试：使用Windows LibreOffice：" + cmd[0])

    print("调试：执行命令：" + str(cmd))

    run_kwargs = {
        'stdout': subprocess.PIPE,
        'stderr': subprocess.PIPE,
        'timeout': get_libreoffice_timeout_seconds(),
        'check': False,
    }

    try:
        result = subprocess.run(cmd, **run_kwargs)
    except subprocess.TimeoutExpired:
        print("调试：LibreOffice转换超时")
        _kill_libreoffice_processes()
        return b""
    except FileNotFoundError:
        print("调试：LibreOffice命令未找到")
        return b""
    except Exception as e:
        print("调试：LibreOffice转换异常：" + str(e))
        _kill_libreoffice_processes()
        return b""

    stdout_text = result.stdout.decode('utf-8', errors='ignore').strip()
    stderr_text = result.stderr.decode('utf-8', errors='ignore').strip()
    if stdout_text:
        print("调试：LibreOffice输出：" + stdout_text)
    if stderr_text:
        print("调试：LibreOffice错误：" + stderr_text)

    if result.returncode != 0:
        print("调试：LibreOffice执行失败，返回码：" + str(result.returncode))
        _kill_libreoffice_processes()
        return b""

    if not os.path.exists(pdf_path):
        print("调试：PDF文件未生成")
        return b""

    with open(pdf_path, "rb") as pdf_file:
        pdf_bytes = pdf_file.read()

    if not pdf_bytes:
        print("调试：PDF文件为空")
        return b""

    print("调试：PDF生成成功，大小：" + str(len(pdf_bytes)) + "字节")
    return pdf_bytes


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

def import_template_module(structure_module: str, template_name: str, reload: bool = False):
    """
    安全地导入模板配置模块，支持包含特殊字符（逗号、中文标点等）的模板名称。

    与 importlib.import_module() 不同，此函数通过文件路径加载模块，
    因此模板名称可以包含任意文件系统允许的字符。

    Args:
        structure_module: 父包的模块名，如 'template_structure' 或 'template_structure_classic'
        template_name: 模板名称（也是 .py 文件名，不含扩展名）
        reload: 是否强制重新加载（忽略缓存）

    Returns:
        加载的模块对象

    Raises:
        ModuleNotFoundError: 模块文件不存在时抛出
    """
    import importlib.util as _util
    import sys as _sys

    full_name = f"{structure_module}.{template_name}"

    # reload 时清除缓存
    if reload and full_name in _sys.modules:
        del _sys.modules[full_name]

    # 先从缓存取
    if full_name in _sys.modules:
        return _sys.modules[full_name]

    # 确保父包已加载
    if structure_module not in _sys.modules:
        importlib.import_module(structure_module)

    parent_pkg = _sys.modules[structure_module]
    base_dir = parent_pkg.__path__[0]
    file_path = os.path.join(base_dir, f"{template_name}.py")

    if not os.path.isfile(file_path):
        raise ModuleNotFoundError(f"No module named '{full_name}' (file not found: {file_path})")

    spec = _util.spec_from_file_location(full_name, file_path)
    if spec is None or spec.loader is None:
        raise ModuleNotFoundError(f"No module named '{full_name}' (could not create spec)")

    mod = _util.module_from_spec(spec)
    mod.__package__ = structure_module  # 支持模板内的相对导入（如 from .common_data import ...）
    _sys.modules[full_name] = mod
    try:
        spec.loader.exec_module(mod)
    except Exception:
        _sys.modules.pop(full_name, None)
        raise
    return mod


def get_title_mapping(template_name, measure_mode=None):
    common_title_mapping = {}
    private_title_mapping = {}
    
    # 再尝试加载私有 title_mapping（优先级更高）
    try:
        if measure_mode == MeasureMode.classic.value:
            structure_module = config.classic_structure_module
        else:
            structure_module = config.structure_module
        private_mod = import_template_module(structure_module, template_name)
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



def remove_marker_text(doc_stream: BytesIO, marker: str, val_marker: str) -> BytesIO:
    """
    精确删除 Word 文档中含有删除标记的 **文本内容**，而不是删除整个段落或表格行。

    设计思路：
    - 模板中 {{ 光度模式_t }} ： {{ 光度模式 }} 渲染后变成  __DEL_ROW__ ： __DEL_VAL__
    - 本函数只把 "__DEL_ROW__"、"__DEL_VAL__" 以及它们周围的分隔符（：、:、空格、制表符）
      从 run 文本中移除，段落本身保留不动。
    - 这样不会影响同一行的 {% if %} 控制标记，也不会破坏表格单元格结构。

    如果清理后整个段落**只剩空白**且不在表格单元格中，则删除该段落，
    避免留下无意义的空行。

    Args:
        doc_stream: Word文档流
        marker:     标题标记（如 __DEL_ROW__）
        val_marker: 值标记  （如 __DEL_VAL__）

    Returns:
        BytesIO: 处理后的文档流
    """
    import re as _re

    try:
        from docx import Document
        doc_stream.seek(0)
        doc = Document(doc_stream)

        nsmap = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
        body = doc.element.body

        # 需要清除的标记列表（过滤掉空字符串）
        markers = [m for m in [marker, val_marker] if m]

        # 构建正则：匹配 marker 及其前后紧挨的分隔符（：:、空格、制表符）
        # 例如 "__DEL_ROW__ ： __DEL_VAL__" -> ""
        # 例如 "__DEL_ROW__：__DEL_VAL__"   -> ""
        # 例如 "xxx __DEL_ROW__ ： __DEL_VAL__ yyy" -> "xxx  yyy"
        pattern_parts = []
        for m in markers:
            escaped = _re.escape(m)
            # 匹配: [前面的分隔符] + marker + [后面的分隔符]
            # 分隔符包括：空格、制表符、：、:
            pattern_parts.append(
                r'[\s：:]*' + escaped + r'[\s：:]*'
            )
        combined_pattern = _re.compile('|'.join(pattern_parts))

        all_paragraphs = body.findall('.//w:p', nsmap)

        cleaned_run_count = 0
        removed_para_count = 0

        for p_elem in all_paragraphs:
            t_elements = p_elem.findall('.//w:t', nsmap)
            full_text = ''.join(t.text or '' for t in t_elements)

            # 快速跳过：段落不含任何标记
            if not any(m in full_text for m in markers):
                continue

            # ---- 策略1: 尝试跨 run 拼接后替换，再回写 ----
            # docxtpl 渲染后，一个 marker 可能被拆到多个连续 run 里
            # 收集连续的 run 组，拼接文本后做替换，再分配回去

            # 获取段落下直属的所有 w:r 元素（保持顺序）
            run_elements = p_elem.findall('.//w:r', nsmap)
            if not run_elements:
                continue

            # 拼出所有 run 的完整文本和每个 run 的边界
            run_texts = []
            for r_elem in run_elements:
                t_in_run = r_elem.findall('.//w:t', nsmap)
                run_text = ''.join(t.text or '' for t in t_in_run)
                run_texts.append(run_text)

            joined = ''.join(run_texts)

            # 执行替换
            cleaned = combined_pattern.sub('', joined)

            if cleaned == joined:
                # 没有实际变化，跳过
                continue

            cleaned_run_count += 1

            # 把清理后的文本重新分配回各 run
            # 策略：第一个 run 拿到所有清理后文本，其余 run 清空
            for idx, r_elem in enumerate(run_elements):
                t_in_run = r_elem.findall('.//w:t', nsmap)
                if idx == 0:
                    if t_in_run:
                        t_in_run[0].text = cleaned
                        # 保留空格
                        t_in_run[0].set(
                            '{http://www.w3.org/XML/1998/namespace}space',
                            'preserve'
                        )
                        # 清空第一个 run 的其余 w:t
                        for extra_t in t_in_run[1:]:
                            extra_t.text = ''
                else:
                    for t_node in t_in_run:
                        t_node.text = ''

            # 如果清理后段落只剩空白，且不在表格单元格里，则删除整个段落
            if not cleaned.strip():
                parent = p_elem.getparent()
                if parent is not None:
                    parent_tag = parent.tag.split('}')[-1] if '}' in parent.tag else parent.tag
                    if parent_tag != 'tc':
                        # 不在表格单元格中，安全删除空段落
                        parent.remove(p_elem)
                        removed_para_count += 1

        print(f"DEBUG remove_marker_text: 清理了 {cleaned_run_count} 个段落的标记文本, "
              f"删除了 {removed_para_count} 个空段落")

        output_stream = BytesIO()
        doc.save(output_stream)
        output_stream.seek(0)
        return output_stream

    except Exception as e:
        print(f"ERROR remove_marker_text: {e}")
        doc_stream.seek(0)
        return doc_stream


# 保留旧函数名作为兼容别名
def remove_marker_rows(doc_stream: BytesIO, marker: str) -> BytesIO:
    """向后兼容：调用 remove_marker_text，val_marker 使用空字符串。"""
    return remove_marker_text(doc_stream, marker, '')
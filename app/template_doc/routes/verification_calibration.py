from jinja2 import Template
import requests
import os
import platform
import subprocess
import tempfile
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError
from io import BytesIO
from typing import Dict, Any
from datetime import datetime
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from docx import Document
from docxtpl import DocxTemplate
import base64

from config import config
from utils.log_decorator import log_response
from utils.verification_calibration_utils.verification_calibration_handle import InspectionAndCorrectionReport
from utils.doc_converter import get_libreoffice_command, get_libreoffice_subprocess_kwargs, explain_libreoffice_returncode
from app.template_doc.model.template_doc import TemplateDoc

router = APIRouter()
_docx2pdf_disabled = False  # 一旦检测到 RPC 失败则禁用 docx2pdf，改走 PowerShell/LibreOffice


def flatten_docx_for_conversion(file_path: str) -> str:
    """
    扁平化Word文档，清理复杂的XML标记（特别是sub_doc产生的嵌套结构）
    这有助于LibreOffice更好地处理文档转换
    
    Args:
        file_path: 原Word文档路径
        
    Returns:
        str: 扁平化后的Word文档路径
    """
    try:
        print(f"正在扁平化Word文档: {file_path}")
        
        # 用python-docx重新读取并保存，这会清理XML结构
        doc = Document(file_path)
        
        # 生成扁平化版本的文件名
        dir_name = os.path.dirname(file_path)
        base_name = os.path.splitext(os.path.basename(file_path))[0]
        flattened_path = os.path.join(dir_name, f"{base_name}_flattened.docx")
        
        # 重新保存，这会清理复杂的XML标记
        doc.save(flattened_path)
        
        print(f"扁平化完成: {flattened_path}")
        return flattened_path
        
    except Exception as e:
        print(f"扁平化失败，使用原文件: {e}")
        return file_path

def convert_docx_to_pdf_bytes_simple(docx_stream: BytesIO, output_dir: str, base_name: str) -> bytes:
    """使用 LibreOffice 将 docx 流转换为 pdf（无任何降级或回退）。"""
    output_dir = os.path.abspath(output_dir)
    os.makedirs(output_dir, exist_ok=True)

    with tempfile.NamedTemporaryFile(delete=False, suffix='.docx', dir=output_dir) as tmp_docx:
        tmp_docx.write(docx_stream.read())
        tmp_docx_path = tmp_docx.name

    pdf_path = os.path.join(output_dir, f"{base_name}.pdf")

    # 选择 LibreOffice 可执行文件
    cmd = get_libreoffice_command(output_dir, tmp_docx_path, 'pdf')

    if not cmd:
        raise FileNotFoundError('未找到 LibreOffice 可执行文件，请确认已安装并在 PATH 中')

    exe = cmd[0]
    if not isinstance(exe, str) or not os.path.exists(exe):
        raise FileNotFoundError(f"LibreOffice 可执行文件不存在: {exe}")

    print(f"LibreOffice 命令: {cmd}")
    print(f"输出目录: {output_dir}")
    print(f"临时DOCX: {tmp_docx_path}")

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120, **get_libreoffice_subprocess_kwargs(cmd))
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr)

    if result.returncode != 0:
        detail = explain_libreoffice_returncode(result.returncode)
        if detail:
            print(f"LibreOffice 诊断: {detail}")
        raise RuntimeError(f"LibreOffice 转换失败，返回码 {result.returncode}")

    if not os.path.exists(pdf_path) or os.path.getsize(pdf_path) == 0:
        raise RuntimeError('LibreOffice 转换后未生成 PDF 文件')

    with open(pdf_path, 'rb') as f:
        pdf_bytes = f.read()

    # 清理临时 docx（保留 pdf）
    try:
        os.remove(tmp_docx_path)
    except Exception:
        pass

    return pdf_bytes


def convert_docx_to_pdf_with_priority(docx_file_path: str) -> bytes:
    """
    按优先级尝试不同的PDF转换器：
    1. WPS (Mac/Windows/Linux)
    2. Microsoft Office (Windows/Mac)
    3. LibreOffice (Mac/Windows/Linux)
    
    Args:
        docx_file_path: 已保存的Word文档文件路径
        
    Returns:
        bytes: PDF字节流
        
    Raises:
        Exception: 所有转换器都失败时抛出异常
    """
    system = platform.system().lower()
    conversion_errors = []
    
    # 使用同一目录进行转换，避免权限问题
    output_dir = os.path.dirname(docx_file_path)
    base_name = os.path.splitext(os.path.basename(docx_file_path))[0]
    pdf_path = os.path.join(output_dir, f"{base_name}.pdf")
    
    print(f"使用工作目录: {output_dir}")
    print(f"Word文件: {docx_file_path}")
    print(f"目标PDF: {pdf_path}")
    
    # # 1. 尝试 WPS 转换
    # try:
    #     print("正在尝试 WPS 转换...")
    #     if _try_wps_conversion(docx_file_path, pdf_path, system):
    #         with open(pdf_path, 'rb') as f:
    #             return f.read()
    # except Exception as e:
    #     conversion_errors.append(f"WPS转换失败: {str(e)}")
    #     print(f"WPS转换失败: {e}")
    
    # 2. 尝试 Microsoft Office 转换（在macOS上暂时跳过权限问题）
    # if system != 'darwin':  # 非macOS系统才尝试Office
    #     try:
    #         print("正在尝试 Microsoft Office 转换...")
    #         if _try_office_conversion(docx_file_path, pdf_path, system):
    #             with open(pdf_path, 'rb') as f:
    #                 return f.read()
    #     except Exception as e:
    #         conversion_errors.append(f"Office转换失败: {str(e)}")
    #         print(f"Office转换失败: {e}")
    # else:
    #     print("macOS上跳过Office转换（权限问题）")
    
    # 3. 最后尝试 LibreOffice 转换（使用扁平化处理）
    try:
        print("正在尝试 LibreOffice 转换...")
        
        # 先扁平化文档，清理sub_doc产生的复杂XML结构
        flattened_docx_path = flatten_docx_for_conversion(docx_file_path)
        
        # 使用扁平化后的文档进行转换
        with open(flattened_docx_path, 'rb') as f:
            docx_bytes = f.read()
        docx_stream = BytesIO(docx_bytes)
        return convert_docx_to_pdf_bytes_simple(docx_stream, output_dir, base_name)
    except Exception as e:
        conversion_errors.append(f"LibreOffice转换失败: {str(e)}")
        print(f"LibreOffice转换失败: {e}")
    
    # 所有转换器都失败
    error_msg = "所有PDF转换器都失败了:\n" + "\n".join(conversion_errors)
    raise Exception(error_msg)


def _try_wps_conversion(docx_path: str, pdf_path: str, system: str) -> bool:
    """尝试使用 WPS 进行转换"""
    wps_commands = {
        'darwin': [  # macOS - WPS Office for Mac的命令行转换
            # 尝试使用osascript调用WPS进行转换（避免打开界面）
            ['osascript', '-e', f'''
                tell application "wpsoffice"
                    set theDoc to open POSIX file "{docx_path}"
                    export theDoc to POSIX file "{pdf_path}" as "PDF"
                    close theDoc
                    quit
                end tell
            '''],
            # 如果上述方法不行，直接跳过WPS（因为macOS版WPS可能不支持命令行转换）
        ],
        'windows': [  # Windows
            ['wps.exe', '/convert-to', 'pdf', f'/outdir:{os.path.dirname(pdf_path)}', docx_path],
            [r'C:\Program Files (x86)\Kingsoft\WPS Office\ksolaunch.exe', '--headless', '--convert-to', 'pdf', '--outdir', os.path.dirname(pdf_path), docx_path]
        ],
        'linux': [  # Linux
            ['wps', '--headless', '--convert-to', 'pdf', '--outdir', os.path.dirname(pdf_path), docx_path],
            ['/opt/kingsoft/wps-office/office6/wps', '--headless', '--convert-to', 'pdf', '--outdir', os.path.dirname(pdf_path), docx_path]
        ]
    }
    
    commands = wps_commands.get(system, [])
    
    # macOS上的WPS Office可能不支持命令行转换，直接返回False让它尝试下一个转换器
    if system == 'darwin':
        print("macOS上的WPS Office可能不支持无界面命令行转换，跳过...")
        return False
    
    for cmd in commands:
        try:
            exe = cmd[0]
            # 如果是绝对路径且不存在，直接跳过
            if os.path.isabs(exe) and not os.path.exists(exe):
                print(f"WPS 可执行文件不存在: {exe}")
                continue

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            if result.returncode == 0 and os.path.exists(pdf_path) and os.path.getsize(pdf_path) > 0:
                return True

            if result.stderr:
                print(f"WPS stderr: {result.stderr}")
            if result.stdout:
                print(f"WPS stdout: {result.stdout}")
        except FileNotFoundError:
            print(f"未找到 WPS 命令: {cmd[0]} (请确认 WPS 安装路径或加入 PATH)")
            continue
        except subprocess.TimeoutExpired:
            print(f"WPS 转换超时: {cmd}")
            continue
        except subprocess.CalledProcessError as e:
            print(f"WPS 转换失败: {e}")
            continue
    
    return False


def _call_docx2pdf_with_com(docx_path: str, pdf_path: str) -> None:
    """在线程内初始化 COM 后调用 docx2pdf。"""
    pythoncom = None
    try:
        try:
            import pythoncom  # type: ignore
            pythoncom.CoInitialize()
        except Exception:
            pythoncom = None
        from docx2pdf import convert
        convert(docx_path, pdf_path)
    finally:
        try:
            if pythoncom:
                pythoncom.CoUninitialize()
        except Exception:
            pass


def _is_rpc_error(exc: BaseException) -> bool:
    """检测 COM RPC 失败（0x800706BE / -2147023170）。"""
    hresult = getattr(exc, "hresult", None)
    if hresult is None and getattr(exc, "args", None):
        first = exc.args[0]
        if isinstance(first, int):
            hresult = first
    return hresult == -2147023170


def _try_office_conversion(docx_path: str, pdf_path: str, system: str) -> bool:
    """尝试使用 Microsoft Office 进行转换"""
    if system == 'windows':
        # Windows - 使用 COM 自动化或命令行
        global _docx2pdf_disabled
        if not _docx2pdf_disabled:
            try:
                with ThreadPoolExecutor(max_workers=1) as executor:
                    future = executor.submit(_call_docx2pdf_with_com, docx_path, pdf_path)
                    future.result(timeout=20)
                if os.path.exists(pdf_path) and os.path.getsize(pdf_path) > 0:
                    return True
                print("docx2pdf 运行后未生成有效 PDF，继续尝试 PowerShell")
            except FuturesTimeoutError:
                print("docx2pdf 超时，继续尝试 PowerShell")
            except Exception as e:
                if _is_rpc_error(e):
                    _docx2pdf_disabled = True
                    print("docx2pdf 检测到 RPC 失败，禁用后续 docx2pdf，改用 PowerShell")
                else:
                    print(f"docx2pdf 转换异常: {e}")
        
        # 尝试PowerShell脚本
        powershell_script = "; ".join([
            "$word = New-Object -ComObject Word.Application",
            "$word.Visible = $false",
            f"$doc = $word.Documents.Open(\"{docx_path}\")",
            f"$doc.SaveAs([ref]\"{pdf_path}\", [ref]17)",
            "$doc.Close()",
            "$word.Quit()"
        ])

        try:
            result = subprocess.run(
                ['powershell', '-NoLogo', '-NonInteractive', '-Command', powershell_script],
                capture_output=True, timeout=60, check=True
            )
            if result.stdout:
                print(result.stdout)
            if result.stderr:
                print(result.stderr)
            if os.path.exists(pdf_path) and os.path.getsize(pdf_path) > 0:
                return True
        except subprocess.CalledProcessError as e:
            # 若 Word 已经成功保存但退出返回非零，也允许通过
            if os.path.exists(pdf_path) and os.path.getsize(pdf_path) > 0:
                print("PowerShell 返回非零，但 PDF 已生成，忽略错误")
                return True
            print(f"PowerShell 转换失败: {e.stderr.decode('utf-8', errors='ignore') if hasattr(e, 'stderr') else e}")
        except subprocess.TimeoutExpired:
            print("PowerShell 转换超时")
        except Exception as e:
            print(e)
    
    elif system == 'darwin':
        # macOS - 使用 Microsoft Office for Mac
        office_commands = [
            ['/Applications/Microsoft Word.app/Contents/MacOS/Microsoft Word', '--headless', '--convert-to', 'pdf', '--outdir', os.path.dirname(pdf_path), docx_path],
        ]
        
        for cmd in office_commands:
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
                if result.returncode == 0 and os.path.exists(pdf_path) and os.path.getsize(pdf_path) > 0:
                    return True
            except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.CalledProcessError):
                continue
    
    return False


class VerificationCalibrationInputSchema(BaseModel):
    """验证校准请求数据模型"""
    task_id: str = Field(..., description='任务id')
    sample_id: Dict[str, Any] = Field(None, description='样品id')
    template_id: int = Field(..., description='模板id')


@router.post('/verification_calibration')
@log_response
async def verification_calibration(data: VerificationCalibrationInputSchema):
    """
    验证校准接口
    
    Args:
        data: 包含校准ID和验证数据的请求体
        
    Returns:
        JSON响应，包含code、message和pdf数据（base64格式）
    """
    try:
        task_id = data.task_id
        sample_id = data.sample_id
        template_id = data.template_id
        
        template_instance = await TemplateDoc.get(id=template_id, is_del=0)
        template_content = template_instance.template_content  # base64编码的内容
        # 解码base64为字节流
        doc_bytes = base64.b64decode(template_content)
        doc_stream = BytesIO(doc_bytes)
        # 使用DocxTemplate而不是Template
        template = DocxTemplate(doc_stream)

        verification_calibration_url = config.verification_calibration_url
        request_url  = verification_calibration_url + f'?taskId={task_id}'
        res = requests.get(request_url)
        res_json = res.json()

        # 生成Word文档流
        iar = InspectionAndCorrectionReport(doc=template, vc_data_list=res_json.get('data').get('worksheets'))
        docx_out_stream = iar.run()
        
        # 保存文件到本地
        current_dir = os.path.dirname(os.path.abspath(__file__))
        output_dir = os.path.join(current_dir, '../../../output/verification_calibration')
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # 先保存Word文件（用于调试）
        docx_out_stream.seek(0)
        docx_bytes = docx_out_stream.read()
        docx_filename = os.path.join(output_dir, f'verification_and_calibration_{task_id}_{timestamp}.docx')
        with open(docx_filename, 'wb') as f:
            f.write(docx_bytes)
        print(f"Word文档已保存至: {docx_filename}")
        
        # 使用已保存的Word文件进行PDF转换
        # pdf_bytes = convert_docx_to_pdf_with_priority(docx_filename)
        
        # # 保存PDF到本地
        # pdf_filename = os.path.join(output_dir, f'verification_and_calibration_{task_id}_{timestamp}.pdf')
        
        # with open(pdf_filename, 'wb') as f:
        #     f.write(pdf_bytes)
        
        # # 将PDF字节流转换为base64用于返回
        # import base64
        # pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')
        
        # print(f"验证校准成功, PDF已保存至: {pdf_filename}")
        # print(f"Verification Calibration Response: {res_json.get('data').get('worksheets')}")

        # 返回 docx 文件流给前端（作为附件下载）
        def file_iterator(path, chunk_size=8192):
            with open(path, 'rb') as fh:
                while True:
                    chunk = fh.read(chunk_size)
                    if not chunk:
                        break
                    yield chunk

        headers = {
            'Content-Disposition': f'attachment; filename="{os.path.basename(docx_filename)}"'
        }
        return StreamingResponse(file_iterator(docx_filename), media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document', headers=headers)
    except Exception as e:
        import traceback
        
        # 获取调用栈字符串
        error_traceback = traceback.format_exc()
        
        # 同时使用print和logging，确保在各种环境下都能看到
        print(f"验证校准失败: {str(e)}")
        print('调用栈：')
        print(error_traceback)
        return {
            'code': 500,
            'message': f'验证校准失败: {str(e)}',
            'data': {}
        }
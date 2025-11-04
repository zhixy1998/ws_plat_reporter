import os
import base64
import tempfile
import subprocess
from io import BytesIO
from typing import List, Optional
from pathlib import Path

from tortoise import connections
from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from exceptions.error import ErrorCode
from utils.log_decorator import log_response
from constants.template_constant import TemplateType
from exceptions.command_exception import APIException
from app.template_doc.model.template_doc import TemplateDoc
from utils.template_utils import get_doc_name_and_doc_stream_obj
from utils.doc_converter import get_libreoffice_command
from utils.classic_fille_template_utils_simple import ClassicFillDataUtils
from .classic_export_original_data_doc_view import get_measure_type

router = APIRouter()


class InputSchema(BaseModel):
    template_id: int = Field(..., description='模板id')
    task_id: str = Field(..., description='任务id')
    sample_id: str = Field(None, description='样品id')
    analysis_id: str = Field(None, description='分析id')
    all_display: int = Field(0, description='Abs和T%是否显示')
    serial_number: str = Field(None, description='样品序号')
    digit: int = Field(None, description='保留小数位数')
    image_base64: str = Field(None, description='图片base64')

@router.post('/preview_template')
@log_response
async def preview_template(data: InputSchema):
    """预览模板，将docx转换为PDF的base64返回"""
    classic_db_con = connections.get('classic_db')
    template_id = data.template_id
    task_id = data.task_id
    sample_id = data.sample_id
    serial_number = data.serial_number

    # 直接获取文件流，更简单
    measure_type = await get_measure_type(task_id)
    if template_id is None:
        raise APIException(ErrorCode.TEMPLATE_NOT_FOUND)
    original_template_name, original_doc_stream_obj = await get_doc_name_and_doc_stream_obj(template_id=template_id, conn=classic_db_con)
    fill_data_instance_original = ClassicFillDataUtils(original_template_name, template_id=template_id, measure_type=measure_type)
    original_doc_stream_obj = await fill_data_instance_original.fill_data(doc_stream=original_doc_stream_obj, task_id=task_id, sample_id=sample_id, 
        serial_number=serial_number, image_base64=data.image_base64, analysis_id=data.analysis_id, all_display=data.all_display, digit=data.digit)
    
    # 转换为PDF
    pdf_base64 = convert_docx_to_pdf_base64(original_doc_stream_obj)
    
    return {
        'code': 200,
        'message': '预览成功',
        'data': {'pdf': pdf_base64}
    }


@router.post('/preview_template_download')
async def preview_template_download(data: InputSchema):
    """
    预览模板，将docx转换为PDF并直接返回文件下载（调试用）
    """
    classic_db_con = connections.get('classic_db')
    template_id = data.template_id
    task_id = data.task_id
    sample_id = data.sample_id
    serial_number = data.serial_number

    # 直接获取文件流，更简单
    measure_type = await get_measure_type(task_id)
    if template_id is None:
        raise APIException(ErrorCode.TEMPLATE_NOT_FOUND)
    original_template_name, original_doc_stream_obj = await get_doc_name_and_doc_stream_obj(template_id=template_id, conn=classic_db_con)
    fill_data_instance_original = ClassicFillDataUtils(original_template_name, template_id=template_id, measure_type=measure_type)
    original_doc_stream_obj = await fill_data_instance_original.fill_data(doc_stream=original_doc_stream_obj, task_id=task_id, sample_id=sample_id, 
                             serial_number=serial_number, image_base64=data.image_base64, analysis_id=data.analysis_id, all_display=data.all_display)
    
    # 转换为PDF（返回字节流）
    pdf_bytes = convert_docx_to_pdf_bytes(original_doc_stream_obj)
    
    if not pdf_bytes:
        raise APIException(ErrorCode.INTERNAL_ERROR, "PDF转换失败")
    
    # 生成文件名（处理中文编码）
    from urllib.parse import quote
    filename = f"{original_template_name}_{task_id}.pdf"
    encoded_filename = quote(filename)
    
    # 返回文件下载
    return StreamingResponse(
        BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"
        }
    )


def convert_docx_to_pdf_bytes(file_stream) -> bytes:
    """
    将 Word 文档转换为 PDF，返回字节流（用于文件下载）
    使用 LibreOffice 转换，支持所有页面
    """
    # 重置流指针到开头（如果可能）
    try:
        file_stream.seek(0)
    except:
        pass
    
    doc_raw_bytes = file_stream.read()
    with tempfile.TemporaryDirectory() as tmpdir:
        docx_path = os.path.join(tmpdir, "input.docx")
        pdf_path = os.path.join(tmpdir, "input.pdf")
        
        # 保存 docx 文件
        with open(docx_path, "wb") as f:
            f.write(doc_raw_bytes)
        
        try:
            # 使用 LibreOffice 转换为 PDF
            print(f" [DEBUG] DOCX → PDF 转换开始...")
            cmd = get_libreoffice_command(tmpdir, docx_path, 'pdf')
            result = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30)
            
            # 检查 PDF 是否生成
            if not os.path.exists(pdf_path):
                print(f" PDF 生成失败")
                return b""
            
            # 读取 PDF 文件
            with open(pdf_path, "rb") as pdf_file:
                pdf_bytes = pdf_file.read()
                
            print(f" [DEBUG] PDF 生成成功: {len(pdf_bytes)} bytes")
            return pdf_bytes
            
        except subprocess.CalledProcessError as e:
            print(f" LibreOffice 转换失败: {e}")
            return b""
        except Exception as e:
            print(f" 转换过程出错: {e}")
            import traceback
            traceback.print_exc()
            return b""


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


def classic_convert_docx_to_images_base64(file_stream) -> List[str]:
    """
    将Word文档转换为图片列表，返回base64编码列表
    适用于预览功能，保持格式完整性
    
    转换流程：Word → PDF → PNG (支持多页)
    原因：LibreOffice 直接转 PNG 只能转第一页
    """
    doc_raw_bytes = file_stream.read()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        docx_path = os.path.join(tmpdir, "input.docx")
        pdf_path = os.path.join(tmpdir, "input.pdf")
        
        # 保存docx文件
        with open(docx_path, "wb") as f:
            f.write(doc_raw_bytes)
        
        try:
            # 步骤1：先转换为 PDF（保留所有页）
            print(f" [DEBUG] 步骤1: DOCX → PDF")
            cmd_pdf = get_libreoffice_command(tmpdir, docx_path, 'pdf')
            subprocess.run(cmd_pdf, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30)
            
            if not os.path.exists(pdf_path):
                print(f" PDF 生成失败")
                return []
            
            print(f" PDF 生成成功: {os.path.getsize(pdf_path)} bytes")
            
            # 步骤2：使用 pdf2image 将 PDF 转换为图片
            try:
                from pdf2image import convert_from_path
                print(f"  [DEBUG] 步骤2: PDF → PNG (使用 pdf2image)")
                
                # 转换 PDF 的所有页为图片
                images = convert_from_path(pdf_path, dpi=200)  # 200 DPI 保证清晰度
                
                image_base64_list = []
                for i, image in enumerate(images):
                    # 将 PIL Image 转换为 base64
                    img_buffer = BytesIO()
                    image.save(img_buffer, format='PNG', optimize=True)
                    img_buffer.seek(0)
                    img_base64 = base64.b64encode(img_buffer.read()).decode('utf-8')
                    image_base64_list.append(f"data:image/png;base64,{img_base64}")
                    print(f"  ✓ 第 {i+1} 页转换完成")
                
                print(f" [DEBUG] 最终返回 {len(image_base64_list)} 张图片")
                return image_base64_list
                
            except ImportError:
                print(f"  pdf2image 未安装，尝试使用 ImageMagick")
                # 备用方案：使用 ImageMagick
                return convert_pdf_to_images_imagemagick(pdf_path, tmpdir)
            
        except subprocess.CalledProcessError as e:
            print(f" LibreOffice 转换失败: {e}")
            return []
        except Exception as e:
            print(f" 转换过程出错: {e}")
            import traceback
            traceback.print_exc()
            return []


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
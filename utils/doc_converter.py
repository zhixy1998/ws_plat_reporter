"""
DOC到DOCX转换工具
使用LibreOffice实现真正的DOC转DOCX转换
支持跨平台（Mac/Linux/Windows）
"""

import os
import tempfile
import platform
import subprocess
import subprocess
from pathlib import Path
from io import BytesIO
from config import config

def detect_file_format(file_content: bytes) -> str:
    """
    检测文件格式
    """
    # DOC文件的魔术字节
    if file_content.startswith(b'\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1'):
        return 'doc'
    # DOCX文件的魔术字节 (ZIP格式)
    elif file_content.startswith(b'PK\x03\x04') or file_content.startswith(b'PK\x05\x06'):
        return 'docx'
    else:
        return 'unknown'

def _build_user_installation_uri(temp_dir: str) -> str:
    profile_dir = Path(temp_dir).resolve() / 'libreoffice-profile'
    profile_dir.mkdir(parents=True, exist_ok=True)
    return profile_dir.as_uri()


def get_libreoffice_subprocess_kwargs(command: list) -> dict:
    """为 Windows 便携版 LibreOffice 提供稳定的启动目录和 PATH。"""
    if platform.system() != 'Windows' or not command:
        return {}

    executable = command[0]
    if not isinstance(executable, str):
        return {}

    executable = os.path.abspath(executable)
    program_dir = os.path.dirname(executable)
    env = os.environ.copy()
    env['PATH'] = program_dir + os.pathsep + env.get('PATH', '')
    return {
        'cwd': program_dir,
        'env': env,
    }


def explain_libreoffice_returncode(returncode: int) -> str:
    """将 Windows 进程退出码转换为可读诊断。"""
    unsigned_code = returncode & 0xFFFFFFFF
    if unsigned_code == 0xE06D7363:
        return 'LibreOffice 在启动阶段抛出 Windows C++ 未处理异常，常见于便携版依赖/用户配置目录/运行目录不正确。'
    if unsigned_code == 0xC0000135:
        return 'LibreOffice 缺少运行依赖 DLL，进程未能正常启动。'
    if unsigned_code == 0xC0000142:
        return 'LibreOffice 初始化失败，通常与运行环境或依赖加载有关。'
    return ''


# 判断当前操作系统
def get_libreoffice_command(temp_dir: str, doc_path: str,aim :str ) -> list:
    """
    根据操作系统类型返回相应的LibreOffice转换命令
    Args:
        temp_dir: 输出目录路径
        doc_path: 输入DOC文件路径
        convert-to: 目标文件格式
    Returns:
        命令参数列表
    """
    system = platform.system()
    if system in ['Darwin']:
        command = [
            'soffice', 
            '--headless',
            '--norestore',
            '--nologo',
            '--nofirststartwizard',
            '--convert-to', aim,
            '--outdir', temp_dir,
            doc_path
        ]
    elif system in ['Windows']:
        libreoffice_path = os.path.abspath(config.libre_office_path)
        user_installation = _build_user_installation_uri(temp_dir)
        print(f"LibreOffice路径: {libreoffice_path}")
        print(f"LibreOffice用户目录: {user_installation}")
        command = [
            libreoffice_path, 
            '--headless',
            '--norestore',
            '--nodefault',
            '--nolockcheck',
            '--nologo',
            '--nofirststartwizard',
            f'-env:UserInstallation={user_installation}',
            '--convert-to', aim,
            '--outdir', os.path.abspath(temp_dir),
            os.path.abspath(doc_path)
        ]

    elif system in ['Linux']:  # macOS 或 Linux
        command = [
            'libreoffice', 
            '--headless',
            '--norestore',
            '--nologo',
            '--nofirststartwizard',
            '--convert-to', aim,
            '--outdir', temp_dir,
            doc_path
        ]
    else:
        raise ValueError(f"不支持本机操作系统,请另存为.docx文件后再保存: {system}")
    return command

def convert_doc_to_docx_libreoffice(doc_content: bytes) -> BytesIO:
    """
    使用LibreOffice转换DOC文件到DOCX
    """
    try:
        # 创建临时目录
        with tempfile.TemporaryDirectory() as temp_dir:
            # 写入DOC文件
            doc_path = os.path.join(temp_dir, 'input.doc')
            with open(doc_path, 'wb') as f:
                f.write(doc_content)
            
            # 使用LibreOffice转换
            print(f" 使用LibreOffice转换DOC文件...")
            
            # LibreOffice命令行转换
            cmd=get_libreoffice_command(temp_dir,doc_path,'docx')
            # cmd = [
            #     'soffice',
            #     #'libreoffice',
            #     '--headless',
            #     '--convert-to', 'docx',
            #     '--outdir', temp_dir,
            #     doc_path
            # ]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,  # 30秒超时
                **get_libreoffice_subprocess_kwargs(cmd)
            )
            
            if result.returncode != 0:
                detail = explain_libreoffice_returncode(result.returncode)
                if detail:
                    print(f"LibreOffice诊断: {detail}")
                raise Exception(f"LibreOffice转换失败: {result.stderr}")
            
            # 读取转换后的DOCX文件
            docx_path = os.path.join(temp_dir, 'input.docx')
            
            if not os.path.exists(docx_path):
                raise Exception("LibreOffice转换完成但未找到输出文件")
            
            with open(docx_path, 'rb') as f:
                docx_content = f.read()
            
            print(f" LibreOffice转换成功，DOCX大小: {len(docx_content)} 字节")
            
            return BytesIO(docx_content)
            
    except subprocess.TimeoutExpired:
        raise Exception("LibreOffice转换超时（30秒）")
    except FileNotFoundError as e:
        print(e)
        raise Exception("LibreOffice未安装，请安装LibreOffice")
    except Exception as e:
        raise Exception(f"LibreOffice转换失败: {str(e)}")

def convert_doc_to_docx(doc_content: bytes) -> BytesIO:
    """
    主转换函数，使用LibreOffice转换DOC到DOCX
    
    Args:
        doc_content: DOC文件的字节内容
    
    Returns:
        转换后的DOCX文件BytesIO对象
    """
    
    # 检测文件格式
    file_format = detect_file_format(doc_content)
    
    if file_format == 'docx':
        # 已经是DOCX格式，直接返回
        print(" 文件已经是DOCX格式")
        return BytesIO(doc_content)
    elif file_format != 'doc':
        raise ValueError("不支持的文件格式，请上传DOC或DOCX文件")
    
    print(f" 检测到DOC文件，大小: {len(doc_content)} 字节")
    
    # 使用LibreOffice转换
    return convert_doc_to_docx_libreoffice(doc_content)

# 使用示例
if __name__ == "__main__":
    print("DOC转DOCX转换工具 - 使用LibreOffice")
    print("需要安装LibreOffice: https://www.libreoffice.org/download/")
    print("Mac: brew install --cask libreoffice")
    print("Ubuntu: sudo apt-get install libreoffice")
    print("Windows: 下载安装包")

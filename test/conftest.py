import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pytest
import asyncio
from urllib.parse import urlparse
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from app.main import app
from tortoise import Tortoise
from app.template_doc.model.template_doc import TemplateDoc
from app.template_doc.model.template_bookmark import TemplateBookmark
from app.template_doc.model.template_extra_info import TemplateExtraInfo
from app.template_doc.model.template_doc_base import TemplateDocBase
from app.template_doc.model.bookmark_data import BookmarkData

# 加载环境变量
load_dotenv(override=True)


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """设置测试数据库，测试前检查数据库名称并清空相关表"""
    # 从 DB_URL 中解析数据库名称
    db_url = os.getenv("DB_URL")
    if not db_url:
        pytest.exit("测试终止：未找到 DB_URL 环境变量", returncode=1)
    
    # 解析数据库URL获取数据库名称
    parsed_url = urlparse(db_url)
    current_db = parsed_url.path.lstrip('/')  # 移除开头的 '/'
    
    print(f"🔍 从DB_URL解析的数据库名称: {current_db}")
    
    # 定义允许的测试数据库名称
    allowed_test_dbs = ["t800_uv_inexus_test"]
    
    # 检查是否为测试数据库
    if current_db not in allowed_test_dbs:
        print(f" 错误: 当前数据库 '{current_db}' 不是测试数据库")
        print(f"   允许的测试数据库: {allowed_test_dbs}")
        print(f"   当前DB_URL: {db_url}")
        pytest.exit("测试终止：数据库名称不符合测试要求", returncode=1)
    
    print(f" 数据库名称验证通过: {current_db}")
    
    # 等待数据库初始化后再清空数据
    yield

@pytest.fixture(scope="session")
def client():
    """同步 TestClient，使用应用 lifespan 自动初始化数据库"""
    with TestClient(app) as c:
        yield c



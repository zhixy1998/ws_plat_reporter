import pytest,sys
import os
import uuid
from app.db import init_db  # ✅ 导入你现有的数据库初始化方法
from app.template_doc.model.template_doc import TemplateDoc

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

sys.path.append(BASE_DIR)

@pytest.mark.order(1)
def test_upload_template_success(client, request):

    """测试模板上传成功 - 直接使用测试数据库"""
    # 使用真实的测试文件
    current_dir = os.path.dirname(__file__)
    test_file_path = os.path.join(current_dir, "test_template.docx")
    
    if not os.path.exists(test_file_path):
        pytest.skip(f"测试文件不存在: {test_file_path}")
    
    # 生成随机模板名称，避免重复
    random_suffix = str(uuid.uuid4())[:8]
    template_name = f"测试模板_{random_suffix}"
    
    with open(test_file_path, "rb") as f:
        files = {
            "file": ("test_template.docx", f, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        }
        data = {
            "name": template_name,
            "template_type": 0
        }
        response = client.post("/template/upload_template", files=files, data=data)
    
    assert response.status_code == 200
    result = response.json()
    assert result["code"] == 200
    print('create_result==============', result)
    # 尝试保存模板ID，供后续用例读取
    try:
        template_id = (
            result.get("data", {}).get("id")
            if isinstance(result.get("data"), dict)
            else None
        )
        if template_id:
            request.config.cache.set("template_id", str(template_id))
    except Exception:
        pass
    
    print(f"✅ 测试完成: 模板上传成功")
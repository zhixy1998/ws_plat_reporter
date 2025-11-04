import pytest
from typing import Optional


@pytest.mark.order(2)
def test_get_bookmarks_simple(client, request):
    """测试获取书签接口 - 同步版本"""
    template_id: Optional[str] = request.config.cache.get("template_id", None)
    if not template_id:
        pytest.skip("未获取到模板ID（依赖上传用例写入缓存），跳过书签用例")
    print(f"使用模板ID: {template_id}")

    response = client.get(f"/template/get_bookmark?template_id={template_id}")

    result = response.json()
    assert result["code"] == 200

    print(f" 书签测试成功: 模板ID {template_id} 的API响应正常")

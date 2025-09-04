
import pytest
from typing import Optional


@pytest.mark.order(3)
def test_get_report_template(client, request):
    """测试获取书签接口 - 同步版本"""
    template_name: Optional[str] = request.config.cache.get("template_name", None)
    template_id: Optional[str] = request.config.cache.get("template_id", None)
    if not template_name:
        pytest.skip("未获取到模板name（依赖上传用例写入缓存），跳过获取报告模版用例")

    response = client.get(f"/template/get_report_template?desc=1")

    result = response.json()
    assert result["code"] == 200
    assert result['data']['template_list'][0]['name'] == template_name
    assert result['data']['template_list'][0]['id'] == int(template_id)

    print(f"✅ 书签测试成功: 模板名称 {template_name} 的API响应正常")
import pytest
from typing import Optional
from urls import TOTAL_TEMPLATE_URL

@pytest.mark.order(5)
def test_get_template_industry(client, request):
    """测试获取书签接口 - 同步版本"""
    response = client.get(TOTAL_TEMPLATE_URL)
    result = response.json()
    assert result["code"] == 200
    sum_template_count = result['data']['sum_count']
    request.config.cache.set("sum_template_count", sum_template_count)

    
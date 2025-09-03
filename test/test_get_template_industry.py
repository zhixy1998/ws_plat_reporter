
import pytest
from typing import Optional


@pytest.mark.order(6)
def test_get_template_industry(client, request):
    """测试获取书签接口 - 同步版本"""
    response = client.get(f"/template/get_template_industry")

    result = response.json()
    assert result["code"] == 200
    

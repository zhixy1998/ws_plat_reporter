
import pytest
from typing import Optional
from urls import TOTAL_TEMPLATE_URL


@pytest.mark.order(7)
def test_del_template(client, request):
    template_id: Optional[str] = request.config.cache.get("template_id", None)
    response = client.post(f"/template/del_template", json={"id": template_id})

    result = response.json()
    assert result["code"] == 200

    old_sum_template_count: Optional[str] = request.config.cache.get("sum_template_count", None)


    response = client.get(TOTAL_TEMPLATE_URL)
    result = response.json()
    assert result["code"] == 200
    sum_template_count = result['data']['sum_count']
    assert sum_template_count == old_sum_template_count - 1

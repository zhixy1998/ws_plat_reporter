"""
更新模版
现在支持: 名字
"""

import pytest, uuid
from typing import Optional


@pytest.mark.order(4)
def test_update_template(client, request):
    """测试更新模板接口"""
    template_id: Optional[str] = request.config.cache.get("template_id", None)
    if not template_id:
        pytest.skip("未获取到模板ID（依赖上传用例写入缓存），跳过更新用例")
    print(f"使用模板ID: {template_id}")

    random_suffix = str(uuid.uuid4())[:8]
    new_template_name = f"修改模版新名称_{random_suffix}"
    print(f"使用模板名称: {new_template_name}")
    response = client.post(f"/template/update_template", json={"id": template_id, "name": new_template_name})

    result = response.json()
    assert result["code"] == 200


    response = client.get(f"/template/get_report_template?desc=1")

    result = response.json()
    assert result["code"] == 200
    assert result['data']['template_list'][0]['name'] == new_template_name
    assert result['data']['template_list'][0]['id'] == int(template_id)

    print(f" 更新模板测试成功: 模板ID {template_id} 的API响应正常")

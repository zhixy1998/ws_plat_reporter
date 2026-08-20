import asyncio
import os
import random
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)

from app.db import init_db
from app.template_doc.model.template_doc import TemplateDoc
from app.template_doc.model.template_doc_base import TemplateDocBase
from constants.template_constant import TemplateType, ExperimentType

# ====== 可修改配置 ======
INDUSTRY_LIST = [""]


async def run():
    await init_db()

    # 过滤：向导模式数据库 + 报告模版（原始记录） + 定量测定
    bases = await TemplateDocBase.filter(
        type=TemplateType.report_template.value,
        experiment_type=ExperimentType.quantitative_determination.value,
        is_del=0,
    ).all()

    if not bases:
        print("未找到任何匹配模板")
        return

    print(f"找到 {len(bases)} 个原始记录定量模板，开始随机分配行业...")

    for base in bases:
        industry = random.choice(INDUSTRY_LIST)
        base.industry_type = industry
        await base.save()

        docs = await TemplateDoc.filter(base_template_id=base.id).all()
        for doc in docs:
            doc.industry_type = industry
            await doc.save()

        print(f"  ✓ {base.name} → {industry}")

    print(f"\n完成，共更新 {len(bases)} 个模板")


if __name__ == "__main__":
    asyncio.run(run())

import asyncio
import os
import sys
import random
""""
要在项目根目录执行 python scripts/one_time/chang_industry_type.py  类似这样
"""
# 加入项目根目录到 sys.path，确保可以导入 app.o
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

sys.path.append(BASE_DIR)

from app.db import init_db  #  导入你现有的数据库初始化方法
from app.template_doc.model.template_doc import TemplateDoc

async def run():
    items = ['食品', '环境', '医药', '土壤', '水质', '空气', '其他']
    await init_db()  #  初始化数据库连接

    # 示例逻辑：修改名字中含“测试”的模板
    templates = await TemplateDoc.all()
    for t in templates:
        t.industry_type = random.choice(items)
        await t.save()
    
    print(f"处理了 {len(templates)} 个模板")

if __name__ == "__main__":
    asyncio.run(run())

import asyncio
import os
import random
import sys

from tortoise.fields import base
from tortoise.transactions import in_transaction

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)

from app.db import init_db
from app.template_doc.model.template_doc import TemplateDoc
from app.template_doc.model.template_doc_base import TemplateDocBase
from app.template_doc.model.template_bookmark import TemplateBookmark
from app.template_doc.model.template_extra_info import TemplateExtraInfo
from config import config

# ====== 可修改配置 ======
# 行业列表
INDUSTRY_LIST = ["环境监测", "水质检测", "土壤分析", "大气检测", "食品安全"]

async def run():
    await init_db()  # 初始化数据库连接
    """
    亚硝酸盐_萘乙二胺分光光度法_原始记录报告模板
    六价铬二苯碳酰二肼分光光度法测定报告模板
    总氮过硫酸钾氧化法原始记录报告模板
    氨氮_纳氏试剂分光光度法_原始记录报告模板
    挥发酚_萃取分光光度法_原始记录报告模板
    甲醛_氨基_联氨_巯基分光光度法测定原始记录报告模板
    甲醛_乙酰丙酮分光光度法测定原始记录报告模板
    氰化物_异烟酸_吡唑啉酮分光光度法测定原始记录报告模板
    总氮_碱性过硫酸钾消解紫外分光光度法测定原始记录报告模板
    硼_姜黄素分光光度法测定原始记录报告模板
    氮氧化物_盐酸萘乙二胺分光光度法测定原始记录报告模板
    氨氮_纳氏试剂分光光度法_氨氮_水杨酸分光光度法测定_原始记录报告模板
    """

    template_name_list = ["硫酸盐_铬酸钡分光光度法_原始记录报告模板","硫化物_亚甲基蓝分光光度法_测定报告模板","氟化物_氟试剂分光光度法_原始记录报告模板","氟化物_离子选择电极法_测定原始记录报告模板","总磷_钼酸铵分光光度法_原始记录报告模板",
"硝酸盐氮_紫外分光光度法_原始记录报告模板","硝酸盐氮_酚二磺酸分光光度法_测定报告模板",
"化学需氧量_重铬酸盐法_原始记录报告模板","化学需氧量_快速密闭消解分光光度法_测定报告模板",
"高锰酸盐指数_滴定法_原始记录报告模板","溶解氧_碘量法_测定报告模板","溶解氧_电化学探头法_原始记录报告模板",
"色度_铂钴比色法_原始记录报告模板","浊度_目视比浊法_测定报告模板","浊度_便携式浊度计法_原始记录报告模板",
"余氯_二乙基对苯二胺分光光度法_原始记录报告模板","总氯_二乙基对苯二胺滴定法_测定报告模板",
"二氧化硅_硅钼黄分光光度法_原始记录报告模板","游离氯_二乙基对苯二胺分光光度法_原始记录报告模板",
"氯化物_硝酸银滴定法_测定原始记录报告模板","总铁_邻菲啰啉分光光度法_原始记录报告模板",
"总铁_火焰原子吸收分光光度法_测定报告模板","铜_二乙基二硫代氨基甲酸钠分光光度法_原始记录报告模板",
"锌_双硫腙分光光度法_测定报告模板","锰_甲醛肟分光光度法_原始记录报告模板","铅_双硫腙分光光度法_原始记录报告模板",
"镉_双硫腙分光光度法_测定报告模板","砷_二乙基二硫代氨基甲酸银分光光度法_原始记录报告模板","锑_孔雀绿分光光度法_测定报告模板",
"铜锌铅镉_火焰原子吸收分光光度法_原始记录报告模板","铅镉_石墨炉原子吸收分光光度法_测定报告模板",
"汞_冷原子吸收分光光度法_原始记录报告模板","砷硒_微波消解原子荧光法_测定报告模板","钾钠_火焰原子吸收分光光度法_原始记录报告模板",
"钡_电位滴定法_原始记录报告模板","镍_丁二酮肟分光光度法_原始记录报告模板","铍_铬天青分光光度法_测定报告模板",
"钒_钽试剂萃取分光光度法_原始记录报告模板","钴_氯化亚锡分光光度法_测定报告模板","铊_电感耦合等离子体质谱法_原始记录报告模板",
"阴离子表面活性剂_亚甲蓝分光光度法_原始记录报告模板","苯胺类_萘基乙二胺分光光度法_测定报告模板",
"挥发酚_氨基安替比林分光光度法_原始记录报告模板","石油类_红外分光光度法_原始记录报告模板","动植物油类_红外分光光度法_测定报告模板",
"尿素_二乙酰一肟分光光度法_原始记录报告模板","叶绿素_分光光度法_测定报告模板","挥发性有机物_吹扫捕集气相色谱质谱法_原始记录报告模板",
"半挥发性有机物_液液萃取气相色谱质谱法_测定报告模板","苯系物_顶空气气相色谱法_原始记录报告模板","多环芳烃_高效液相色谱法_测定报告模板",
"硝基苯类化合物_液液萃取气相色谱法_原始记录报告模板","有机磷农药_气相色谱法_测定报告模板","有机氯农药_气相色谱质谱法_原始记录报告模板",
"氯苯类_气相色谱法_测定报告模板","土壤酸碱度_电位法_原始记录报告模板","土壤水分_重量法_测定报告模板","土壤有机碳_重铬酸钾氧化分光光度法_原始记录报告模板",
"土壤阳离子交换量_三氯化六氨合钴浸提分光光度法_测定报告模板","土壤总汞_催化热解冷原子吸收分光光度法_原始记录报告模板",
"土壤砷铋锑_微波消解原子荧光法_测定报告模板","土壤六价铬_碱溶液提取火焰原子吸收法_原始记录报告模板","土壤有效磷_碳酸氢钠浸提钼锑抗分光光度法_测定报告模板",
"土壤氰化物_分光光度法_原始记录报告模板","空气二氧化硫_甲醛吸收副玫瑰苯胺分光光度法_原始记录报告模板","空气臭氧_靛蓝二磺酸钠分光光度法_测定报告模板",
"空气一氧化碳_非分散红外吸收法_原始记录报告模板","环境空气颗粒物_重量法_原始记录报告模板","废气二氧化硫_定电位电解法_测定报告模板",
"废气颗粒物_等速采样重量法_原始记录报告模板","废气非甲烷总烃_气相色谱法_测定报告模板","废气沥青烟_重量法_原始记录报告模板","废气氯化氢_硝酸银容量法_测定报告模板","空气降尘_重量法_原始记录报告模板","固废腐蚀性_玻璃电极法_原始记录报告模板","固废有机质_灼烧减量法_测定报告模板","室内空气甲醛_酚试剂分光光度法_原始记录报告模板","室内总挥发性有机物_热解吸气相色谱法_测定报告模板","污泥含水率_重量法_原始记录报告模板","矿化物_离子色谱法_原始记录报告模板",
]
    base_template_name = "亚硝酸盐_萘乙二胺分光光度法_原始记录报告模板"
    standard_template_base = await TemplateDocBase.filter(name=base_template_name).first()
    print(f"找到标准模板基础数据: {standard_template_base}")
    standard_template = await TemplateDoc.filter(base_template_id=standard_template_base.id).first() if standard_template_base else None


    if not standard_template:
        print("未找到标准模板，无法继续")
        return
    old_template_bookmark_list = await TemplateBookmark.filter(template_doc_id=standard_template.id).all()
    base_data = {
        k: v for k, v in standard_template_base.__dict__.items() 
        if not k.startswith('_') and k != 'id'
    }
    for name in template_name_list:
        industry = random.choice(INDUSTRY_LIST)
        async with in_transaction('default'):
            base_data['name'] = name
            base_data['industry_type'] = industry
            new_template_base = await TemplateDocBase.create(**base_data)

            doc_data = {
                k: v for k, v in standard_template.__dict__.items() 
                if not k.startswith('_') and k != 'id' and k != 'base_template_id'
            }
            doc_data['base_template_id'] = new_template_base.id
            doc_data['name'] = name
            doc_data['industry_type'] = industry
            template_doc_instance = await TemplateDoc.create(**doc_data)

            for bookmark in old_template_bookmark_list:
                bookmark_info = {
                    k: v for k, v in bookmark.__dict__.items() 
                    if not k.startswith('_') and k != 'id' and k != 'template_doc_id'
                }
                bookmark_info['template_doc_id'] = template_doc_instance.id
                await TemplateBookmark.create(**bookmark_info)

            print(f"  ✓ {name} → {industry}")

    print(f"\n完成，共创建 {len(template_name_list)} 个模板")


    
    

if __name__ == "__main__":
    asyncio.run(run())
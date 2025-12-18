
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
from app.template_doc.model.template_doc_base import TemplateDocBase
from app.template_doc.model.bookmark_data import BookmarkData
from app.template_doc.model.template_bookmark import TemplateBookmark
from app.template_doc.model.template_extra_info import TemplateExtraInfo

async def run():
    await init_db()  # 初始化数据库连接
    
    i = 0
    template_base_instances = await TemplateDocBase.filter(is_del=1)
    print(f"找到 {len(template_base_instances)} 个已删除的模板基础记录")
    
    for template_base_instance in template_base_instances:
        print(f"处理模板基础记录: {template_base_instance.name} (ID: {template_base_instance.id})")
        
        template_instance = await TemplateDoc.filter(base_template_id=template_base_instance.id).first()
        if template_instance:
            print(f"  找到关联的模板记录: {template_instance.id}")
            
            # 获取所有书签
            bookmarks = await TemplateBookmark.filter(template_doc_id=template_instance.id)
            print(f"  找到 {len(bookmarks)} 个书签记录")
            
            if bookmarks:
                # 先删除书签数据
                bookmark_ids = [bookmark.id for bookmark in bookmarks]
                bookmark_data_count = await BookmarkData.filter(bookmark_id__in=bookmark_ids).count()
                print(f"  删除 {bookmark_data_count} 个书签数据记录")
                await BookmarkData.filter(bookmark_id__in=bookmark_ids).delete()
                
                # 删除书签
                for bookmark in bookmarks:
                    await bookmark.delete()
            
            # 删除自定义书签
            custom_bookmark_count = await TemplateExtraInfo.filter(template_doc_id=template_instance.id).count()
            print(f"  删除 {custom_bookmark_count} 个自定义书签记录")
            await TemplateExtraInfo.filter(template_doc_id=template_instance.id).delete()
            
            # 删除模板额外信息
            extra_info_count = await TemplateExtraInfo.filter(template_doc_id=template_instance.id).count()
            print(f"  删除 {extra_info_count} 个模板额外信息记录")
            await TemplateExtraInfo.filter(template_doc_id=template_instance.id).delete()
            
            # 删除模板记录
            await template_instance.delete()
            print(f"  删除模板记录: {template_instance.id}")
        else:
            print(f"  未找到关联的模板记录")
        
        # 删除模板基础记录
        await template_base_instance.delete()
        print(f"  删除模板基础记录: {template_base_instance.id}")
        
        i += 1
    
    print(f"总共处理了 {i} 个模板")

if __name__ == "__main__":
    asyncio.run(run())
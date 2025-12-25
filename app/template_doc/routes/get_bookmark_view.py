
import importlib
from typing import List, Optional, Dict

from fastapi import APIRouter
from pydantic import BaseModel, Field

from exceptions.error import ErrorCode
from ..model.template_doc import TemplateDoc
from utils.log_decorator import log_response
from utils.template_utils import get_title_mapping
from exceptions.command_exception import APIException
from constants.template_constant import TemplateBookMarkType

router = APIRouter()

class BookmarkItem(BaseModel):
    template_doc_id: int = Field(..., description="所属模板文档ID")
    name: str = Field(..., description="书签名称")
    desc_t: Optional[str] = Field(None, description="time_mapping 的key")
    sort_order: int = Field(None, description="显示顺序（越小越靠前）")
    font: Optional[str] = Field(None, description="字体")
    font_size: Optional[int] = Field(None, description="字号")

class BookmarkDataSchema(BaseModel):
    bookmarks: Dict[int, List[BookmarkItem]] = Field({}, description=f'{TemplateBookMarkType.text.value}:{TemplateBookMarkType.text.name},\
                                  {TemplateBookMarkType.sheet.value}:{TemplateBookMarkType.sheet.name},\
                                  {TemplateBookMarkType.img.value}:{TemplateBookMarkType.img.name}')

class OutSchema(BaseModel):
    code: int = Field(0, description='状态码')
    message: str = Field('获取成功', description='返回信息')
    data: BookmarkDataSchema

@router.get('/get_bookmark', response_model=OutSchema)
@log_response
async def get_bookmark(template_id: int, type: Optional[int] = None):
    template_instance = await TemplateDoc.get_or_none(id=template_id, is_del=0)
    if template_instance is None:
        raise APIException(ErrorCode.TEMPLATE_NOT_FOUND)
    result = []
    # 加载标题映射
    title_mapping = get_title_mapping(template_instance.name)
    for t, info_dict in title_mapping.items():
        result.append({
            'name': info_dict.get('name', ''),
            'desc_t': t,
            'template_doc_id': template_id,
            'font': info_dict.get('font'),
            'font_size': info_dict.get('font_size')
        })


    # 对每个类型的书签树进行处理 
    # processed_result = {item_type: process_tree(bookmarks_tree) for item_type, bookmarks_tree in result.items()} 
    return {'code': 200, 'message': '获取成功', 'data': {'bookmarks': { 0 : result}}}




def build_tree(bookmarks):
    id_list = []
    id_node_map = {item['id']: {**item, 'children': []} for item in bookmarks}

    tree = []
    for item in bookmarks:
        node = id_node_map[item['id']]
        parent_id = item['parent_id']
        if parent_id is None:
            tree.append(node)
        else:
            parent = id_node_map.get(parent_id)
            if parent:
                parent['children'].append(node)
            else:
                tree.append(node)

    # # 扁平化树结构
    # id_list = []
    # def flatten_tree(nodes):
    #     for node in nodes:
    #         id_list.append({
    #             'bm_id': node.get('id'),
    #             'font': node.get('font'),
    #             'font_size': node.get('font_size')
    #         })
    #         if node.get('children'):
    #             flatten_tree(node['children'])

    # flatten_tree(tree)
    # print('id列表:', id_list)
    return tree


# 递归处理树结构，二级标签分割保留
def process_tree(tree):
    result = []
    for node in tree:
        # 跳过 xx_值 这类节点
        if node['name'].endswith('_值'):
            continue  

        name_parts = node['name'].split('_')
        if len(name_parts) == 2:
            node['name'] = name_parts[1]

        # 递归处理子节点
        if node.get('children'):
            node['children'] = process_tree(node['children'])

        result.append(node)
    return result
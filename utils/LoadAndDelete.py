#获取word中存在的书签名称（去重）
from docx import Document
from docx.oxml.ns import qn
from constants.template_constant import TemplateBookMarkType

#获取word中所有的书签名称
def get_word_bookmarks(file_stream):
    doc = Document(file_stream)

    ns_uri = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
    doc_element = doc.part._element

    # 按文档顺序查找所有bookmarkStart和bookmarkEnd
    all_bookmarks = doc_element.xpath('.//*[local-name()="bookmarkStart" or local-name()="bookmarkEnd"]')
    bookmarks = []
    stack = []

    for elem in all_bookmarks:
        tag_name = elem.tag.split('}')[-1]  # 获取local-name
        bm_id = elem.get(f'{{{ns_uri}}}id')

        if tag_name == 'bookmarkStart':
            name = elem.get(f'{{{ns_uri}}}name')
            name_part = name.split('_')
            font, font_size = get_font_and_size(elem)
            bookmark_type = TemplateBookMarkType.text.value
            if(len(name_part) > 1):
                node = {
                    'id': bm_id,
                    'name': name,
                    'children': [],
                }
                # if name_part[0] == TemplateBookMarkType.text.name:
                #     bookmark_type = TemplateBookMarkType.text.value # 文字
                if name_part[0] == TemplateBookMarkType.sheet.name:
                    bookmark_type = TemplateBookMarkType.sheet.value # 表格
                if name_part[0] == TemplateBookMarkType.img.name:
                    bookmark_type = TemplateBookMarkType.img.value # 图片
            else:
                node = {
                    'id': bm_id,
                    'name': name,
                    'children': [],
                }
            node['type'] = bookmark_type
            node['font'] = font
            node['font_size'] = font_size
            node['img_size'] = get_image_size(elem) if bookmark_type == TemplateBookMarkType.img.value else None
            if stack:
                stack[-1]['children'].append(node)
            else:
                bookmarks.append(node)
            stack.append(node)

        elif tag_name == 'bookmarkEnd':
            # 找到结束时，直接出栈（注意：真实Word文件的id一般是严格配对的）
            if stack:
                stack.pop()
            else:
                # 理论上这里可以做异常处理，表示书签不匹配
                pass
    return bookmarks


# 使用示例  获取该文档中所有的书签
# docx_file = r'D:\Python\Template1.docx'
# bookmarks = get_word_bookmarks(docx_file)
# print("文档中的书签列表:", bookmarks)


#删除指定书签
def delete_bookmark_content(doc_path, bookmark_names, output_path):
    """
    删除指定书签及其所有内容（支持跨段落/表格）
    :param doc_path: 输入文档路径
    :param bookmark_names: 要删除的书签名列表
    :param output_path: 输出文档路径
    """
    doc = Document(doc_path)
    root = doc.part._element
    ns_uri = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'

    # 遍历所有书签起始标签
    bookmark_starts = [elem for elem in root.iter() if elem.tag.endswith('bookmarkStart')]

    for bm_start in bookmark_starts:
        # 获取书签名称和ID
        name = bm_start.get(f'{{{ns_uri}}}name')
        if name not in bookmark_names:
            continue

        bm_id = bm_start.get(f'{{{ns_uri}}}id')
        parent = bm_start.getparent()

        # 查找匹配的结束标签（全局搜索）
        bm_end = None
        for elem in root.iter():
            if elem.tag.endswith('bookmarkEnd') and elem.get(f'{{{ns_uri}}}id') == bm_id:
                bm_end = elem
                break

        if not bm_end:
            continue

        # 标记需要删除的节点（跨父节点处理）
        nodes_to_delete = []
        current_node = bm_start
        while current_node != bm_end:
            nodes_to_delete.append(current_node)
            # 深度优先遍历子节点
            if len(current_node) > 0:
                current_node = current_node[0]
            else:
                next_node = current_node.getnext()
                while not next_node and current_node != parent:
                    current_node = current_node.getparent()
                    next_node = current_node.getnext()
                current_node = next_node

        nodes_to_delete.append(bm_end)

        # 逆序删除避免结构破坏
        for node in reversed(nodes_to_delete):
            p = node.getparent()
            if p is not None:
                p.remove(node)

    # 清理空段落
    for para in reversed(doc.paragraphs):
        if not para.text.strip():
            p = para._element
            p.getparent().remove(p)

    doc.save(output_path)

def get_font_and_size(elem):
    # 默认字体 & 字号
    default_font = "宋体"
    default_size = 12

    run = elem.getparent()
    while run is not None and run.tag != '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}r':
        run = run.getparent()

    if run is None:
        return default_font, default_size

    ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}

    font_elem = run.find('.//w:rFonts', namespaces=ns)
    font = font_elem.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}ascii') if font_elem is not None else default_font

    size_elem = run.find('.//w:sz', namespaces=ns)
    font_size = int(size_elem.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val')) / 2 if size_elem is not None else default_size

    return font, font_size


def get_image_size(elem):
    # 默认图像宽度（cm）
    default_size = 14.0

    try:
        drawing = elem.getparent().xpath('.//wp:extent', namespaces={
            'wp': 'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing'
        })
        if drawing:
            cx = int(drawing[0].get('cx'))  # EMUs单位
            cm_size = round(cx / 360000.0, 2)
            return cm_size
    except Exception:
        pass

    return default_size

# 使用示例
# input_file = r'D:\Python\Template1.docx'
# output_file = r'D:\Python\Template1-new.docx'
# bookmarks_to_remove = ["操作步骤","计算公式"]

# delete_bookmark_content(input_file, bookmarks_to_remove, output_file)
# print(f"已删除书签 {bookmarks_to_remove}，新文档保存至 {output_file}")
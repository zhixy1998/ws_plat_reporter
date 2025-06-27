#获取word中存在的书签名称（去重）
from io import BytesIO
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
            if name.startswith('_'):
                continue
            font, font_size = get_font_and_size(elem)
            if TemplateBookMarkType.sheet.decs in name:
                bookmark_type = TemplateBookMarkType.sheet.value
            elif TemplateBookMarkType.img.decs in name:
                bookmark_type = TemplateBookMarkType.img.value
            else:
                bookmark_type = TemplateBookMarkType.text.value
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
def delete_bookmark_content(doc, bookmark_name, output_path):
    # 1. 找到目标 bookmarkStart 和它的 id
    bookmarks = doc.part._element.xpath('.//*[local-name()="bookmarkStart"]')
    start_bm = None
    target_id = None

    for bm in bookmarks:
        name = bm.get(qn("w:name"))
        if name == bookmark_name:
            start_bm = bm
            target_id = bm.get(qn("w:id"))
            break

    if start_bm is None:
        print(f"❌ 没有找到书签 {bookmark_name}")
        return

    # 2. 找到对应 bookmarkEnd（同一个 id）
    bookmark_ends = doc.part._element.xpath('.//*[local-name()="bookmarkEnd"]')
    end_bm = None
    for end in bookmark_ends:
        if end.get(qn("w:id")) == target_id:
            end_bm = end
            break

    if end_bm is None:
        print(f"❌ 没找到书签 {bookmark_name} 的结束标签")
        return
    # 3. 删除 bookmarkStart 到 bookmarkEnd 之间的所有元素，包括两端
    element = start_bm
    while element is not None:
        next_element = element.getnext()
        element.getparent().remove(element)
        if element == end_bm:
            break
        element = next_element

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
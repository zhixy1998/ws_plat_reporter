from docx.oxml.ns import qn
from io import BytesIO
import base64
from docx.shared import Cm
from constants.template_constant import TemplateBookMarkType

#向指定标签插入内容
def fill_word_bookmark(doc, bookmark_name, value, value_type=TemplateBookMarkType.text.value):
    found = False

    for paragraph in doc.paragraphs:
        for element in paragraph._p:
            if element.tag.endswith('bookmarkStart'):
                name = element.get(qn('w:name'))
                if name == bookmark_name:
                    found = True
                    remove_following_runs(paragraph, element)
                    insert_value(paragraph, element, value, value_type)

    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for paragraph in cell.paragraphs:
                    for element in paragraph._p:
                        if element.tag.endswith('bookmarkStart'):
                            name = element.get(qn('w:name'))
                            if name == bookmark_name:
                                found = True
                                remove_following_runs(paragraph, element)
                                insert_value(paragraph, element, value, value_type)

    for section in doc.sections:
        for paragraph in section.header.paragraphs:
            for element in paragraph._p:
                if element.tag.endswith('bookmarkStart'):
                    name = element.get(qn('w:name'))
                    if name == bookmark_name:
                        found = True
                        remove_following_runs(paragraph, element)
                        insert_value(paragraph, element, value, value_type)

    for section in doc.sections:
        for paragraph in section.footer.paragraphs:
            for element in paragraph._p:
                if element.tag.endswith('bookmarkStart'):
                    name = element.get(qn('w:name'))
                    if name == bookmark_name:
                        found = True
                        remove_following_runs(paragraph, element)
                        insert_value(paragraph, element, value, value_type)

    if not found:
        found = try_global_bookmark_fill(doc, bookmark_name, value, value_type)

    if not found:
        print(f"⚠ 没有找到书签: {bookmark_name}")

    output_stream = BytesIO()
    doc.save(output_stream)
    output_stream.seek(0)
    return output_stream

def insert_value(paragraph, bookmark_element, value, value_type, doc=None):
    insert_index = paragraph._element.index(bookmark_element) + 1

    if value_type == TemplateBookMarkType.text.value:
        new_run = paragraph.insert_paragraph_before().add_run(str(value))
        paragraph._element.insert(insert_index, new_run._element)

    elif value_type == TemplateBookMarkType.img.value:
        # 先判断是否带有 data:image/png;base64, 前缀
        if value.startswith("data:image"):
            header, b64data = value.split(",", 1)
        else:
            b64data = value

        image_bytes = base64.b64decode(b64data)
        image_stream = BytesIO(image_bytes)
        run = paragraph.add_run()
        run.add_picture(image_stream, width=Cm(14))  # 自行控制宽度

    elif value_type == TemplateBookMarkType.sheet.value:
        if not doc:
            print("错误：插入表格时缺少'doc'对象。")
            return

        p_element = paragraph._element # 书签所在的段落元素 <w:p>

        # 1. 向上查找，判断书签是否在表格内
        parent_tbl_elem = None
        parent = p_element.getparent()
        while parent is not None:
            if parent.tag == qn('w:tbl'):
                parent_tbl_elem = parent
                break
            parent = parent.getparent()

        # 2. 创建新表格 (你的逻辑，很好)
        # 注意：add_table 会将表格添加到文档末尾，我们之后需要移动它
        table_data = value
        cols = len(table_data[0])
        # 确保列数大于0
        if cols == 0:
            print(f"警告: 为书签 {bookmark_element.get(qn('w:name'))} 提供的表格数据没有列。")
            return
            
        tbl = doc.add_table(rows=0, cols=cols)
        tbl.style = 'Table Grid'
        for row_data in table_data:
            # 确保每行数据长度与列数一致
            if len(row_data) != cols:
                 print(f"警告: 行数据 {row_data} 的长度与表格列数 {cols} 不匹配。")
                 continue # 或者进行其他错误处理
            row_cells = tbl.add_row().cells
            for idx, cell_data in enumerate(row_data):
                row_cells[idx].text = str(cell_data)
        
        # 3. 根据情况，替换旧表格或占位段落
        if parent_tbl_elem is not None:
            # a. 如果书签在表格里，用新表格替换整个旧表格
            parent_tbl_elem.addnext(tbl._element)
            parent_tbl_elem.getparent().remove(parent_tbl_elem)
        else:
            # b. 如果书签在普通段落里，用新表格替换该段落
            p_element.addnext(tbl._element)
            p_element.getparent().remove(p_element)

def remove_following_runs(paragraph, bookmark_element):
    start_found = False
    elements_to_remove = []

    for element in paragraph._p:
        if element == bookmark_element:
            start_found = True
            continue

        if not start_found:
            continue

        if element.tag.endswith('bookmarkEnd'):
            break

        if element.tag.endswith('r'):
            elements_to_remove.append(element)

    for el in elements_to_remove:
        paragraph._p.remove(el) 


# 全局查找书签并填充
def try_global_bookmark_fill(doc, bookmark_name, value, value_type):
    from docx.oxml import parse_xml
    doc_element = doc.part._element
    bookmarks = doc_element.xpath('.//*[local-name()="bookmarkStart"]')

    for bm in bookmarks:
        name = bm.get(qn('w:name'))
        if name == bookmark_name:
            parent = bm.getparent()
            # 这里不直接插入，而是调用 insert_value ，
            # 传入一个伪造的段落对象来包装 bm 元素方便调用。
            # 或者找bm的上级段落paragraph并传入

            # 找到书签所在的段落对象
            from docx.text.paragraph import Paragraph
            p_elem = bm.getparent()
            while p_elem is not None and p_elem.tag != qn('w:p'):
                p_elem = p_elem.getparent()
            if p_elem is None:
                # 书签不在段落里，无法插入文本或图片，直接返回True
                return True
            paragraph = Paragraph(p_elem, doc)
            insert_value(paragraph, bm, value, value_type, doc)
            return True
    return False
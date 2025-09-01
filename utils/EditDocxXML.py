import base64
from io import BytesIO
from typing import List, Optional

from docx import Document
from docx.oxml.ns import qn
from docx.text.run import Run
from docx.shared import Pt, Cm, Twips
from docx.oxml import OxmlElement
from docx.text.paragraph import Paragraph
from constants.template_constant import TemplateBookMarkType

#向指定标签插入内容
def fill_word_bookmark(doc, bookmark_name, value, value_type=TemplateBookMarkType.text.value, font=None, font_size=None, specific_column_widths: Optional[List[int]] = None ):
    if isinstance(doc, BytesIO):
        doc.seek(0)
        doc = Document(doc)

    found = False
    replaced_count = 0
    # 遍历文档主体段落
    for paragraph in doc.paragraphs:
        for element in paragraph._p:
            if element.tag.endswith('bookmarkStart'):
                name = element.get(qn('w:name'))
                if name == bookmark_name:
                    found = True
                    if value:
                        remove_following_runs(paragraph, element)
                        insert_value(paragraph, element, value, value_type, doc=doc, specific_column_widths=specific_column_widths)
                    else:
                        set_bookmark_run_style(doc, paragraph, bookmark_name, font=font, font_size=font_size)
    # 遍历表格中的段落
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for paragraph in cell.paragraphs:
                    for element in paragraph._p:
                        if element.tag.endswith('bookmarkStart'):
                            name = element.get(qn('w:name'))
                            if name == bookmark_name and replaced_count == 0:
                                replaced_count += 1
                                found = True
                                if value:
                                    remove_following_runs(paragraph, element)
                                    insert_value(paragraph, element, value, value_type, doc=doc, specific_column_widths=specific_column_widths)
                                else:
                                    set_bookmark_run_style(doc, paragraph, bookmark_name, font=font, font_size=font_size)
    # 遍历页眉中的段落
    for section in doc.sections:
        for paragraph in section.header.paragraphs:
            for element in paragraph._p:
                if element.tag.endswith('bookmarkStart'):
                    name = element.get(qn('w:name'))
                    if name == bookmark_name:
                        found = True
                        if value:
                            remove_following_runs(paragraph, element)
                            insert_value(paragraph, element, value, value_type, doc=doc, specific_column_widths=specific_column_widths)
                        else:
                            set_bookmark_run_style(doc, paragraph, bookmark_name, font=font, font_size=font_size)
    # 遍历页脚中的段落
    for section in doc.sections:
        for paragraph in section.footer.paragraphs:
            for element in paragraph._p:
                if element.tag.endswith('bookmarkStart'):
                    name = element.get(qn('w:name'))
                    if name == bookmark_name:
                        found = True
                        if value:
                            remove_following_runs(paragraph, element)
                            insert_value(paragraph, element, value, value_type, doc=doc, specific_column_widths=specific_column_widths)
                        else:
                            set_bookmark_run_style(doc, paragraph, bookmark_name, font=font, font_size=font_size)

    if not found:
        found = try_global_bookmark_fill(doc, bookmark_name, value, value_type, font=font, font_size=font_size, specific_column_widths=specific_column_widths)

    if not found:
        pass  # 没有找到书签

    output_stream = BytesIO()
    doc.save(output_stream)
    output_stream.seek(0)
    return output_stream

def insert_value(paragraph, bookmark_element, value, value_type, doc=None, specific_column_widths: Optional[List[int]] = None):
    insert_index = paragraph._element.index(bookmark_element) + 1

    if value_type == TemplateBookMarkType.text.value:
        new_run = paragraph.insert_paragraph_before().add_run(str(value))
        paragraph._element.insert(insert_index, new_run._element)

    elif value_type == TemplateBookMarkType.img.value:
        if not value:
            return
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
        if not value:
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
        
        # 查找旧的table的格式
        tblPr = parent_tbl_elem.tblPr
        if tblPr is not None:
            tblStyle = tblPr.tblStyle
            if tblStyle is not None:
                old_style_id = tblStyle.val  # 这是样式名字符串
            else:
                old_style_id = None
        else:
            old_style_id = None

        old_style_name = get_style_name_from_id(doc, old_style_id)

        # 2. 创建新表格 (你的逻辑，很好)
        # 注意：add_table 会将表格添加到文档末尾，我们之后需要移动它
        table_data = value
        cols = len(table_data[0])
        # 确保列数大于0
        if cols == 0:
            print(f"警告: 为书签 {bookmark_element.get(qn('w:name'))} 提供的表格数据没有列。")
            return
        tbl = doc.add_table(rows=0, cols=cols)
        # tbl.style = old_style_name  # 临时注释掉样式设置
        # print(f"🎨 跳过表格样式设置，使用默认样式")
        set_table_border(tbl)
        
        # 先添加所有行数据
        for row_data in table_data:
            # 确保每行数据长度与列数一致
            if len(row_data) != cols:
                 print(f"警告: 行数据 {row_data} 的长度与表格列数 {cols} 不匹配。")
                 continue # 或者进行其他错误处理
            row_cells = tbl.add_row().cells
            for idx, cell_data in enumerate(row_data):
                row_cells[idx].text = str(cell_data)
        
        # 最后设置表格宽度和列宽
        set_table_width(tbl)  # 设置表格整体宽度和对齐
        
        # ！！！在这里使用 specific_column_widths 设置列宽！！！
        if specific_column_widths and len(specific_column_widths) == cols:
            for idx, col_width_emu in enumerate(specific_column_widths):
                # 将 EMU 转换为 dxa (1 dxa = 15 EMU)
                if col_width_emu is not None:
                    tbl.columns[idx].width = Twips(col_width_emu // 635) # 使用 // 进行整数除法
                # else: 如果为 None，则保持 python-docx 默认行为或您可以提供一个默认 dxa 值
        else:
            # 如果没有提供精确列宽，让表格自动调整列宽
            # 不手动设置列宽，让 set_table_width 中的整体宽度生效
            pass

        # 3. 根据情况，替换旧表格或占位段落
        if parent_tbl_elem is not None:
            # a. 如果书签在表格里，用新表格替换整个旧表格
            parent_tbl_elem.addnext(tbl._element)
            parent_tbl_elem.getparent().remove(parent_tbl_elem)
        else:
            # b. 如果书签在普通段落里，在段落后插入表格，但保留原段落
            p_element.addnext(tbl._element)
            # 不删除原段落，只清理书签相关的内容
            remove_following_runs(paragraph, bookmark_element)

def remove_following_runs(paragraph, bookmark_element):
    start_found = False
    elements_to_remove = []
    bookmark_id = bookmark_element.get(qn('w:id'))

    for element in paragraph._p:
        if element == bookmark_element:
            start_found = True
            continue

        if not start_found:
            continue

        # 只在找到匹配ID的bookmarkEnd时停止
        if element.tag.endswith('bookmarkEnd') and element.get(qn('w:id')) == bookmark_id:
            break

        if element.tag.endswith('r'):
            elements_to_remove.append(element)

    for el in elements_to_remove:
        paragraph._p.remove(el)

def set_bookmark_run_style(doc, paragraph, bookmark_name, font=None, font_size=None):
    # 1. 找到所有 bookmarkStart 和 bookmarkEnd
    # 1. 找到目标 bookmarkStart 和对应 id
    bookmark_starts = doc.part._element.xpath('.//*[local-name()="bookmarkStart"]')
    start_bm = None
    bm_id = None

    for bm in bookmark_starts:
        if bm.get(qn("w:name")) == bookmark_name:
            start_bm = bm
            bm_id = bm.get(qn("w:id"))
            break

    if start_bm is None:
        print(f"❌ 没找到书签 {bookmark_name}")
        return

    # 2. 找到对应的 bookmarkEnd
    bookmark_ends = doc.part._element.xpath('.//*[local-name()="bookmarkEnd"]')
    end_bm = None
    for bm in bookmark_ends:
        if bm.get(qn("w:id")) == bm_id:
            end_bm = bm
            break

    if end_bm is None:
        print(f"❌ 没找到书签 {bookmark_name} 的结束标签")
        return

    # 3. 遍历 bookmarkStart 到 bookmarkEnd 之间的兄弟节点
    element = start_bm.getnext()
    while element is not None and element != end_bm:
        if element.tag.endswith("r"):  # 是 run
            # 检查该 run 的直接子元素是否为 <w:t>
            for child in element.getchildren():
                if child.tag.endswith("t"):
                    child.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")

                    # 找到该 run 的所属段落
                    p_elem = element
                    while p_elem is not None and p_elem.tag != qn("w:p"):
                        p_elem = p_elem.getparent()
                    if p_elem is None:
                        continue

                    para = Paragraph(p_elem, doc)
                    run = Run(element, para)

                    if font:
                        run.font.name = font
                        r = run._element.rPr
                        rFonts = r.get_or_add_rFonts()
                        rFonts.set(qn('w:eastAsia'), font)
                    if font_size:
                        run.font.size = Pt(font_size)
        element = element.getnext()

# 全局查找书签并填充
def try_global_bookmark_fill(doc, bookmark_name, value, value_type, font, font_size, specific_column_widths=None):
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
            insert_value(paragraph, bm, value, value_type, doc=doc, specific_column_widths=specific_column_widths)
            return True
    return False


def get_style_name_from_id(doc, style_id):
    for style in doc.styles:
        if style.style_id == style_id:
            return style.name
    return None

def set_table_border(table):
    tbl = table._element
    tblPr = tbl.tblPr

    tblBorders = OxmlElement('w:tblBorders')

    for border_name in ('top', 'left', 'bottom', 'right', 'insideH', 'insideV'):
        border = OxmlElement(f'w:{border_name}')
        border.set(qn('w:val'), 'single')   # 实线
        border.set(qn('w:sz'), '4')         # 粗细
        border.set(qn('w:space'), '0')
        border.set(qn('w:color'), '000000') # 黑色
        tblBorders.append(border)

    tblPr.append(tblBorders)

def set_table_width(tbl, width_cm=8):
    tblPr = tbl._element.tblPr

    # 先清除所有现有的宽度设置，避免冲突
    for elem in tblPr.findall(qn('w:tblW')):
        tblPr.remove(elem)

    # 设置表格布局算法为固定布局
    tblLayout = OxmlElement('w:tblLayout')
    tblLayout.set(qn('w:type'), 'fixed')  # 固定布局
    tblPr.insert(0, tblLayout)
    
    # 创建新的宽度元素
    tblW = OxmlElement('w:tblW')
    
    # 使用百分比宽度 (30% 的页面宽度)
    width_pct = 1500  # 30% = 1500 (30 * 50)
    tblW.set(qn('w:w'), str(width_pct))
    tblW.set(qn('w:type'), 'pct')  # 使用百分比
    tblPr.insert(1, tblW)
    
    # 添加表格对齐方式设置 - 居中对齐
    jc = OxmlElement('w:jc')
    jc.set(qn('w:val'), 'center')  # 居中对齐
    tblPr.insert(2, jc)
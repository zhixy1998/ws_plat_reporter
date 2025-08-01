#获取word中存在的书签名称（去重）
import re, os, json
from typing import Dict, List

from docx import Document
from docx.oxml.ns import qn
from docx.table import Table
from docx.oxml.table import CT_Tbl
from constants.template_constant import TemplateBookMarkType, StructureType
from docx.shared import Cm
from docx.oxml import OxmlElement
from io import BytesIO
# from exceptions.error import ErrorCode
# from exceptions.command_exception import APIException

#获取word中所有的书签名称
# def get_word_bookmarks(file_stream):
#     doc = Document(file_stream)

#     ns_uri = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
#     doc_element = doc.part._element

#     # 按文档顺序查找所有bookmarkStart和bookmarkEnd
#     all_bookmarks = doc_element.xpath('.//*[local-name()="bookmarkStart" or local-name()="bookmarkEnd"]')
#     bookmarks = []
#     stack = []

#     for elem in all_bookmarks:
#         tag_name = elem.tag.split('}')[-1]  # 获取local-name
#         bm_id = elem.get(f'{{{ns_uri}}}id')

#         if tag_name == 'bookmarkStart':
#             name = elem.get(f'{{{ns_uri}}}name')
#             if name.startswith('_'):
#                 continue
#             font, font_size = get_font_and_size(elem)
#             node = {
#                 'id': bm_id,
#                 'name': name,
#                 'children': [],
#             }
#             if TemplateBookMarkType.sheet.decs in name:
#                 bookmark_type = TemplateBookMarkType.sheet.value
#                 tbl = get_table_by_element(elem, doc)
#                 if tbl:
#                     node['table_structure'] = parse_table_to_json(tbl, name)
#                 else:
#                     node['table_structure'] = None
#             elif TemplateBookMarkType.img.decs in name:
#                 bookmark_type = TemplateBookMarkType.img.value
#             else:
#                 bookmark_type = TemplateBookMarkType.text.value
#             node['type'] = bookmark_type
#             node['font'] = font
#             node['font_size'] = font_size
#             node['img_size'] = get_image_size(elem) if bookmark_type == TemplateBookMarkType.img.value else None

#             if stack:
#                 stack[-1]['children'].append(node)
#             else:
#                 bookmarks.append(node)
#             stack.append(node)

#         elif tag_name == 'bookmarkEnd':
#             # 找到结束时，直接出栈（注意：真实Word文件的id一般是严格配对的）
#             if stack:
#                 stack.pop()
#             else:
#                 # 理论上这里可以做异常处理，表示书签不匹配
#                 pass
#     return bookmarks

class AnalysisBookMark:
    """
    分析Word文档中的书签并构建多层嵌套树结构
    支持任意深度的嵌套关系，通过 '-' 分隔符识别层级
    
    例如：
    - "基础信息" (根节点)
    - "基础信息-样品信息" (一级子节点)
    - "基础信息-样品信息-样品名称" (二级子节点)
    - "基础信息-样品信息-样品编号" (二级子节点)
    - "基础信息-测试信息-测试日期" (另一个二级子节点)
    """
    
    def __init__(self, file_stream):
        self.file_stream = file_stream
        self.bookmarks = []  # 最终的树结构
        self.all_nodes = {}  # 所有节点的映射，用于快速查找

    def get_word_bookmarks(self):
        """解析Word文档中的所有书签并构建树结构"""
        doc = Document(self.file_stream)
        ns_uri = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
        doc_element = doc.part._element

        all_bookmarks = doc_element.xpath('.//*[local-name()="bookmarkStart"]')
        raw_bookmarks = []

        # 第一步：收集所有书签的基本信息
        for elem in all_bookmarks:
            bookmark_id = elem.get(f'{{{ns_uri}}}id')
            if not bookmark_id or bookmark_id.startswith('_'):
                continue
            
            name = elem.get(f'{{{ns_uri}}}name')
            if not name or name.startswith('_'):
                continue
            
            font, font_size = get_font_and_size(elem)
        
            # 确定书签类型
            if TemplateBookMarkType.sheet.decs in name:
                bookmark_type = TemplateBookMarkType.sheet.value
                tbl = get_table_by_element(elem, doc)
                table_structure = parse_table_to_json(tbl, name) if tbl else None
                img_size = None
            elif TemplateBookMarkType.img.decs in name:
                bookmark_type = TemplateBookMarkType.img.value
                table_structure = None
                img_size = get_image_size(elem)
            else:
                bookmark_type = TemplateBookMarkType.text.value
                table_structure = None
                img_size = None
            
            node = {
                'id': bookmark_id,
                'name': name,
                'children': [],
                'type': bookmark_type,
                'font': font,
                'font_size': font_size,
            }
        
            if table_structure:
                node['table_structure'] = table_structure
            if img_size:
                node['img_size'] = img_size
            
            raw_bookmarks.append(node)

        # 第二步：构建多层嵌套树结构
        self._build_tree_structure(raw_bookmarks)
        
        return self.bookmarks

    def _build_tree_structure(self, raw_bookmarks):
        """构建多层嵌套的树结构"""
        # 重置
        self.bookmarks = []
        self.all_nodes = {}
        
        # 按名称长度排序，确保父节点先于子节点处理
        sorted_bookmarks = sorted(raw_bookmarks, key=lambda x: len(x['name'].split('_')))
        
        for bookmark in sorted_bookmarks:
            self._add_bookmark_to_tree(bookmark)
    
    def _add_bookmark_to_tree(self, bookmark):
        """将书签添加到树结构中"""
        name = bookmark['name']
        parts = name.split('_')
        
        # 将节点添加到映射中
        self.all_nodes[name] = bookmark
        
        if len(parts) == 1:
            # 根节点
            self.bookmarks.append(bookmark)
        else:
            # 子节点，需要找到父节点
            parent_name = '_'.join(parts[:-1])
            parent_node = self._find_or_create_parent(parent_name)
            parent_node['children'].append(bookmark)
    
    def _find_or_create_parent(self, parent_name):
        """查找或创建父节点"""
        if parent_name in self.all_nodes:
            return self.all_nodes[parent_name]
        
        # 父节点不存在，需要创建
        parts = parent_name.split('_')
        
        # 创建虚拟父节点
        parent_node = {
            'id': f"virtual_{parent_name}",
            'name': parent_name,
            'children': [],
            'type': TemplateBookMarkType.text.value,
            'font': None,
            'font_size': None,
        }
        
        # 递归处理父节点的父节点
        if len(parts) == 1:
            # 这是根节点
            self.bookmarks.append(parent_node)
        else:
            # 这也有父节点
            grandparent_name = '_'.join(parts[:-1])
            grandparent_node = self._find_or_create_parent(grandparent_name)
            grandparent_node['children'].append(parent_node)
        
        # 添加到映射中
        self.all_nodes[parent_name] = parent_node
        return parent_node
    
    def print_tree(self, nodes=None, indent=0):
        """打印树结构，用于调试"""
        if nodes is None:
            nodes = self.bookmarks
        
        for node in nodes:
            print("  " * indent + f"_ {node['name']} (type: {node['type']})")
            if node['children']:
                self.print_tree(node['children'], indent + 1)


#删除指定书签
def delete_bookmark_content(doc, bookmark_name, output_path=None):
    """
    删除指定书签及其内容
    返回修改后的文档
    """
    print(f"开始删除书签: {bookmark_name}")

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
        return doc

    # 2. 找到对应 bookmarkEnd（同一个 id）
    bookmark_ends = doc.part._element.xpath('.//*[local-name()="bookmarkEnd"]')
    end_bm = None
    for end in bookmark_ends:
        if end.get(qn("w:id")) == target_id:
            end_bm = end
            break

    if end_bm is None:
        print(f"❌ 没找到书签 {bookmark_name} 的结束标签")
        return doc

    print(f"找到书签 {bookmark_name}，开始删除内容")

    # 3. 使用更精确的方法删除书签之间的内容
    elements_to_remove = []

    # 获取文档中所有元素的列表（按文档顺序）
    all_elements = doc.part._element.xpath('.//*')

    # 找到开始和结束书签在文档中的位置
    start_index = None
    end_index = None

    for i, elem in enumerate(all_elements):
        if elem == start_bm:
            start_index = i
        elif elem == end_bm:
            end_index = i
            break

    if start_index is None or end_index is None:
        print(f"❌ 无法确定书签 {bookmark_name} 的位置")
        return doc

    # 收集需要删除的元素（包括书签标记本身）
    for i in range(start_index, end_index + 1):
        elements_to_remove.append(all_elements[i])

    # 按照从后往前的顺序删除，避免索引变化问题
    for elem in reversed(elements_to_remove):
        try:
            parent = elem.getparent()
            if parent is not None:
                parent.remove(elem)
        except Exception as e:
            print(f"删除元素时出错: {e}")
            continue

    print(f"✅ 成功删除书签 {bookmark_name} 及其内容")
    return doc

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


def get_table_by_element(elem, doc: Document) -> Table:
    parent = elem
    while parent is not None:
        if parent.tag.endswith('tbl'):
            return Table(parent, doc)
        parent = parent.getparent()
    return None


def parse_table_to_json(tbl: Table, name: str):
    table_info = parse_table_keep_headers(tbl)

    try:
        table_meta = load_table_structure_by_name(name)
    except FileNotFoundError:
        table_meta = {}
    
    # 你可以进一步提取“表头”信息，比如前两行是嵌套表头
    result = {
        'table_name': name,
        "row_count": len(tbl.rows),
        "col_count": len(tbl.columns),
    }
    result.update(table_info)
    """
{
  "headers": [
    ["序号", "样品编号", "试样体积V(ml)", "样品溶液吸光度（A）", "样品溶液吸光度（A）", "样品溶液吸光度（A）", "检测结果m(ug)", "样品浓度C(mg/L)", "备注"],
    ["", "", "", "A1", "A2", "A3", "", "", "", ""]
  ],
  "fields": ["index", "sample_id", "volume", "a1", "a2", "a3", "result", "concentration", "remark"],
  "rows": [
    [1, "S001", 10, 0.123, 0.125, 0.124, 5.6, 0.45, ""],
    [2, "S002", 12.5, 0.201, 0.203, 0.202, 8.1, 0.648, "高"]
  ]
}
    """
    return result


def load_table_structure_by_name(name: str, base_dir: str = "tables") -> dict:
    """
    根据表格名称 name 加载 tables 目录下的 JSON 配置文件。
    文件应命名为 {name}.json。
    """
    json_path = os.path.join(base_dir, f"{name}.json")
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"未找到配置文件: {json_path}")
    
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)



# def is_data_row(row_texts: List[str]) -> bool:
#     """
#     判断是否为数据行：至少半数以上单元格包含数字或小数
#     """
#     numeric_cells = sum(bool(re.search(r'\d', cell)) for cell in row_texts)
#     return numeric_cells >= len(row_toxts) // 2  # 半数以上为数字


def more_than_half_filled(row: List[str]) -> bool:
    non_empty_count = sum(1 for item in row if item.strip() != '')
    return non_empty_count > len(row) / 2


def parse_table_keep_headers(table) -> Dict:
    rows = table.rows
    columns = table.columns
    all_rows = [[cell.text.strip() for cell in row.cells] for row in rows]
    all_columns = [[cell.text.strip() for cell in column.cells] for column in columns]

    header_rows = []
    data_rows = []
    column_width = []

    # 拿到宽度
    for col_idx in range(len(all_columns)):
        cell = table.cell(0, col_idx)
        width = cell.width if cell.width else None
        column_width.append(width)

    first_column = all_columns[0] 
    first_column_all_text_flag = all(item.strip() != '' for item in first_column) # 判断第一列是否全为空

    if first_column_all_text_flag: # 纵向表格(表头在第一列) 标记是否第一列的所有单元格都为空, 如果第一列均有数据，就判断是纵向表头
        structure_type = StructureType.Vertical.value # 默认横向表头
        for col in all_columns:
            is_header = more_than_half_filled(col)
            if not found_column_data and not is_header:
                header_rows.append(col)
            else:
                found_column_data = True
                data_rows.append(col)
    else:  # 横向表格(表头在第一行)
        structure_type = StructureType.Horizontal.value # 默认横向表头
        found_row_data = False
        for row in all_rows:
            is_header = more_than_half_filled(row)
            if not found_row_data and is_header:
                header_rows.append(row)
            else:
                found_row_data = True
                data_rows.append(row)
    return {
        'headers': header_rows,
        'data_rows': data_rows,    # 保留原始二维数据行
        'structure_type': structure_type,
        'column_width': column_width
    }

# 使用示例
# input_file = r'D:\Python\Template1.docx'
# output_file = r'D:\Python\Template1-new.docx'
# bookmarks_to_remove = ["操作步骤","计算公式"]

# delete_bookmark_content(input_file, bookmarks_to_remove, output_file)
# print(f"已删除书签 {bookmarks_to_remove}，新文档保存至 {output_file}")

def lock_table_width_on_document(doc: Document) -> None:
    for table in doc.tables:
        tbl = table._element
        tblPr = tbl.tblPr

        # ... (省略 tblLayout 的设置，确保它是 fixed) ...

        tblW = tblPr.find(qn('w:tblW'))
        if tblW is not None:
            tblW.set(qn('w:type'), 'dxa')
            # 尝试一个更大的宽度，例如 10500 dxa 或 11000 dxa
            # 这个值需要根据您的页面边距和期望的表格大小来定
            tblW.set(qn('w:w'), "10500") # 假设一个更大的值

        # 遍历单元格，确保它们的宽度也设置为 dxa
        # 并且如果需要，可以尝试根据新的表格总宽度均匀分配
        num_cols = len(table.columns)
        if num_cols > 0:
            # 计算每个单元格的平均宽度
            # 这里的 10500 应与上面 tblW 的设置保持一致
            avg_cell_width = str(int(10500 / num_cols))
        else:
            avg_cell_width = "3000" # fallback

        for row in table.rows:
            for cell_idx, cell in enumerate(row.cells):
                tc = cell._element
                tcPr = tc.tcPr

                tcW = tcPr.find(qn('w:tcW'))
                if tcW is not None:
                    tcW.set(qn('w:type'), 'dxa')
                    # 强制设置单元格宽度，使其与表格总宽度一致
                    tcW.set(qn('w:w'), avg_cell_width)
                else:
                    tcW = OxmlElement('w:tcW')
                    tcW.set(qn('w:type'), 'dxa')
                    tcW.set(qn('w:w'), avg_cell_width)
                    tcPr.insert(0, tcW)
from docxtpl import DocxTemplate
from docx import Document
from docx.shared import Cm, Pt, Twips
from docx.oxml.ns import qn, nsmap
from docx.oxml import OxmlElement


def remove_outer_borders_only(table):
    """只移除表格最外圈边框，保留内部网格线"""
    tbl = table._tbl
    tblPr = tbl.tblPr if tbl.tblPr is not None else OxmlElement('w:tblPr')
    tblBorders = OxmlElement('w:tblBorders')
    # 外圈边框设为无
    for border_name in ('top', 'left', 'bottom', 'right'):
        border = OxmlElement(f'w:{border_name}')
        border.set(qn('w:val'), 'nil')
        tblBorders.append(border)
    # 内部网格线保留（single 黑色细线）
    for border_name in ('insideH', 'insideV'):
        border = OxmlElement(f'w:{border_name}')
        border.set(qn('w:val'), 'single')
        border.set(qn('w:sz'), '4')  # 0.5pt
        border.set(qn('w:color'), '000000')
        tblBorders.append(border)
    tblPr.append(tblBorders)
    if tbl.tblPr is None:
        tbl.insert(0, tblPr)


def set_cell_margins(table, margin=0):
    """设置表格所有单元格的内边距为 0（让内容贴边）"""
    tbl = table._tbl
    tblPr = tbl.tblPr if tbl.tblPr is not None else OxmlElement('w:tblPr')
    tblCellMar = OxmlElement('w:tblCellMar')
    for side in ('top', 'left', 'bottom', 'right'):
        node = OxmlElement(f'w:{side}')
        node.set(qn('w:w'), str(margin))
        node.set(qn('w:type'), 'dxa')
        tblCellMar.append(node)
    tblPr.append(tblCellMar)
    if tbl.tblPr is None:
        tbl.insert(0, tblPr)


def set_table_full_width(table, width_twips=9072*20):
    """设置表格宽度为指定值（默认约 16cm ≈ A4 可打印宽度）"""
    tbl = table._tbl
    tblPr = tbl.tblPr if tbl.tblPr is not None else OxmlElement('w:tblPr')
    tblW = OxmlElement('w:tblW')
    tblW.set(qn('w:w'), '5000')  # 5000 = 100% (pct)
    tblW.set(qn('w:type'), 'pct')
    tblPr.append(tblW)
    if tbl.tblPr is None:
        tbl.insert(0, tblPr)


def set_uniform_row_heights(table):
    """
    找到表格中最高的行，将所有行设置为相同高度。
    注意：这是设置最小行高，Word 会在内容超出时自动增高。
    
    :param table: python-docx 表格对象
    """
    # 先获取所有行的高度（如果已设置）
    max_height = 0
    for row in table.rows:
        tr = row._tr
        trPr = tr.trPr
        if trPr is not None:
            trHeight = trPr.find(qn('w:trHeight'))
            if trHeight is not None:
                h = trHeight.get(qn('w:val'))
                if h:
                    max_height = max(max_height, int(h))
    
    # 如果没有找到已设置的高度，使用一个默认值（约 0.5cm = 283 twips）
    if max_height == 0:
        max_height = 283
    
    # 设置所有行为相同高度
    for row in table.rows:
        tr = row._tr
        trPr = tr.get_or_add_trPr()
        # 移除已有的 trHeight
        for existing in trPr.findall(qn('w:trHeight')):
            trPr.remove(existing)
        trHeight = OxmlElement('w:trHeight')
        trHeight.set(qn('w:val'), str(max_height))
        trHeight.set(qn('w:hRule'), 'atLeast')  # atLeast = 最小高度，内容多时自动增高
        trPr.append(trHeight)


def set_first_column_wider(table, first_col_pct=15):
    """
    设置第一列比其他列宽一些（作为表头列）。
    
    :param table: python-docx 表格对象
    :param first_col_pct: 第一列占总宽度的百分比，默认 15%
    """
    if not table.rows:
        return
    
    num_cols = len(table.rows[0].cells)
    if num_cols <= 1:
        return
    
    # 计算其他列的百分比
    remaining_pct = 100 - first_col_pct
    other_col_pct = remaining_pct / (num_cols - 1)
    
    # 百分比转换为 pct 单位（50 = 1%，所以乘以 50）
    first_col_width = int(first_col_pct * 50)
    other_col_width = int(other_col_pct * 50)
    
    for row in table.rows:
        for i, cell in enumerate(row.cells):
            tc = cell._tc
            tcPr = tc.get_or_add_tcPr()
            # 移除已有的 tcW
            for existing in tcPr.findall(qn('w:tcW')):
                tcPr.remove(existing)
            tcW = OxmlElement('w:tcW')
            if i == 0:
                tcW.set(qn('w:w'), str(first_col_width))
            else:
                tcW.set(qn('w:w'), str(other_col_width))
            tcW.set(qn('w:type'), 'pct')
            tcPr.append(tcW)

template_path = 'test_ex.docx' # 模板文件在utils目录下

doc = DocxTemplate(template_path)

# 您的数据，直接对应 JSON 结构
data_for_template = {
  "sample_info_list": [
    {
      "index": 1,
      "id": "S001",
      "volume": 10.0,
      "absorbance": {
        "a1": 0.123,
        "a2": 0.125,
        "a3": 0.124,
        "a_avg": 0.124
      },
      "result": 5.6,
      "concentration": 0.45,
      "remark": ""
    },
    {
      "index": 2,
      "id": "S002",
      "volume": 12.5,
      "absorbance": {
        "a1": 0.201,
        "a2": 0.203,
        "a3": 0.202,
        "a_avg": 0.202
      },
      "result": 8.1,
      "concentration": 0.648,
      "remark": "高"
    }
  ],
}
abs_data_1 = [
        {"label": "管号", "cols": ["1", "2", "3", "4", "5", "6", "7"]},
        {"label": "标准系列, (μg)", "cols": ["0.0", "1.00", "2.00", "6.00", "10.00", "20.00", "30.00"]},
        {"label": "吸光度（A）", "cols": ["1", "5", "8", "12", "16", "20", "24"]},
        {"label": "吸光度均值(A̅)", "cols": ["1", "4", "8", "12", "16", "20", "24"]}
    ]
abs_data_2 = [
        {"label": "扣除空白后", "cols": ["0.5", "1", "4", "7", "19", "11", "14"]}
    ]
data_for_template['abs_data_1'] = abs_data_1
data_for_template['abs_data_2'] = abs_data_2
data_for_template['blank_abs'] = {"label": "空白吸光度A0", "value": "0.5"}

# data_s = {
#   'a': [2131,2123,34124,41241,51241,61241,71241],
#   'b': [512739,612312,712312,812312,912312,1012312,1112312],
#   'c': [212312,312312,412312,512312,612312,712312,812312],
#   'g': [212312,312312,412312,512312,612312,712312,812312]
# }
# data_s = [
#   [2131,2123,34124,41241],
#   [512739,612312,712312,812312],
#   [212312,312312,412312,512312],
#   [212312,312312,412312,512312]
# ]
data_s = {
  'a': [2131,2123],
  'b': [512739,612312],
  'c': [212312,312312],
  'g': [212312,312312]
}
data_for_template['data_s'] = data_s
# `doc.render` 的上下文就是这个数据

grouped_data = [
      {
         "样品编号":"A001",
         "吸光度":"1:10",
         "平均值":"1.25",
         "rows":[
            {
               "样品编号":"A001",
               "浓度":"10ml",
               "吸光度":"1:10",
               "稀释倍数":"1:100",
               "测定值":"1.23",
               "平均值":"1.25"
            },
            {
               "样品编号":"A001",
               "浓度":"20ml",
               "吸光度":"1:10",
               "稀释倍数":"1:100",
               "测定值":"1.27",
               "平均值":"1.25"
            }
         ]
      },
      {
         "样品编号":"B002",
         "吸光度":"1:20",
         "平均值":"2.15",
         "rows":[
            {
               "样品编号":"B002",
               "浓度":"15ml",
               "吸光度":"1:20",
               "稀释倍数":"1:50",
               "测定值":"2.08",
               "平均值":"2.15"
            },
            {
               "样品编号":"B002",
               "浓度":"12ml",
               "吸光度":"1:20",
               "稀释倍数":"1:50",
               "测定值":"2.22",
               "平均值":"2.15"
            }
         ]
      },
      {
         "样品编号":"C003",
         "吸光度":"1:30",
         "平均值":"3.40",
         "rows":[
            {
               "样品编号":"C003",
               "浓度":"18ml",
               "吸光度":"1:30",
               "稀释倍数":"1:200",
               "测定值":"3.35",
               "平均值":"3.40"
            },
            {
               "样品编号":"C003",
               "浓度":"25ml",
               "吸光度":"1:30",
               "稀释倍数":"1:200",
               "测定值":"3.45",
               "平均值":"3.40"
            }
         ]
      }
   ]

dynamic_table = {'header': [1,2,3,4,5,6], 'data_double_list': [['1_vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv','2_vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv','3_vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv','4_vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv','5_vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv','6_vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv'], ['1_vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv','2_vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv','3_vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv','4_vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv','5_vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv','6_vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv']]}
data_for_template['dynamic_table'] = dynamic_table
data_for_template['grouped_data'] = grouped_data
k_values = [{'label': 'k0:', 'value': '1312321312'}, {'label': 'k1:', 'value': '35235235'}, {'label': 'k2:', 'value': '64645645'}, {'label': 'k3:', 'value': '756756756'}]
data_for_template['k_values'] = k_values

sub_table = [
['吸光度', '100', '100', '300', '400', '500', '100', '100', '300', '400', '500', '100', '100', '300', '400', '500'], 
['氧化物含量', '10', '20', '30', '40', '50', '10', '20', '30', '40', '50', '10', '20', '30', '40', '50'], 
['浓度', '10', '20', '30', '40', '50', '10', '20', '30', '40', '50', '10', '20', '30', '40', '50'], 
]
subdoc = doc.new_subdoc()
rows = len(sub_table)
cols = max(len(r) for r in sub_table) if rows else 0

t = subdoc.add_table(rows=rows, cols=cols)
t.style = "Table Grid"
remove_outer_borders_only(t)  # 只去掉外圈边框，保留内部网格线
set_cell_margins(t, margin=0)  # 单元格内边距设为 0
set_table_full_width(t)  # 表格宽度 100%
set_first_column_wider(t, first_col_pct=12)  # 第一列稍宽（作为表头）
for r, row in enumerate(sub_table):
    for c in range(cols):
        t.cell(r, c).text = "" if c >= len(row) or row[c] is None else str(row[c])
data_for_template['subdoc_table'] = subdoc

doc.render(data_for_template)

output_filename = 'report_from_nested_data.docx'
doc.save(output_filename)

# 后处理：把包含嵌套表格的外层单元格内边距设为 0
from docx import Document as DocxDocument
final_doc = DocxDocument(output_filename)
for table in final_doc.tables:
    for row in table.rows:
        for cell in row.cells:
            # 检查单元格里是否有嵌套表格
            if cell.tables:
                # 设置该单元格内边距为 0
                tc = cell._tc
                tcPr = tc.get_or_add_tcPr()
                tcMar = OxmlElement('w:tcMar')
                for side in ('top', 'left', 'bottom', 'right'):
                    node = OxmlElement(f'w:{side}')
                    node.set(qn('w:w'), '0')
                    node.set(qn('w:type'), 'dxa')
                    tcMar.append(node)
                tcPr.append(tcMar)
                
                # 把单元格内所有段落的段前段后间距设为 0
                for para in cell.paragraphs:
                    para.paragraph_format.space_before = Pt(0)
                    para.paragraph_format.space_after = Pt(0)
                    para.paragraph_format.line_spacing = 1.0
                
                # 统一嵌套表格的行高 & 第一列不换行
                for nested_table in cell.tables:
                    # 找出第一列中内容最长的文字
                    max_chars = 0
                    for nested_row in nested_table.rows:
                        if nested_row.cells:
                            text = nested_row.cells[0].text
                            max_chars = max(max_chars, len(text))
                            
                            # 给第一列设置不换行（noWrap），中文也会撑宽而不是换行增高
                            first_cell = nested_row.cells[0]
                            tc = first_cell._tc
                            tcPr = tc.get_or_add_tcPr()
                            noWrap = OxmlElement('w:noWrap')
                            tcPr.append(noWrap)
                    
                    # 根据最长内容估算第一列宽度（用于统一所有行的第一列宽度）
                    # 中文字符约 10.5pt 宽，加点余量
                    char_width_pt = 11
                    first_col_width_pt = max_chars * char_width_pt + 8  # 加点内边距
                    first_col_width_twips = int(first_col_width_pt * 20)  # 1pt = 20 twips
                    
                    # 设置第一列所有行的宽度一致
                    for nested_row in nested_table.rows:
                        if nested_row.cells:
                            first_cell = nested_row.cells[0]
                            tc = first_cell._tc
                            tcPr = tc.get_or_add_tcPr()
                            # 移除已有的 tcW
                            for existing in list(tcPr.findall(qn('w:tcW'))):
                                tcPr.remove(existing)
                            tcW = OxmlElement('w:tcW')
                            tcW.set(qn('w:w'), str(first_col_width_twips))
                            tcW.set(qn('w:type'), 'dxa')
                            tcPr.append(tcW)
final_doc.save(output_filename)

# 再打开生成后的 Word，设置列宽
# docx_doc = Document(output_filename)
# # 遍历所有表格
# print(docx_doc.tables)
# for table in docx_doc.tables:
#     col_count = len(table.columns)
#     print('col_count:', col_count)
#     if col_count == 0:
#         continue

#     # 设置每列宽度（例如平均分 14cm 宽度）
#     col_width = Cm(14 / col_count)
#     for row in table.rows:
#         for cell in row.cells:
#             cell.width = col_width
#     for i in range(col_count):
#         table.columns[i].width = col_width

# 保存最终调整后的 Word 文件




print(f"报告 '{output_filename}' 已成功生成！")
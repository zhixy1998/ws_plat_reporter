from docxtpl import DocxTemplate
from docx import Document
from docx.shared import Cm

template_path = 'test_ex1.docx' # 模板文件在utils目录下

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
data_s = [
  [2131,2123,34124,41241],
  [512739,612312,712312,812312],
  [212312,312312,412312,512312],
  [212312,312312,412312,512312]
]
# data_s = {
#   'a': [2131,2123],
#   'b': [512739,612312],
#   'c': [212312,312312],
#   'g': [212312,312312]
# }
data_for_template['data_s'] = data_s
# `doc.render` 的上下文就是这个数据
doc.render(data_for_template)

output_filename = 'report_from_nested_data.docx'
doc.save(output_filename)

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
import os
from io import BytesIO
from datetime import datetime

from docx.shared import Mm
from docx.oxml.ns import qn
from docx.shared import Cm, Pt
from docxtpl import InlineImage
from docxtpl import DocxTemplate
from docx.oxml import OxmlElement
from jinja2 import Environment, FileSystemLoader

"""
wt: wavelength_table
tt: transmission_table
sl: stray_light 杂散光
bs: baseline_straightness 基线平直度
bdn: baseline_dark_noise 基线暗噪声
sb: spectral_bandwidth 光谱带宽
n: noise 噪声
d: drift 漂移
wen: wavelength_edge_noise 波长边缘噪声
va: voltage_adaptability 电压适应性
ds: dielectric_strength  介电强度
cc: contact_current  接触电流
pg: protective_grounding 保护接地
ir: insulation_resistance 绝缘电阻
av: Sample_cell_accuracy_and_repeatability_verification 样品池准确度于重复性校验
as: appearance_and_structure 外观和结构
result: 结论
"""


def transpose_table(columns, rows):
    """
    将横向表格转换成纵向表格
    
    将原始的行列结构转置，使得原来的每一行变成一列。
    
    Args:
        columns (list): 列头数组，如 ['项目名称', '特征值（nm）', '测量值（nm）', ...]
        rows (list): 数据行数组，每行是一个列表，
                    如 [['氘灯(656.1)', '656.1', '', ...], ['氘灯(486.0)', '486', '', ...], ...]
    
    Returns:
        dict: 转换后的纵向表格，包含：
              - 'columns': 原数据的行索引（如 ['第1行', '第2行', ...]）或第一列的值
              - 'rows': 转置后的行数据，每行对应原来的一列
    
    Example:
        >>> columns = ['A', 'B', 'C']
        >>> rows = [['a1', 'b1', 'c1'], ['a2', 'b2', 'c2']]
        >>> result = transpose_table(columns, rows)
        # 结果：
        # columns: ['行1', '行2']
        # rows: [
        #   ['A', 'a1', 'a2'],
        #   ['B', 'b1', 'b2'],
        #   ['C', 'c1', 'c2']
        # ]
    """
    if not rows or not columns:
        return {'columns': [], 'rows': []}
    
    # 获取原数据的第一列作为新的列头
    # 或者使用行索引
    try:
        # 尝试从第一列获取标签（通常是项目名称）
        new_columns = [row[0] for row in rows]
    except (IndexError, TypeError):
        # 如果失败，使用行索引
        new_columns = [f'第{i+1}行' for i in range(len(rows))]
    
    # 使用 zip 进行矩阵转置
    transposed_rows = list(zip(*rows))
    
    # 将原列头添加到每行的开头
    transposed_data = []
    for i, transposed_row in enumerate(transposed_rows):
        new_row = [columns[i]] + list(transposed_row)
        transposed_data.append(new_row)
    
    return {
        'columns': [''] + new_columns,  # 第一列为空或标签
        'rows': transposed_data
    }


def convert_table_to_dicts(columns, rows):
    """
    将表格数据转换为字典列表
    
    Args:
        columns (list): 列头数组，如 ['项目名称', '特征值（nm）', '测量值（nm）', ...]
        rows (list): 数据行数组，每行是一个列表
    
    Returns:
        list: 字典列表，每个字典的key是列头，value是对应的值
        
    Example:
        >>> columns = ['项目名称', '特征值（nm）', '测量值（nm）']
        >>> rows = [
        ...     ['氘灯(656.1)', '656.1', ''],
        ...     ['氘灯(486.0)', '486', '']
        ... ]
        >>> result = convert_table_to_dicts(columns, rows)
        [
            {'项目名称': '氘灯(656.1)', '特征值（nm）': '656.1', '测量值（nm）': ''},
            {'项目名称': '氘灯(486.0)', '特征值（nm）': '486', '测量值（nm）': ''}
        ]
    """
    if not rows or not columns:
        return []
    
    result = []
    for row in rows:
        row_dict = {}
        for i, column in enumerate(columns):
            # 如果行的长度不足，用空字符串填充
            row_dict[column] = row[i] if i < len(row) else ''
        result.append(row_dict)
    
    return result


def group_dicts_by_field(data_dicts, field_name='项目名称'):
    """
    根据指定字段的值分组字典
    
    将字典列表按照指定字段的值进行分组：
    - 重复出现的值（出现次数>1）对应的字典分别放在各自的list中，形成 [[dict1, dict2], [dict3, dict4, dict5]]
    - 不重复的值（出现次数=1）对应的字典放在一个list中，形成 [dict6, dict7]
    
    Args:
        data_dicts (list): 字典列表
        field_name (str): 用于分组的字段名，默认为'项目名称'
    
    Returns:
        tuple: (repeated_groups_list, unique_list)
               repeated_groups_list: [[dict1, dict2], [dict3, dict4, dict5]] - 重复值的分组
               unique_list: [dict6, dict7] - 不重复值的列表
    
    Example:
        >>> data = [
        ...     {'项目名称': '1', 'value': 'a'},
        ...     {'项目名称': '1', 'value': 'b'},
        ...     {'项目名称': '2', 'value': 'c'},
        ...     {'项目名称': '5', 'value': 'd'},
        ...     {'项目名称': '5', 'value': 'e'},
        ...     {'项目名称': '5', 'value': 'f'}
        ... ]
        >>> repeated, unique = group_dicts_by_field(data)
        # repeated: [[dict1, dict2], [dict3, dict4, dict5]]
        # unique: [dict2]
    """
    if not data_dicts:
        return [], []
    
    # 第一步：统计每个字段值出现的次数
    field_count = {}
    for data_dict in data_dicts:
        field_value = data_dict.get(field_name)
        field_count[field_value] = field_count.get(field_value, 0) + 1
    
    # 第二步：按出现次数分组
    repeated_groups = {}  # {field_value: [dict1, dict2, ...]}
    unique_list = []
    
    for data_dict in data_dicts:
        field_value = data_dict.get(field_name)
        
        if field_count[field_value] > 1:
            # 重复的值
            if field_value not in repeated_groups:
                repeated_groups[field_value] = []
            repeated_groups[field_value].append(data_dict)
        else:
            # 不重复的值
            unique_list.append(data_dict)
    
    # 第三步：将repeated_groups转换为list of lists（保持为多层结构）
    repeated_list = list(repeated_groups.values())
    
    return repeated_list, unique_list


def convert_dicts_to_vertical_table(data_dicts_list):
    """
    将字典列表转换为纵向表格结构
    
    Args:
        data_dicts_list: 字典列表，如 [{'项目名称': '1', '值': 'a'}, {'项目名称': '1', '值': 'b'}, ...]
    
    Returns:
        list: 纵向表格行数据，如 [['项目名称', '1', '1', '2'], ['值', 'a', 'b', 'c'], ...]
              第一列是表头（key），后续列是对应的值（value）
    
    Example:
        >>> data = [
        ...     {'项目名称': '1', '值': 'a'},
        ...     {'项目名称': '1', '值': 'b'},
        ...     {'项目名称': '2', '值': 'c'},
        ... ]
        >>> result = convert_dicts_to_vertical_table(data)
        # result: [['项目名称', '1', '1', '2'], ['值', 'a', 'b', 'c']]
    """
    if not data_dicts_list:
        return []
    
    # 获取所有的key（表头）
    all_keys = set()
    for data_dict in data_dicts_list:
        all_keys.update(data_dict.keys())
    
    all_keys = sorted(list(all_keys))  # 排序以保持一致性
    
    # 构建纵向表格
    vertical_table = []
    for key in all_keys:
        row = [key]  # 第一列是表头
        for data_dict in data_dicts_list:
            row.append(str(data_dict.get(key, '')))  # 后续列是对应的值
        vertical_table.append(row)
    
    return vertical_table


def _remove_outer_borders_only(table):
    """只移除外圈边框，保留内部网格线"""
    tbl = table._tbl
    tblPr = tbl.tblPr
    if tblPr is None:
        tblPr = OxmlElement('w:tblPr')
        tbl.insert(0, tblPr)
    
    tblBorders = OxmlElement('w:tblBorders')
    for border_name in ['top', 'left', 'bottom', 'right', 'insideH', 'insideV']:
        border = OxmlElement(f'w:{border_name}')
        border.set(qn('w:val'), 'none' if border_name in ['top', 'left', 'bottom', 'right'] else 'single')
        border.set(qn('w:sz'), '4')
        border.set(qn('w:space'), '0')
        border.set(qn('w:color'), 'auto')
        tblBorders.append(border)
    
    # 移除已有的边框定义
    existing_borders = tblPr.findall(qn('w:tblBorders'))
    for border in existing_borders:
        tblPr.remove(border)
    
    tblPr.append(tblBorders)


def _set_cell_margins(table, margin=0):
    """设置表格单元格内边距"""
    tbl = table._tbl
    tblPr = tbl.tblPr
    if tblPr is None:
        tblPr = OxmlElement('w:tblPr')
        tbl.insert(0, tblPr)
    
    tblCellMar = OxmlElement('w:tblCellMar')
    for margin_name in ['top', 'left', 'bottom', 'right']:
        mar = OxmlElement(f'w:{margin_name}')
        mar.set(qn('w:w'), str(margin))
        mar.set(qn('w:type'), 'dxa')
        tblCellMar.append(mar)
    
    existing_margins = tblPr.findall(qn('w:tblCellMar'))
    for m in existing_margins:
        tblPr.remove(m)
    
    tblPr.append(tblCellMar)


def _set_table_full_width(table):
    """设置表格宽度为100%"""
    tbl = table._tbl
    tblPr = tbl.tblPr
    if tblPr is None:
        tblPr = OxmlElement('w:tblPr')
        tbl.insert(0, tblPr)
    
    tblW = OxmlElement('w:tblW')
    tblW.set(qn('w:w'), '5000')
    tblW.set(qn('w:type'), 'pct')
    
    existing_widths = tblPr.findall(qn('w:tblW'))
    for width in existing_widths:
        tblPr.remove(width)
    
    tblPr.append(tblW)


def _set_first_column_wider(table, first_col_pct=30):
    """设置第一列宽度"""
    for row in table.rows:
        if row.cells:
            first_cell = row.cells[0]
            tcPr = first_cell._tc.get_or_add_tcPr()
            tcW = OxmlElement('w:tcW')
            tcW.set(qn('w:w'), str(first_col_pct * 100))
            tcW.set(qn('w:type'), 'pct')
            
            existing_widths = tcPr.findall(qn('w:tcW'))
            for width in existing_widths:
                tcPr.remove(width)
            
            tcPr.append(tcW)


def _set_column_widths(table, col_widths, total_width_cm=None):
    """
    设置表格的列宽
    
    Args:
        table: python-docx表格对象
        col_widths: 列宽列表，每个元素是百分比（如 [30, 12, 12, 12]）
        total_width_cm: 表格总宽度（厘米），如果为None则使用默认值
    """
    if not col_widths:
        return
    
    # 设置表格宽度为100%（自适应父容器）
    tbl = table._tbl
    tblPr = tbl.tblPr
    if tblPr is None:
        tblPr = OxmlElement('w:tblPr')
        tbl.insert(0, tblPr)
    
    tblW = OxmlElement('w:tblW')
    tblW.set(qn('w:w'), '5000')  # 5000 = 100% * 50
    tblW.set(qn('w:type'), 'pct')
    
    # 移除已有的宽度设置
    existing_widths = list(tblPr.findall(qn('w:tblW')))
    for width in existing_widths:
        tblPr.remove(width)
    
    tblPr.append(tblW)
    
    # 假设父单元格宽度约为 15 厘米（可以根据实际情况调整）
    if total_width_cm is None:
        total_width_cm = 15
    
    # 1 厘米 = 567 twips (dxa)
    total_width_dxa = int(total_width_cm * 567)
    
    # 为每一列的所有单元格设置宽度（使用 dxa 绝对值）
    for col_idx, width_pct in enumerate(col_widths):
        if col_idx < len(table.columns):
            # 计算该列的实际宽度（dxa）
            col_width_dxa = int(total_width_dxa * width_pct / 100)
            
            # 遍历该列的所有单元格
            for row in table.rows:
                if col_idx < len(row.cells):
                    cell = row.cells[col_idx]
                    tcPr = cell._tc.get_or_add_tcPr()
                    
                    # 移除已有的宽度设置（转为list避免迭代器问题）
                    existing_widths = list(tcPr.findall(qn('w:tcW')))
                    for w in existing_widths:
                        tcPr.remove(w)
                    
                    # 添加新的宽度设置（使用 dxa 绝对值）
                    tcW = OxmlElement('w:tcW')
                    tcW.set(qn('w:w'), str(col_width_dxa))
                    tcW.set(qn('w:type'), 'dxa')
                    tcPr.append(tcW)


class InspectionAndCorrectionReport():
    contexts = {}
    table_data = {}

    def __init__(self, vc_data_list):
        # 获取模板文件的完整路径
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.template_path = os.path.join(current_dir, 'verification_jinja.docx')
        self.logo_image = os.path.join(current_dir, 'img/logo_image.png')

        # 在渲染之前定义图片对象
        self.doc = DocxTemplate(self.template_path)
        self.vc_data_list = vc_data_list
        self.section_index = 1
        
    def run(self):
        env = Environment(
            loader=FileSystemLoader('.'),
            trim_blocks=True,
            lstrip_blocks=True
        )
        # 获取通用数据
        self.get_common_data()
        # 获取波长数据表格的数据
        self.get_wavelength_table()
        # 获取透射比的可见区数据
        self.get_transmission_table()
        # 杂散光
        self.get_stray_light()
        # 基线平直度
        self.get_baseline_straightness()
        # 基线暗噪声
        self.get_baseline_dark_noise()
        # 光谱带宽
        self.get_spectral_bandwidth()
        # 噪声
        self.get_noise()
        # 漂移
        self.get_drift()
        # 波长边缘噪声
        self.wavelength_edge_noise()
        # 电压适应性
        # self.get_voltage_adaptability()
        # 介电强度
        self.dielectric_strength()
        # 接触电流
        self.get_contact_current()
        # 保护接地
        self.get_protective_grounding()
        # 绝缘电阻
        self.get_insulation_resistance()
        # 样品池准确度于重复性校验
        self.get_accuracy_verification()
        # 外观和结构
        self.get_appearance_and_structure()
        # 结论
        self.get_result()
        # 备注
        self.get_remark()
        i = 0
        # for table_name, data in self.table_data.items():
        #     i += 1
        #     data['index'] = i
        # contexts = {'table_data': self.table_data}
        # contexts.update(self.contexts)
        logo_pic = InlineImage(self.doc, self.logo_image, width=Mm(40)) # 指定宽度
        self.contexts['logo_image'] = logo_pic
        self.doc.render(self.contexts, jinja_env=env)
        out_stream = BytesIO()
        self.doc.save(out_stream)
        # 保存一份在本地
        current_dir = os.path.dirname(os.path.abspath(__file__))
        output_filename = os.path.join(current_dir, 'verification_and_calibration_result.docx')
        self.doc.save(output_filename)

        return out_stream

    def create_subdoc_table(self, rows, is_vertical=True, merge_enabled=False, merge_key=None, row_height=None, parent_cell_height=None, width=None):
        """
        创建subdoc表格，支持单元格合并和动态行高
        
        Args:
            rows: 表格行数据，二维列表，每个单元格可以是字符串或字典
                 字符串格式: [["h1", "vh1"], ["h2", "vh2"]]
                 字典格式: [[{'text': 'h1', 'width': 30}, {'text': 'vh1', 'width': 12}], ...]
                 注意: 当使用字典格式时，width参数中的值表示占总宽度的百分比
            is_vertical: 是否为纵向表格（默认True），纵向表格第一列为表头
            merge_enabled: 是否启用单元格合并（默认False）
            merge_key: 合并的key，纵向表格时为行标签名，横向表格时为列标签名
            row_height: 每行的高度（单位：厘米），如果为None则根据parent_cell_height自动计算
            parent_cell_height: 父单元格的高度（单位：厘米），用于计算每行的高度
            width: 表格总宽度（单位：厘米），当rows中存在dict对象时必须传入
        
        Returns:
            subdoc对象，可直接用于模板中的 {{ p sub_doc_name }}
        
        Raises:
            ValueError: 当rows中存在dict对象但未传入width参数时抛出
        """
        if not rows:
            return self.doc.new_subdoc()
        
        # 检查rows中是否存在dict对象
        has_dict = False
        for row in rows:
            for cell in row:
                if isinstance(cell, dict):
                    has_dict = True
                    break
            if has_dict:
                break
        
        # 如果存在dict对象，必须传入width参数
        if has_dict and width is None:
            raise ValueError("当rows中存在dict对象时，必须传入width参数（表格总宽度，单位：厘米）")
        
        # 创建subdoc对象
        subdoc = self.doc.new_subdoc()
        
        # 计算表格维度
        table_rows = len(rows)
        table_cols = max(len(row) for row in rows) if rows else 0
        
        if table_rows == 0 or table_cols == 0:
            return subdoc
        
        # 创建表格
        t = subdoc.add_table(rows=table_rows, cols=table_cols)
        t.style = "Table Grid"
        
        # 移除subdoc中的段落间距和缩进
        for paragraph in subdoc.paragraphs:
            pPr = paragraph._element.get_or_add_pPr()
            # 移除段前段后间距
            spacing = OxmlElement('w:spacing')
            spacing.set(qn('w:before'), '0')
            spacing.set(qn('w:after'), '0')
            spacing.set(qn('w:line'), '240')  # 单倍行距
            spacing.set(qn('w:lineRule'), 'auto')
            
            # 移除已有的spacing
            existing_spacing = pPr.findall(qn('w:spacing'))
            for s in existing_spacing:
                pPr.remove(s)
            pPr.append(spacing)
            
            # 移除段落左右缩进
            ind = OxmlElement('w:ind')
            ind.set(qn('w:left'), '0')
            ind.set(qn('w:right'), '0')
            ind.set(qn('w:hanging'), '0')
            ind.set(qn('w:firstLine'), '0')
            
            existing_inds = pPr.findall(qn('w:ind'))
            for i in existing_inds:
                pPr.remove(i)
            pPr.append(ind)
            
            # 设置段落左对齐
            jc = OxmlElement('w:jc')
            jc.set(qn('w:val'), 'left')
            existing_jcs = pPr.findall(qn('w:jc'))
            for j in existing_jcs:
                pPr.remove(j)
            pPr.append(jc)
        
        # 设置表格样式（移除外边框，只保留内部网格线）
        _remove_outer_borders_only(t)
        _set_cell_margins(t, margin=0)
        
        # 设置表格的左右边距为0，让表格贴边
        tbl = t._tbl
        tblPr = tbl.tblPr
        if tblPr is None:
            tblPr = OxmlElement('w:tblPr')
            tbl.insert(0, tblPr)
        
        # 设置表格边距
        tblMar = OxmlElement('w:tblMar')
        tblMar_attrs = {
            'top': '0',
            'left': '0',
            'bottom': '0',
            'right': '0'
        }
        for margin_name, margin_value in tblMar_attrs.items():
            mar = OxmlElement(f'w:{margin_name}')
            mar.set(qn('w:w'), margin_value)
            mar.set(qn('w:type'), 'dxa')
            tblMar.append(mar)
        
        existing_mars = list(tblPr.findall(qn('w:tblMar')))
        for m in existing_mars:
            tblPr.remove(m)
        tblPr.append(tblMar)
        
        # 设置表格布局为固定布局
        tblLayout = OxmlElement('w:tblLayout')
        tblLayout.set(qn('w:type'), 'fixed')
        
        existing_layouts = list(tblPr.findall(qn('w:tblLayout')))
        for layout in existing_layouts:
            tblPr.remove(layout)
        tblPr.append(tblLayout)
        
        # 收集第一行的列宽信息（用于设置整个表格的列宽）
        # 支持dict（带width百分比）和str（自动平分剩余宽度）混合格式
        col_widths = []
        total_parent_width = 100  # 父单元格总宽度（百分比）
        specified_width = 0  # 已指定的宽度百分比
        none_count = 0  # 需要平分宽度的列数
        
        if rows and len(rows) > 0:
            for c in range(table_cols):
                if c < len(rows[0]):
                    cell_data = rows[0][c]
                    if isinstance(cell_data, dict):
                        cell_width = cell_data.get('width', None)
                        col_widths.append(cell_width)
                        if cell_width is not None:
                            specified_width += cell_width
                        else:
                            none_count += 1
                    else:
                        # 字符串类型，标记为None，后续平分剩余宽度
                        col_widths.append(None)
                        none_count += 1
                else:
                    col_widths.append(None)
                    none_count += 1
        
        # 计算每个None列应该分配的宽度百分比
        if none_count > 0:
            remaining_width = total_parent_width - specified_width
            avg_width = remaining_width / none_count
            # 将None替换为计算出的平均宽度百分比
            col_widths = [avg_width if w is None else w for w in col_widths]
        
        # 填充表格数据
        for r, row_data in enumerate(rows):
            for c in range(table_cols):
                if c < len(row_data):
                    cell_data = row_data[c]
                    
                    # 判断单元格数据类型
                    if isinstance(cell_data, dict):
                        cell_text = cell_data.get('text', '')
                    else:
                        cell_text = str(cell_data)
                else:
                    cell_text = ""
                
                # 设置单元格文本并明确设置字体
                cell = t.cell(r, c)
                cell.text = cell_text
                # 为单元格中的所有段落设置字体
                for paragraph in cell.paragraphs:
                    for run in paragraph.runs:
                        run.font.name = '宋体'
                        run._element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
                        run.font.size = Pt(9)
        
        # 处理单元格合并
        if merge_enabled:
            if is_vertical:
                # 纵向表格：横向合并相同的值
                self._merge_cells_vertical(t, rows, merge_key)
            else:
                # 横向表格：纵向合并相同的值
                self._merge_cells_horizontal(t, rows, merge_key)
        
        # 在合并单元格之后设置列宽（合并会破坏之前的宽度设置）
        if width is not None:
            # 如果指定了width，使用 tblGrid 来强制设置列宽
            self._set_table_grid_widths(t, col_widths, total_width_cm=width)
        else:
            # 没有指定width时，设置表格宽度为100%自适应父单元格
            tblW = OxmlElement('w:tblW')
            tblW.set(qn('w:w'), '5000')  # 5000 = 100%
            tblW.set(qn('w:type'), 'pct')
            
            existing_widths = list(tblPr.findall(qn('w:tblW')))
            for w in existing_widths:
                tblPr.remove(w)
            tblPr.append(tblW)
            
            # 设置表格布局为自动布局，让Word自动分配列宽
            existing_layouts = list(tblPr.findall(qn('w:tblLayout')))
            for layout in existing_layouts:
                tblPr.remove(layout)
            tblLayout_auto = OxmlElement('w:tblLayout')
            tblLayout_auto.set(qn('w:type'), 'autofit')
            tblPr.append(tblLayout_auto)
        
        # 设置行高（在合并单元格之后设置）
        # 如果指定了parent_cell_height，则根据它计算每行高度
        # 否则使用默认的row_height或自动计算
        if row_height is None:
            if parent_cell_height is not None:
                # 根据父单元格高度和行数平均分配（单位：厘米）
                row_height_cm = parent_cell_height / table_rows
                row_height_value = Cm(row_height_cm)
            else:
                # 使用默认高度（可以调整），默认7.6厘米
                parent_cell_height_default = 7.6
                row_height_cm = parent_cell_height_default / table_rows
                row_height_value = Cm(row_height_cm)
        else:
            row_height_value = Cm(row_height)
        
        # 为每一行设置行高和单元格属性
        for row_idx, row in enumerate(t.rows):
            # 设置行高为精确值
            tr = row._tr
            trPr = tr.get_or_add_trPr()
            trHeight = OxmlElement('w:trHeight')
            trHeight.set(qn('w:val'), str(int(row_height_value.twips)))  # 转换为twips
            trHeight.set(qn('w:hRule'), 'atLeast')  # 使用最小高度，内容多时可自动增加
            
            # 移除已有的高度设置
            existing_heights = list(trPr.findall(qn('w:trHeight')))
            for h in existing_heights:
                trPr.remove(h)
            trPr.append(trHeight)
            
            # 设置单元格垂直居中对齐
            for col_idx, cell in enumerate(row.cells):
                # 设置垂直居中
                tc = cell._element
                tcPr = tc.get_or_add_tcPr()
                
                # 先移除已有的vAlign设置
                existing_vAligns = list(tcPr.findall(qn('w:vAlign')))
                for vAlign in existing_vAligns:
                    tcPr.remove(vAlign)
                
                # 添加新的vAlign
                vAlign = OxmlElement('w:vAlign')
                vAlign.set(qn('w:val'), 'center')
                tcPr.append(vAlign)
                
                # ========== 为每个单元格单独设置边框（只保留内侧边框，去掉外边框） ==========
                tcBorders = OxmlElement('w:tcBorders')
                
                # 判断单元格位置，决定是否显示边框
                is_first_row = (row_idx == 0)
                is_last_row = (row_idx == table_rows - 1)
                is_first_col = (col_idx == 0)
                is_last_col = (col_idx == table_cols - 1)
                
                for border_name in ['top', 'left', 'bottom', 'right']:
                    border = OxmlElement(f'w:{border_name}')
                    
                    # 外边框设置为无，内边框设置为单线
                    should_hide = (
                        (border_name == 'top' and is_first_row) or
                        (border_name == 'bottom' and is_last_row) or
                        (border_name == 'left' and is_first_col) or
                        (border_name == 'right' and is_last_col)
                    )
                    
                    if should_hide:
                        border.set(qn('w:val'), 'none')
                        border.set(qn('w:sz'), '0')
                    else:
                        border.set(qn('w:val'), 'single')
                        border.set(qn('w:sz'), '4')
                        border.set(qn('w:color'), '000000')
                    border.set(qn('w:space'), '0')
                    tcBorders.append(border)
                
                # 移除已有的边框定义
                existing_borders = list(tcPr.findall(qn('w:tcBorders')))
                for b in existing_borders:
                    tcPr.remove(b)
                tcPr.append(tcBorders)
                # ================================================================
                
                # 设置单元格内段落无间距和缩进
                for paragraph in cell.paragraphs:
                    pPr = paragraph._element.get_or_add_pPr()
                    spacing = OxmlElement('w:spacing')
                    spacing.set(qn('w:before'), '0')
                    spacing.set(qn('w:after'), '0')
                    spacing.set(qn('w:line'), '240')
                    spacing.set(qn('w:lineRule'), 'auto')
                    
                    existing_spacing = list(pPr.findall(qn('w:spacing')))
                    for s in existing_spacing:
                        pPr.remove(s)
                    pPr.append(spacing)
                    
                    # 移除单元格内段落的缩进
                    ind = OxmlElement('w:ind')
                    ind.set(qn('w:left'), '0')
                    ind.set(qn('w:right'), '0')
                    ind.set(qn('w:hanging'), '0')
                    ind.set(qn('w:firstLine'), '0')
                    
                    existing_inds = list(pPr.findall(qn('w:ind')))
                    for i in existing_inds:
                        pPr.remove(i)
                    pPr.append(ind)
        
        return subdoc

    def _merge_cells_vertical(self, table, rows, merge_key=None):
        """
        纵向表格的单元格合并：横向合并相同的值
        对所有行（除第一列外）检查连续相同的值并合并
        """
        # 遍历所有行
        for row_idx, row_data in enumerate(rows):
            # 找出连续相同的单元格，进行横向合并
            col = 1  # 从第2列开始（第1列是表头）
            while col < len(row_data):
                # 找出与当前单元格相同的连续单元格
                start_col = col
                # 获取当前单元格的文本值
                current_cell = row_data[col]
                current_value = current_cell.get('text') if isinstance(current_cell, dict) else current_cell
                
                # 比较单元格值（支持字典和字符串格式）
                while col < len(row_data):
                    cell = row_data[col]
                    cell_value = cell.get('text') if isinstance(cell, dict) else cell
                    if cell_value != current_value:
                        break
                    col += 1
                
                # 如果有多个相同的单元格，进行合并
                if col - start_col > 1:
                    # 合并从 start_col 到 col-1 的单元格
                    start_cell = table.cell(row_idx, start_col)
                    end_cell = table.cell(row_idx, col - 1)
                    try:
                        table.merge_cells(start_cell, end_cell)
                    except Exception as e:
                        print(f"合并单元格失败 (行{row_idx}, 列{start_col}-{col-1}): {e}")

    def _merge_cells_horizontal(self, table, rows, merge_key=None):
        """
        横向表格的单元格合并：纵向合并相同的值
        对所有列（除第一行外）检查连续相同的值并合并
        """
        # 如果没有数据，直接返回
        if not rows or len(rows) <= 1:
            return
        
        # 获取列数
        num_cols = len(rows[0]) if rows else 0
        
        # 遍历所有列
        for col_idx in range(num_cols):
            # 从第2行开始，找出该列中连续相同的单元格，进行纵向合并
            row = 1  # 从第2行开始（第1行是表头）
            while row < len(rows):
                # 找出与当前单元格相同的连续单元格
                start_row = row
                if col_idx < len(rows[row]):
                    current_cell = rows[row][col_idx]
                    current_value = current_cell.get('text') if isinstance(current_cell, dict) else str(current_cell)
                else:
                    current_value = ""
                
                # 向下找所有相同的值
                while row < len(rows):
                    if col_idx < len(rows[row]):
                        cell = rows[row][col_idx]
                        cell_value = cell.get('text') if isinstance(cell, dict) else str(cell)
                        if cell_value != current_value:
                            break
                    else:
                        break
                    row += 1
                
                # 如果有多个相同的单元格，进行合并
                if row - start_row > 1:
                    # 合并从 start_row 到 row-1 的单元格
                    start_cell = table.cell(start_row, col_idx)
                    end_cell = table.cell(row - 1, col_idx)
                    try:
                        table.merge_cells(start_cell, end_cell)
                    except Exception as e:
                        print(f"合并单元格失败 (列{col_idx}, 行{start_row}-{row-1}): {e}")

    def _set_table_grid_widths(self, table, col_widths, total_width_cm=None):
        """
        使用 tblGrid 强制设置表格列宽
        
        tblGrid 是 Word 中真正控制列宽的元素，不受单元格合并影响
        
        Args:
            table: python-docx表格对象
            col_widths: 列宽列表，每个元素是百分比（如 [12, 22, 22, 22, 22]）
            total_width_cm: 表格总宽度（厘米）
        """
        if not col_widths or total_width_cm is None:
            return
        
        tbl = table._tbl
        
        # 1 厘米 = 567 twips (dxa)
        total_width_dxa = int(total_width_cm * 567)
        
        # 移除已有的 tblGrid
        existing_grids = list(tbl.findall(qn('w:tblGrid')))
        for grid in existing_grids:
            tbl.remove(grid)
        
        # 创建新的 tblGrid
        tblGrid = OxmlElement('w:tblGrid')
        
        for width_pct in col_widths:
            col_width_dxa = int(total_width_dxa * width_pct / 100)
            gridCol = OxmlElement('w:gridCol')
            gridCol.set(qn('w:w'), str(col_width_dxa))
            tblGrid.append(gridCol)
        
        # 将 tblGrid 插入到 tblPr 之后
        tblPr = tbl.tblPr
        if tblPr is not None:
            tblPr.addnext(tblGrid)
        else:
            tbl.insert(0, tblGrid)
        
        # 同时设置表格宽度为固定值
        tblPr = tbl.tblPr
        if tblPr is None:
            tblPr = OxmlElement('w:tblPr')
            tbl.insert(0, tblPr)
        
        # 移除已有的表格宽度设置
        existing_widths = list(tblPr.findall(qn('w:tblW')))
        for w in existing_widths:
            tblPr.remove(w)
        
        # 设置表格宽度为固定值（dxa）
        tblW = OxmlElement('w:tblW')
        tblW.set(qn('w:w'), str(total_width_dxa))
        tblW.set(qn('w:type'), 'dxa')
        tblPr.append(tblW)
        
        # 为每个单元格也设置宽度（双重保险）
        for col_idx, width_pct in enumerate(col_widths):
            col_width_dxa = int(total_width_dxa * width_pct / 100)
            for row in table.rows:
                if col_idx < len(row.cells):
                    cell = row.cells[col_idx]
                    tc = cell._tc
                    tcPr = tc.get_or_add_tcPr()
                    
                    # 移除已有的宽度设置
                    existing_widths = list(tcPr.findall(qn('w:tcW')))
                    for w in existing_widths:
                        tcPr.remove(w)
                    
                    # 添加新的宽度设置
                    tcW = OxmlElement('w:tcW')
                    tcW.set(qn('w:w'), str(col_width_dxa))
                    tcW.set(qn('w:type'), 'dxa')
                    tcPr.append(tcW)


    def get_common_data(self):
        # (你的数据... 保持不变)
        self.contexts['产品型号'] = '---'
        self.contexts['产品编号'] = '---'
        self.contexts['检验员'] = '---'
        self.contexts['insp_date'] = datetime.now().strftime('%Y-%m-%d') # 检验日期
        self.contexts['复核员'] = '---'
        self.contexts['temp'] = '---' # 温度
        self.contexts['相对湿度'] = '---'
        self.contexts['检验结果'] = '--'
        self.contexts['UV_v'] = '---' # 版本号
        self.contexts['UVTouch_v'] = '---'
        self.contexts['检验软件版本号'] = '---'
    
    def get_wavelength_table(self):
        wt = None
        for i in self.vc_data_list:
            if i.get('name') == '波长示值误差与重复性校验':
                wt = i
                break
        head = wt.get('head_data')
        name = wt.get('name')
        repeated = [] # [{'name': '', 'head': [], 'rows': [[]], 'qualified_standard': ''}]
        unique = {'name': name, 'head': head, 'rows': [], 'qualified_standard': ''}
        qualified_line_data = wt.get('qualifiedLine')
        for test_tool, test_info_dict in qualified_line_data.items():
            qualified_standard = test_info_dict.get('qualified_standard')
            row = test_info_dict.get('related_rows')
            if len(row) > 1:
                repeat_dict = {}
                repeat_dict['name'] = name
                repeat_dict['head'] = head
                repeat_dict['qualified_standard'] = qualified_standard
                repeat_dict['rows'] = row
                repeated.append(repeat_dict)
            else:
                now_qualified_standard = unique.get('qualified_standard','')
                if qualified_standard not in now_qualified_standard:
                    unique['qualified_standard'] += qualified_standard
                unique['rows'].append(row[0])
        # print('wt:', wt)
        if wt:

            data_dict_list = convert_table_to_dicts(unique.get('head'), unique.get('rows'))
            form_len = len(unique) + len(repeated)

            wt_contexts = {}
        
            vertical_table = convert_dicts_to_vertical_table(data_dict_list)[::-1]
            # 不修改表格，保持所有列都是字符串格式，会自动平均分配宽度
            
            column_len = len(vertical_table[0])
            add_row = []
            for i in range(column_len):
                if i == 0:
                    add_row.append('波长段')
                else:
                    add_row.append('B段')
            vertical_table.insert(0, add_row)
            print(vertical_table)
            # 为纵向表格创建一个subdoc对象
            # 传入父单元格高度（单位：英寸），如果不传则使用默认值3.0英寸
            sub_doc = self.create_subdoc_table(vertical_table, is_vertical=True, merge_key='项目名称', merge_enabled=True, parent_cell_height=7)
            
            wt_contexts['unique'] = {
                    'name': unique.get('name'),
                    'project_name': unique.get('qualified_standard'),
                    'sub_doc': sub_doc,
                }

            # 处理重复的数据（分组）
            for r in repeated:  # repeated_group是个list of dict
                # 转换为纵向表格
                data_dict_list = convert_table_to_dicts(r.get('head'), r.get('rows'))
                vertical_table = convert_dicts_to_vertical_table(data_dict_list)[::-1]
                # 为纵向表格创建一个subdoc对象
                # 使用相同的父单元格高度确保一致性
                sub_doc = self.create_subdoc_table(vertical_table, is_vertical=True, merge_key='项目名称', merge_enabled=True, parent_cell_height=9.18)
                if wt_contexts.get('repeated') is None:
                    wt_contexts['repeated'] = []    
                wt_contexts['repeated'].append(
                    {
                        'name': r.get('name'),
                        'project_name': r.get('qualified_standard'),
                        'sub_doc': sub_doc
                    }
                )
            wt_contexts['index'] = self.section_index
            self.contexts['wt'] = wt_contexts
            self.section_index += 1

    def get_transmission_table(self):
        tt_contexts = {}
        tt = None
        tt_ultraviolet_ray = None
        for i in self.vc_data_list:
            if i.get('name') == '透射比示值误差与重复性校验可见区':
                tt = i
            if i.get('name') == '透射比示值误差与重复性校验紫外区':
                tt_ultraviolet_ray = i
        if tt:
            head = tt.get('head_data')
            name = tt.get('name')
            repeated = [] # [{'name': '', 'head': [], 'rows': [[]], 'qualified_standard': ''}]
            unique = {'name': name, 'head': head, 'rows': [], 'qualified_standard': ''}
            qualified_line_data = tt.get('qualifiedLine')
            test_tool_str = ''
            for test_tool, test_info_dict in qualified_line_data.items():
                qualified_standard = test_info_dict.get('qualified_standard')
                row = test_info_dict.get('related_rows')
                repeat_dict = {}
                repeat_dict['name'] = name
                repeat_dict['head'] = head
                repeat_dict['qualified_standard'] = qualified_standard
                repeat_dict['rows'] = row
                repeat_dict['test_tool'] = test_tool
                repeated.append(repeat_dict)
            for r in repeated:
                data_dict_list = convert_table_to_dicts(r.get('head'), r.get('rows'))
                vertical_table = convert_dicts_to_vertical_table(data_dict_list)[::-1]
                # percent_filter_title = ''
                # ul_ray_title = ''
                # for i in data_dict_list:
                #     item_name = i.get('项目名称','')
                #     if '%' in item_name and item_name not in ul_ray_title:
                #         percent_filter_title += item_name + '、'
                #     else:
                #         ul_ray_title += item_name
                for index, v in enumerate(vertical_table):
                    if v[0] == '项目名称':
                        break
                vertical_table.pop(index)
                    
                new_vertical_table = [] 
                for v in vertical_table:
                    new_row = []
                    h = v[0]
                    new_row.append({'text':h, 'width': 21})
                    new_row.extend(v[1:])
                    new_vertical_table.append(new_row)
                vertical_table = new_vertical_table

                sub_doc = self.create_subdoc_table(vertical_table, is_vertical=True, merge_key='', merge_enabled=True, parent_cell_height=7, width=13.7)
                if tt_contexts.get('repeated') is None:
                    tt_contexts['repeated'] = []    
                tt_contexts['repeated'].append(
                    {
                        'name': r.get('name'),
                        'test_tool': r.get('test_tool'),
                        'project_name': r.get('qualified_standard'),
                        'sub_doc': sub_doc
                    }
                )
            

        if tt_ultraviolet_ray:
            head = tt_ultraviolet_ray.get('head_data')
            name = tt_ultraviolet_ray.get('name')
            repeated = [] # [{'name': '', 'head': [], 'rows': [[]], 'qualified_standard': ''}]
            unique = {'name': name, 'head': head, 'rows': [], 'qualified_standard': ''}
            qualified_line_data = tt_ultraviolet_ray.get('qualifiedLine')
            for test_tool, test_info_dict in qualified_line_data.items():
                unique['qualified_standard'] = test_info_dict.get('qualified_standard','')
                unique['rows'] = test_info_dict.get('related_rows')
                unique['test_tool'] = test_tool
            
                data_dict_list = convert_table_to_dicts(unique.get('head'), unique.get('rows'))
                vertical_table = convert_dicts_to_vertical_table(data_dict_list)[::-1]
                new_vertical_table = []
                for v in vertical_table:
                    new_row = []
                    h = v[0]
                    new_row.append({'text':h, 'width': 21})
                    new_row.extend(v[1:])
                    new_vertical_table.append(new_row)
                vertical_table = new_vertical_table
                sub_doc = self.create_subdoc_table(vertical_table, is_vertical=True, merge_key='', merge_enabled=True, parent_cell_height=7, width=13.7)
                tt_contexts['unique'] = {
                        'name': unique.get('name'),
                        'test_tool': unique.get('test_tool'),
                        'project_name': unique.get('qualified_standard'),
                        'sub_doc': sub_doc,
                    }
                
        tt_contexts['index'] = self.section_index
        self.contexts['tt'] = tt_contexts
        self.section_index += 1
            
    def get_stray_light(self):
        """
        杂散光
        """
        sl_contexts = {}
        sl = None
        for i in self.vc_data_list:
            if i.get('name') == '杂散光校验':
                sl = i
                break
        head = sl.get('head_data')
        name = sl.get('name')
        repeat = []
        rows = []
        qualified_line_data = sl.get('qualifiedLine')
        for test_tool, test_info_dict in qualified_line_data.items():
            qualified_standard = test_info_dict.get('qualified_standard')
            row = test_info_dict.get('related_rows')
            rows.append(row[0])
 
        # data_dict_list = convert_table_to_dicts(head, rows)
        # vertical_table = convert_dicts_to_vertical_table(data_dict_list)[::-1]
        combined = [head] + rows
        sub_doc = self.create_subdoc_table(combined, is_vertical=False, merge_key='', merge_enabled=True, parent_cell_height=1.2)
        sl_contexts['sub_doc'] = sub_doc
        sl_contexts['name'] = name
        sl_contexts['index'] = self.section_index
        self.section_index += 1

        self.contexts['sl'] = sl_contexts

        # self.contexts['sl'] = {
        #     'index': 4,
        #     'title': '杂散光',
        #     'test_tool_desc': '检验工具',
        #     'test_tool': {'tool_1':{'label': '碘化钠标准溶液', 'value': {'v1': '220nm', 'v2': '<0.01%'}},
        #                   'tool_2':{'label': '亚硝酸钠标准溶液', 'value': {'v1': '360nm', 'v2': '≤0.02%'}},
        #                    },
        #     'test_value_desc': '测量值（%)',
        #     'test_values': {
        #        'headers' : {'v1': 1, 'v2': 2, 'v3': 3},
        #        'data': {'v1': '0.000', 'v2': '0.000', 'v3': '0.000', 'v4': '0.000', 'v5': '0.000', 'v6': '0.000'}
        #     },
        #     'test_result_v': '结果',
        #     'test_results': {'v1': '未检测', 'v2': '未检测'}
        # }
    
    def get_baseline_straightness(self):
        """
        基线平直度
        """
        bs_contexts = {}
        bs = None
        for i in self.vc_data_list:
            if i.get('name') == '基线平直度检验':
                bs = i
                break
        head = bs.get('head_data')
        name = bs.get('name')
        repeat = []
        rows = []
        qualified_line_data = bs.get('qualifiedLine')
        for test_tool, test_info_dict in qualified_line_data.items():
            qualified_standard = test_info_dict.get('qualified_standard')
            row = test_info_dict.get('related_rows')
            rows.append(row[0])
        
        combined = [head] + rows
        new_combined = []
        for c in combined:
            c.pop(0)
            new_combined.append(c)
        combined = new_combined
        sub_doc = self.create_subdoc_table(combined, is_vertical=False, merge_key='', merge_enabled=True, parent_cell_height=1.2)
        bs_contexts['sub_doc'] = sub_doc
        bs_contexts['name'] = name
        bs_contexts['index'] = self.section_index
        self.section_index += 1

        self.contexts['bs'] = bs_contexts


    def get_baseline_dark_noise(self):
        """
        基线暗噪声
        """
        bdn_contexts = {}
        bdn = None
        for i in self.vc_data_list:
            if i.get('name') == '基线暗噪声检验':
                bdn = i
                break
        head = bdn.get('head_data')
        name = bdn.get('name')
        repeat = []
        rows = []
        qualified_line_data = bdn.get('qualifiedLine')
        for test_tool, test_info_dict in qualified_line_data.items():
            qualified_standard = test_info_dict.get('qualified_standard')
            row = test_info_dict.get('related_rows')
            rows.append(row[0])
        
        # for index, r in enumerate(rows):
        #     if r[0] == '项目名称':
        #         break
        #     r.pop(index)
        
        combined = [head] + rows
        new_combined = []
        for c in combined:
            c.pop(0)
            new_combined.append(c)
        combined = new_combined
        sub_doc = self.create_subdoc_table(combined, is_vertical=False, merge_key='', merge_enabled=True, parent_cell_height=1.2)
        bdn_contexts['sub_doc'] = sub_doc
        bdn_contexts['name'] = name
        bdn_contexts['index'] = self.section_index
        self.section_index += 1

        self.contexts['bdn'] = bdn_contexts


    def get_spectral_bandwidth(self):
        """
        光谱带宽
        """
        sb_contexts = {}
        sb = None
        for i in self.vc_data_list:
            if i.get('name') == '光谱带宽与仪器最小光谱带宽':
                sb = i
                break
        head = sb.get('head_data')
        name = sb.get('name')
        repeat = []
        rows = []
        qualified_line_data = sb.get('qualifiedLine')
        for test_tool, test_info_dict in qualified_line_data.items():
            qualified_standard = test_info_dict.get('qualified_standard')
            row = test_info_dict.get('related_rows')
            rows.append(row[0])
        

        data_dict_list = convert_table_to_dicts(head, rows)
        vertical_table = convert_dicts_to_vertical_table(data_dict_list)[::-1]
        sub_doc = self.create_subdoc_table(vertical_table, is_vertical=False, merge_key='', merge_enabled=True, parent_cell_height=1.2)
        sb_contexts['sub_doc'] = sub_doc
        sb_contexts['name'] = name
        sb_contexts['index'] = self.section_index
        sb_contexts['project_name'] = qualified_standard
        self.section_index += 1

        self.contexts['sb'] = sb_contexts
        # self.contexts['sb'] = {
        #     'index': 7,
        #     'title': '光谱带宽',
        #     'standard_v': '不超过标称光谱带宽的±20%',
        #     'corner_cell': '光谱带宽（nm）',
        #     'ch': {'h1': '测量值(nm)', 'h2': '偏差（%）'}, # ch Column header
        #     'rh': {'h1': '氘灯5.0', 'h2': '氘灯2.0', 'h3': '氘灯1.0', 'h4':'氘灯0.5', 'h5': '氘灯0.2'}, # rh Row header
        #     'rows': {'row_1': {'v1': '0.000', 'v2': '0.000', 'v3': '0.000', 'v4': '0.000', 'v5': '0.000'},
        #              'row_2': {'v1': '0.000', 'v2': '0.000', 'v3': '0.000', 'v4': '0.000', 'v5': '0.000'}
        #              }
        # }

    def get_noise(self):
        """
        噪声
        """
        i= 8
        n_contexts = {}
        n = None
        for i in self.vc_data_list:
            if i.get('name') == '噪声检验':
                n = i
                break
        head = n.get('head_data')
        name = n.get('name')
        repeat = []
        rows = []
        qualified_line_data = n.get('qualifiedLine')
        for test_tool, test_info_dict in qualified_line_data.items():
            qualified_standard = test_info_dict.get('qualified_standard')
            row = test_info_dict.get('related_rows')
            rows.append(row[0])
        new_rows = []
        for r in rows:
            new_one_rows = []
            for index, one_row_v in enumerate(r):
                new_one_rows.append(head[index])
                new_one_rows.append(one_row_v)
            new_rows.append(new_one_rows)
        sub_doc = self.create_subdoc_table(new_rows, is_vertical=False, merge_key='', merge_enabled=True, parent_cell_height=1.6)
        n_contexts['sub_doc'] = sub_doc
        n_contexts['name'] = name
        n_contexts['index'] = self.section_index
        self.section_index += 1
        self.contexts['n'] = n_contexts

    def get_drift(self):
        """
        漂移
        """
        d_contexts = {}
        d = None
        for i in self.vc_data_list:
            if i.get('name') == '漂移检验':
                d = i
                break
        head = d.get('head_data')
        name = d.get('name')
        rows = []
        qualified_line_data = d.get('qualifiedLine')
        for test_tool, test_info_dict in qualified_line_data.items():
            qualified_standard = test_info_dict.get('qualified_standard')
            row = test_info_dict.get('related_rows')
            rows = row
        
        new_rows = []
        for r in rows:
            new_one_rows = []
            for index, one_row_v in enumerate(r):
                if index > 1:
                    new_one_rows.append(head[index])
                    new_one_rows.append(one_row_v)
            new_rows.append(new_one_rows)
        d_contexts['sub_doc'] = self.create_subdoc_table(new_rows, is_vertical=False, merge_key='', merge_enabled=True, parent_cell_height=1.6)
        d_contexts['name'] = name
        d_contexts['index'] = self.section_index
        self.section_index += 1
        self.contexts['d'] = d_contexts
    
    def wavelength_edge_noise(self):
        """
        波长边缘噪声
        """
        wen_contexts = {}
        wen = None
        for i in self.vc_data_list:
            if i.get('name') == '波长边缘噪声':
                wen = i
                break
        head = wen.get('head_data')
        head.insert(0, '--')
        name = wen.get('name')
        rows = []
        qualified_line_data = wen.get('qualifiedLine')
        for test_tool, test_info_dict in qualified_line_data.items():
            qualified_standard = test_info_dict.get('qualified_standard')
            row = test_info_dict.get('related_rows')
            rows.append([qualified_standard] + row[0])
        combined = [head] + rows
        wen_contexts['sub_doc'] = self.create_subdoc_table(combined, is_vertical=False, merge_key='', merge_enabled=True, parent_cell_height=1.2)
        wen_contexts['name'] = name
        wen_contexts['index'] = self.section_index
        self.section_index += 1
        self.contexts['wen'] = wen_contexts


    def get_voltage_adaptability(self):
        """
        电压适应性
        """
        va_contexts = {}
        va = None
        for i in self.vc_data_list:
            if i.get('name') == '电压适应性检验':
                va = i
                break
        if va:
            pass
        else:
            self.contexts['va'] = {
            'index': self.section_index,
            'title': '电压适应性',
            'title_v': '--',
            'test_tool_desc': '检验工具',
            'tool_1': '调压器，数字万用表',
            'headers': {'v1': '电压', 'v2': '--', 'v3': '--', 'v4': '--'},
            'data': {
                'row_1': {'v1': '--', 'v2': '', 'v3': '', 'v4': ''},
                'row_2': {'v1': '--', 'v2': '', 'v3': '', 'v4': ''},
                'row_3': {'v1': '--', 'v2': '', 'v3': '', 'v4': ''},
                'row_4': {'v1': '--', 'v2': '', 'v3': '', 'v4': ''},
            }
            }
        self.section_index += 1

    def dielectric_strength(self):
        """
        介电强度
        """
        ds_contexts = {}
        ds = None
        for i in self.vc_data_list:
            if i.get('name') == '介电强度检验':
                ds = i
                break
        if ds:
            head = ds.get('head_data')
            name = ds.get('name')
            rows = []
            qualified_line_data = ds.get('qualifiedLine')
            for test_tool, test_info_dict in qualified_line_data.items():
                qualified_standard = test_info_dict.get('qualified_standard')
                row = test_info_dict.get('related_rows')
                rows = row
        else:
            self.contexts['ds'] = {
                'index': self.section_index,
                'title': '介电强度检验',
                'test_v_1': '--',
                'test_v_desc': '--',
                'test_v_2': '--', # ☑ □
            }

        self.section_index += 1
    def get_contact_current(self):
        self.contexts['cc'] = {
            'index': self.section_index,
            'title': '接触电流检验',
            'condition_1': '---',
            'condition_2': '---',
            'test_tool_desc': '---',
            'test_1': {'desc': '---', 'v': '---'},
            'test_2': {'desc': '---', 'v': '---'}
        }
        self.section_index += 1


    def get_protective_grounding(self):
        self.contexts['pg'] = {
            'index': self.section_index,
            'title': '保护地接地',
            'title_v': '---',
            'test_tool_desc': '---',
            'test_1': {'desc': '---', 'v': '---'},
        }

        self.section_index += 1
    
    def get_insulation_resistance(self):
        self.contexts['ir'] = {
            'index': self.section_index,
            'title': '绝缘电阻',
            'title_v': '--',
            'test_tool_desc': '---',
            'test_1': {'desc': '---', 'v': '---'},
        }
        self.section_index += 1
    
    def get_accuracy_verification(self):
        self.contexts['av'] = {
            'index': self.section_index,
            'title': '样品池准确度于重复性校验',
            'title_v': '---',
            'test_tool_desc': '---',
            'test_1': {'desc': '---', 'v': '---'},
            'test_2': {'desc': '---', 'v': '---'}
        }
        self.section_index += 1
    
    def get_appearance_and_structure(self):
        self.contexts['as'] = {
            'index': self.section_index,
            'title': '外观和结构',
            'title_v': '---',
            'result': '---' # ☑ □
        }

        self.section_index += 1

    def get_result(self):
        self.contexts['result'] = '-----'
    
    def get_remark(self):
        self.contexts['remark'] = """-----"""
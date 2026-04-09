"""
HTML 版检定校准报告生成器（Playwright + Chromium → PDF）

即插即用，替换 InspectionAndCorrectionReport：

  旧代码（docxtpl）：
      from utils.verification_calibration_utils.verification_calibration_handle \\
          import InspectionAndCorrectionReport

  新代码（HTML → PDF）：
      from utils.verification_calibration_utils.html_report.html_report_builder \\
          import HtmlCalibrationReportBuilder as InspectionAndCorrectionReport

  调用：
      iar = InspectionAndCorrectionReport(
          doc=template,            # ← 会被忽略，保留只为兼容
          vc_data_list=...,
          operation_instrument=...
      )
      pdf_stream = iar.run()       # ← 返回 BytesIO（PDF）
"""

import os
import base64
from io import BytesIO
from datetime import datetime
from typing import Optional, List

from jinja2 import Environment, FileSystemLoader
from .html_report_base import BaseHtmlReportBuilder

# HTML 模板所在目录
_TEMPLATE_DIR = os.path.dirname(os.path.abspath(__file__))


class HtmlCalibrationReportBuilder(BaseHtmlReportBuilder):
    """
    专门为“检定校准”提供数据拼装与上下文生成的Builder。
    继承自BaseHtmlReportBuilder，负责数据处理和模板上下文的生成。
    """

    def __init__(self, vc_data_list: list, operation_instrument: str,
                 doc=None, logo_path: str = None, template_html: str = None, **kwargs):
        """
        Args:
            vc_data_list:  Java 接口返回的 worksheets 列表
            operation_instrument:  仪器型号，如 'T600T700'
            doc:  兼容旧接口，传入后会被忽略
            logo_path:  logo 图片路径，默认自动查找
            template_html:  HTML 模板字符串（从数据库取出的），
                            如果不传则使用文件系统中的 calibration_report.html
        """
        super().__init__(template_html=template_html, template_file='calibration_report.html')

        self.vc_data_list = vc_data_list or []
        self.operation_instrument = operation_instrument
        self.section_index = 1

        # logo 图片路径
        if logo_path and os.path.exists(logo_path):
            self.logo_path = logo_path
        else:
            self.logo_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                'img', 'persee_logo_image.png'
            )



    # ================================================================
    # 上下文构建 —— 遍历 vc_data_list，有什么就渲染什么
    # ================================================================

    def _build_context(self) -> dict:
        ctx = {}

        # --- 基本信息 ---
        ctx['title'] = (
            self.operation_instrument
            + '系列紫外可见分光光度计整机检验原始记录表'
        )
        ctx['insp_date'] = datetime.now().strftime('%Y-%m-%d')
        ctx['temp'] = ''
        ctx['humidity'] = ''
        ctx['inspection_result'] = ''
        ctx['uv_version'] = ''
        ctx['software_version'] = ''
        ctx['logo_base64'] = self._read_logo_base64()
        ctx['logo_path'] = ''

        # --- 动态检测项 ---
        self.section_index = 1

        # 条件渲染的项目（接口返回什么就渲染什么）
        conditional_sections = [
            ('wt',         self._extract_wavelength),
            ('tt',         self._extract_transmission),
            ('sl',         self._extract_stray_light),
            ('bs',         self._extract_baseline_straightness),
            ('bdn',        self._extract_baseline_dark_noise),
            ('sb',         self._extract_spectral_bandwidth),
            ('n',          self._extract_noise),
            ('d',          self._extract_drift),
            ('wen',        self._extract_wavelength_edge_noise),
        ]

        for key, extractor in conditional_sections:
            result = extractor()
            if result is not None:
                ctx[key] = result

        # 无条件渲染的项目（与原代码一致，接口没数据也显示 ---）
        always_sections = [
            ('ds',         self._extract_dielectric_strength,  '介电强度检验'),
            ('cc',         self._extract_contact_current,      '接触电流检验'),
            ('pg',         self._extract_protective_grounding, '保护地接地'),
            ('ir',         self._extract_insulation_resistance,'绝缘电阻'),
            ('av',         self._extract_accuracy_verification,'样品池准确度与重复性校验'),
            ('appearance', self._extract_appearance,           '外观和结构'),
        ]

        for key, extractor, default_name in always_sections:
            result = extractor()
            if result is not None:
                ctx[key] = result
            else:
                # 无数据时也要显示（占位），与原代码一致
                ctx[key] = {
                    'index': self._next_index(),
                    'name': default_name,
                    'headers': [],
                    'rows': [],
                }

        # --- 结论 & 备注 ---
        ctx['result'] = ''
        ctx['remark'] = ''

        return ctx

    # ================================================================
    # 辅助方法
    # ================================================================

    def _find_item(self, name: str) -> Optional[dict]:
        """在 vc_data_list 中按 name 查找"""
        for item in self.vc_data_list:
            if item.get('name') == name:
                return item
        return None

    def _next_index(self) -> int:
        idx = self.section_index
        self.section_index += 1
        return idx

    @staticmethod
    def _format_qs(qs: str) -> str:
        """
        格式化 qualified_standard 文本，在合适位置插入换行<br>。
        例如：
          '波长示值误差:0.1:波长重复性:0.1波长示值误差:0.3:波长重复性:0.1'
        →
          '波长示值误差:0.1<br>波长重复性:0.1<br>波长示值误差:0.3<br>波长重复性:0.1'
        """
        import re
        if not qs:
            return qs
        # 在"数字+中文"交界处插入 <br>（如 0.1波长 → 0.1<br>波长）
        result = re.sub(r'(\d(?:\.\d+)?)([\u4e00-\u9fff])', r'\1<br>\2', qs)
        return result

    def _read_logo_base64(self) -> str:
        try:
            with open(self.logo_path, 'rb') as f:
                return base64.b64encode(f.read()).decode()
        except Exception:
            return ''

    # ================================================================
    # 各检测项提取 —— 数据处理逻辑完全按照原代码
    # 有数据 → 返回 dict;  无数据 → 返回 None
    # ================================================================

    def _extract_wavelength(self) -> Optional[dict]:
        """
        波长示值误差与重复性校验
        对应原 get_wavelength_table()
        原逻辑：
          1. 分 unique（单行工具）和 repeated（多行工具）
          2. convert_table_to_dicts → convert_dicts_to_vertical_table[::-1] 转置
          3. 前面插入一行 ['波长段', 'B段', 'B段', ...]
          4. qualified_standard 作为单独一列显示
        """
        wt = self._find_item('波长示值误差与重复性校验')
        if not wt:
            return None

        head = wt.get('head_data', [])
        qualified_line_data = wt.get('qualifiedLine', {})

        # 区分 repeated（多行）和 unique（单行）
        repeated_groups = []
        unique_rows = []
        unique_qualified = ''

        for test_tool, test_info_dict in qualified_line_data.items():
            qualified_standard = test_info_dict.get('qualified_standard', '')
            rows = test_info_dict.get('related_rows', [])
            if len(rows) > 1:
                repeated_groups.append({
                    'qualified_standard': qualified_standard,
                    'head': head,
                    'rows': rows,
                })
            else:
                if qualified_standard and qualified_standard not in unique_qualified:
                    unique_qualified += qualified_standard
                if rows:
                    unique_rows.append(rows[0])

        result = {
            'index': self._next_index(),
            'name': '波长示值误差与重复性校验',
        }

        # unique 部分 → 转置（加 波长段 行）
        if unique_rows:
            vt = self._to_vertical_table(head, unique_rows, add_wave_row=True)
            result['unique'] = {
                'qualified_standard': self._format_qs(unique_qualified),
                'vertical_rows': vt,
            }

        # repeated 部分 → 各自转置（加 波长段 行）
        if repeated_groups:
            repeated_results = []
            for g in repeated_groups:
                vt = self._to_vertical_table(g['head'], g['rows'], add_wave_row=True)
                repeated_results.append({
                    'qualified_standard': self._format_qs(g['qualified_standard']),
                    'vertical_rows': vt,
                })
            result['repeated'] = repeated_results

        # 计算总行数（给模板 rowspan 用）
        row_count = 0
        if result.get('unique'):
            row_count += 1
        if result.get('repeated'):
            row_count += len(result['repeated'])
        result['row_count'] = row_count

        return result

    def _extract_transmission(self) -> Optional[dict]:
        """
        透射比示值误差与重复性校验（可见区 + 紫外区）
        对应原 get_transmission_table()
        原逻辑：同样转置，且去掉"项目名称"行
        """
        tt_vis = self._find_item('透射比示值误差与重复性校验可见区')
        tt_uv = self._find_item('透射比示值误差与重复性校验紫外区')

        if not tt_vis and not tt_uv:
            return None

        groups = []
        for item in [tt_vis, tt_uv]:
            if not item:
                continue
            head = item.get('head_data', [])
            qualified_line_data = item.get('qualifiedLine', {})
            for test_tool, test_info_dict in qualified_line_data.items():
                rows = test_info_dict.get('related_rows', [])
                if rows:
                    vt = self._to_vertical_table(head, rows, add_wave_row=False)
                    # 原代码：去掉"项目名称"行
                    vt = [r for r in vt if r[0] != '项目名称']
                    groups.append({
                        'test_tool': test_tool,
                        'qualified_standard': self._format_qs(
                            test_info_dict.get('qualified_standard', '')
                        ),
                        'vertical_rows': vt,
                    })

        if not groups:
            return None

        return {
            'index': self._next_index(),
            'name': '透射比示值误差与重复性校验',
            'groups': groups,
            'total_rows': len(groups),
        }

    @staticmethod
    def _to_vertical_table(head: list, rows: list, add_wave_row: bool = False) -> list:
        """
        将横向表格转置为纵向表格（与原 convert_dicts_to_vertical_table[::-1] 等效）。

        Args:
            head:  列头 ['项目名称', '特征值(nm)', ...]
            rows:  数据行 [['氘灯(486.0)', '486', ...], ...]
            add_wave_row:  是否在最前面插入 ['波长段', 'B段', ...] 行
        """
        if not head or not rows:
            return []

        # step 1: convert_table_to_dicts
        data_dicts = []
        for row in rows:
            d = {}
            for i, h in enumerate(head):
                d[h] = row[i] if i < len(row) else ''
            data_dicts.append(d)

        # step 2: convert_dicts_to_vertical_table（保持 head 原始顺序）
        vertical = []
        for key in head:
            vrow = [key]
            for d in data_dicts:
                vrow.append(str(d.get(key, '')))
            vertical.append(vrow)

        # step 3: [::-1] 倒序
        vertical = vertical[::-1]

        # step 4: 仅波长表格插入"波长段"行
        if add_wave_row and vertical:
            col_count = len(vertical[0])
            wave_row = ['波长段'] + ['B段'] * (col_count - 1)
            vertical.insert(0, wave_row)

        return vertical

    def _extract_stray_light(self) -> Optional[dict]:
        """
        杂散光校验
        对应原 get_stray_light()
        原逻辑：combined = [head] + rows（每个工具取 row[0]）
        """
        sl = self._find_item('杂散光校验')
        if not sl:
            return None

        head = sl.get('head_data', [])
        qualified_line_data = sl.get('qualifiedLine', {})
        rows = []
        for test_tool, test_info_dict in qualified_line_data.items():
            row = test_info_dict.get('related_rows', [])
            if row:
                rows.append(row[0])

        if not rows:
            return None

        return {
            'index': self._next_index(),
            'name': sl.get('name', '杂散光校验'),
            'headers': head,
            'rows': rows,
        }

    def _extract_baseline_straightness(self) -> Optional[dict]:
        """
        基线平直度检验
        对应原 get_baseline_straightness()
        原逻辑：combined = [head] + rows，然后 pop(0) 去掉第一列
        """
        bs = self._find_item('基线平直度检验')
        if not bs:
            return None

        head = list(bs.get('head_data', []))
        qualified_line_data = bs.get('qualifiedLine', {})
        rows = []
        for test_tool, test_info_dict in qualified_line_data.items():
            row = test_info_dict.get('related_rows', [])
            if row:
                rows.append(list(row[0]))

        if not rows:
            return None

        # 原代码：c.pop(0) 去掉每行第一列
        if head:
            head = head[1:]
        rows = [r[1:] for r in rows if len(r) > 1]

        return {
            'index': self._next_index(),
            'name': bs.get('name', '基线平直度检验'),
            'headers': head,
            'rows': rows,
        }

    def _extract_baseline_dark_noise(self) -> Optional[dict]:
        """
        基线暗噪声检验
        对应原 get_baseline_dark_noise()
        原逻辑：同基线平直度，pop(0) 去掉第一列
        """
        bdn = self._find_item('基线暗噪声检验')
        if not bdn:
            return None

        head = list(bdn.get('head_data', []))
        qualified_line_data = bdn.get('qualifiedLine', {})
        rows = []
        for test_tool, test_info_dict in qualified_line_data.items():
            row = test_info_dict.get('related_rows', [])
            if row:
                rows.append(list(row[0]))

        if not rows:
            return None

        # 去掉第一列
        if head:
            head = head[1:]
        rows = [r[1:] for r in rows if len(r) > 1]

        return {
            'index': self._next_index(),
            'name': bdn.get('name', '基线暗噪声检验'),
            'headers': head,
            'rows': rows,
        }

    def _extract_spectral_bandwidth(self) -> Optional[dict]:
        """
        光谱带宽
        对应原 get_spectral_bandwidth()
        原逻辑：转成 vertical_table（转置表格）
        """
        sb = self._find_item('光谱带宽与仪器最小光谱带宽')
        if not sb:
            return None

        head = sb.get('head_data', [])
        qualified_line_data = sb.get('qualifiedLine', {})
        rows = []
        qualified_standard = ''
        for test_tool, test_info_dict in qualified_line_data.items():
            qualified_standard = test_info_dict.get('qualified_standard', '')
            row = test_info_dict.get('related_rows', [])
            if row:
                rows.append(row[0])

        if not rows:
            return None

        return {
            'index': self._next_index(),
            'name': '光谱带宽',
            'headers': head,
            'rows': rows,
            'qualified_standard': qualified_standard,
        }

    def _extract_noise(self) -> Optional[dict]:
        """
        噪声检验
        对应原 get_noise()
        原逻辑：header 和 value 交错排列 → [h1, v1, h2, v2, ...]
        """
        n = self._find_item('噪声检验')
        if not n:
            return None

        head = n.get('head_data', [])
        qualified_line_data = n.get('qualifiedLine', {})
        rows = []
        for test_tool, test_info_dict in qualified_line_data.items():
            row = test_info_dict.get('related_rows', [])
            if row:
                rows.append(row[0])

        if not rows:
            return None

        # 原代码：交错排列 header 和 value
        new_rows = []
        for r in rows:
            new_one_row = []
            for index, val in enumerate(r):
                if index < len(head):
                    new_one_row.append(head[index])
                new_one_row.append(val)
            new_rows.append(new_one_row)

        return {
            'index': self._next_index(),
            'name': '噪声检验',
            'headers': [],  # 交错后无单独 header 行
            'rows': new_rows,
        }

    def _extract_drift(self) -> Optional[dict]:
        """
        漂移检验
        对应原 get_drift()
        原逻辑：跳过前2列，剩余的 header+value 交错排列
        """
        d = self._find_item('漂移检验')
        if not d:
            return None

        head = d.get('head_data', [])
        qualified_line_data = d.get('qualifiedLine', {})
        rows = []
        for test_tool, test_info_dict in qualified_line_data.items():
            row = test_info_dict.get('related_rows', [])
            rows = row  # 原代码：直接覆盖 rows = row

        if not rows:
            return None

        # 原代码：跳过 index <= 1，交错排列
        new_rows = []
        for r in rows:
            new_one_row = []
            for index, val in enumerate(r):
                if index > 1:
                    if index < len(head):
                        new_one_row.append(head[index])
                    new_one_row.append(val)
            new_rows.append(new_one_row)

        return {
            'index': self._next_index(),
            'name': '漂移检验',
            'headers': [],
            'rows': new_rows,
        }

    def _extract_wavelength_edge_noise(self) -> Optional[dict]:
        """
        波长边缘噪声
        对应原 wavelength_edge_noise()
        原逻辑：head 前插 '--'，每行前插 qualified_standard
        """
        wen = self._find_item('波长边缘噪声')
        if not wen:
            return None

        head = list(wen.get('head_data', []))
        head.insert(0, '')
        qualified_line_data = wen.get('qualifiedLine', {})
        rows = []
        for test_tool, test_info_dict in qualified_line_data.items():
            qs = test_info_dict.get('qualified_standard', '')
            row = test_info_dict.get('related_rows', [])
            if row:
                rows.append([qs] + list(row[0]))

        if not rows:
            return None

        return {
            'index': self._next_index(),
            'name': '波长边缘噪声',
            'headers': head,
            'rows': rows,
        }

    def _extract_dielectric_strength(self) -> Optional[dict]:
        """
        介电强度检验
        对应原 dielectric_strength()
        """
        ds = self._find_item('介电强度检验')
        if not ds:
            return None

        head = ds.get('head_data', [])
        qualified_line_data = ds.get('qualifiedLine', {})
        rows = []
        for test_tool, test_info_dict in qualified_line_data.items():
            row = test_info_dict.get('related_rows', [])
            rows = row

        return {
            'index': self._next_index(),
            'name': '介电强度检验',
            'headers': head,
            'rows': rows if rows else [],
        }

    def _extract_contact_current(self) -> Optional[dict]:
        """
        接触电流检验
        对应原 get_contact_current()
        """
        cc = self._find_item('接触电流检验')
        if not cc:
            return None

        head = cc.get('head_data', [])
        qualified_line_data = cc.get('qualifiedLine', {})
        rows = []
        for test_tool, test_info_dict in qualified_line_data.items():
            row = test_info_dict.get('related_rows', [])
            for r in row:
                rows.append(r)

        return {
            'index': self._next_index(),
            'name': '接触电流检验',
            'headers': head,
            'rows': rows if rows else [],
        }

    def _extract_protective_grounding(self) -> Optional[dict]:
        """
        保护地接地
        对应原 get_protective_grounding()
        """
        pg = self._find_item('保护地接地')
        if not pg:
            return None

        head = pg.get('head_data', [])
        qualified_line_data = pg.get('qualifiedLine', {})
        rows = []
        for test_tool, test_info_dict in qualified_line_data.items():
            row = test_info_dict.get('related_rows', [])
            for r in row:
                rows.append(r)

        return {
            'index': self._next_index(),
            'name': '保护地接地',
            'headers': head,
            'rows': rows if rows else [],
        }

    def _extract_insulation_resistance(self) -> Optional[dict]:
        """
        绝缘电阻
        对应原 get_insulation_resistance()
        """
        ir = self._find_item('绝缘电阻')
        if not ir:
            return None

        head = ir.get('head_data', [])
        qualified_line_data = ir.get('qualifiedLine', {})
        rows = []
        for test_tool, test_info_dict in qualified_line_data.items():
            row = test_info_dict.get('related_rows', [])
            for r in row:
                rows.append(r)

        return {
            'index': self._next_index(),
            'name': '绝缘电阻',
            'headers': head,
            'rows': rows if rows else [],
        }

    def _extract_accuracy_verification(self) -> Optional[dict]:
        """
        样品池准确度与重复性校验
        对应原 get_accuracy_verification()
        """
        av = self._find_item('样品池准确度于重复性校验')
        if not av:
            return None

        head = av.get('head_data', [])
        qualified_line_data = av.get('qualifiedLine', {})
        rows = []
        for test_tool, test_info_dict in qualified_line_data.items():
            row = test_info_dict.get('related_rows', [])
            for r in row:
                rows.append(r)

        return {
            'index': self._next_index(),
            'name': '样品池准确度与重复性校验',
            'headers': head,
            'rows': rows if rows else [],
        }

    def _extract_appearance(self) -> Optional[dict]:
        """
        外观和结构
        对应原 get_appearance_and_structure()
        """
        item = self._find_item('外观和结构')
        if not item:
            return None

        head = item.get('head_data', [])
        qualified_line_data = item.get('qualifiedLine', {})
        rows = []
        for test_tool, test_info_dict in qualified_line_data.items():
            row = test_info_dict.get('related_rows', [])
            for r in row:
                rows.append(r)

        return {
            'index': self._next_index(),
            'name': '外观和结构',
            'headers': head,
            'rows': rows if rows else [],
        }

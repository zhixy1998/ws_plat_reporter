import json
import os
import shutil
from datetime import datetime
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.chart import BarChart, Reference


#Excel操作类
class ExcelDataWriter:
    def __init__(self, config_path):
        self.config = self.load_config(config_path)
        self.wb = None
        self.sheet = None

    def load_config(self, config_path):
        """加载JSON配置文件"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            raise RuntimeError(f"配置文件加载失败: {str(e)}")

    def backup_file(self, file_path):
        """创建文件备份"""
        if not os.path.exists(file_path):
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = os.path.join(os.path.dirname(file_path), "backups")
        os.makedirs(backup_dir, exist_ok=True)

        filename = os.path.basename(file_path)
        backup_path = os.path.join(backup_dir, f"{timestamp}_{filename}")

        shutil.copy2(file_path, backup_path)
        return backup_path

    def apply_formatting(self, cell, format_config):
        """应用单元格格式"""
        # 字体格式
        if 'font' in format_config:
            font_config = format_config['font']
            font = Font(
                bold=font_config.get('bold', False),
                italic=font_config.get('italic', False),
                size=font_config.get('size', 11),
                color=font_config.get('color', '000000')
            )
            cell.font = font

        # 背景填充
        if 'fill' in format_config:
            fill_config = format_config['fill']
            fill = PatternFill(
                start_color=fill_config.get('bg_color', 'FFFFFF'),
                end_color=fill_config.get('bg_color', 'FFFFFF'),
                fill_type="solid"
            )
            cell.fill = fill

        # 边框
        if 'border' in format_config:
            border_config = format_config['border']
            border_style = border_config.get('style', 'thin')
            border_color = border_config.get('color', '000000')

            side = Side(border_style=border_style, color=border_color)
            cell.border = Border(
                left=side, right=side, top=side, bottom=side
            )

        # 对齐方式
        if 'alignment' in format_config:
            align_config = format_config['alignment']
            alignment = Alignment(
                horizontal=align_config.get('horizontal', 'general'),
                vertical=align_config.get('vertical', 'bottom'),
                wrap_text=align_config.get('wrap_text', False),
                shrink_to_fit=align_config.get('shrink_to_fit', False)
            )
            cell.alignment = alignment

        # 数字格式
        if 'number_format' in format_config:
            cell.number_format = format_config['number_format']

    def write_data(self, data_dict):
        """
        根据配置和提供的数据写入Excel
        :param data_dict: 包含所有要写入的数据的字典
        """
        excel_config = self.config['excel_settings']
        file_path = excel_config['file_path']

        # 创建必要的目录
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        # 备份处理
        if excel_config.get('backup', False) and os.path.exists(file_path):
            backup_path = self.backup_file(file_path)
            print(f"已创建备份: {backup_path}")

        # 打开或创建工作簿
        if os.path.exists(file_path):
            self.wb = openpyxl.load_workbook(file_path)
        else:
            self.wb = openpyxl.Workbook()

        # 获取或创建工作表
        sheet_name = excel_config['sheet_name']
        if sheet_name in self.wb.sheetnames:
            self.sheet = self.wb[sheet_name]
        else:
            self.sheet = self.wb.create_sheet(title=sheet_name)

        # 清空工作表内容（保留格式）
        """self.sheet.delete_rows(1, self.sheet.max_row)"""

        # 应用数据位置配置
        for position_id, position_config in self.config['data_positions'].items():
            print(f"position_id:{position_id}")
            # 获取对应数据，如果未提供则跳过
            position_data = data_dict.get(position_id)
            if position_data is None:
                continue

            if (position_id == "report_title" or position_id=="sampleType" or position_id=="measureName" or position_id=="measureDate"
                    or position_id=="measureMethod") or position_id=="deviceType" or position_id=="deviceModel" or position_id=="SN":
                self.write_title(position_config, position_data)
            elif position_id == "headers":
                self.write_headers(position_config)
            elif position_id == "measure_datas":
                self.write_monthly_data(position_config, position_data)
            elif position_id == "summary_datas":
                self.write_summary(position_config, position_data)
            elif position_id == "footer_notes":
                self.write_footer_notes(position_config, position_data)

        # 应用后处理
        self.apply_post_processing()

        # 保存文件
        self.wb.save(file_path)
        print(f"数据已成功写入到 {file_path}")

        return file_path

    def write_title(self, config, title_text):
        """写入报告标题"""
        cell_ref = config['cell']
        merge_range = config.get('merge')
        format_config = config.get('format', {})

        # 写入标题文本
        self.sheet[cell_ref] = title_text

        # 应用格式
        self.apply_formatting(self.sheet[cell_ref], format_config)

        # 合并单元格
        if merge_range:
            self.sheet.merge_cells(merge_range)
            # 应用合并后的格式
            top_left_cell = self.sheet[merge_range.split(':')[0]]
            self.apply_formatting(top_left_cell, format_config)

    def write_headers(self, config):
        """写入列标题"""
        start_cell = config['start_cell']
        orientation = config.get('orientation', 'horizontal')
        columns = config['columns']
        header_format = config.get('header_format', {})

        # 解析起始单元格
        start_col, start_row = openpyxl.utils.cell.coordinate_to_tuple(start_cell)

        # 写入列标题
        for col_idx, col_config in enumerate(columns):
            col_letter = get_column_letter(start_col + col_idx)
            cell = self.sheet[f"{col_letter}{start_row}"]
            cell.value = col_config['header']

            # 应用列格式
            self.apply_formatting(cell, header_format)

            # 设置列宽
            if 'width' in col_config:
                self.sheet.column_dimensions[col_letter].width = col_config['width']

    def write_monthly_data(self, config, monthly_data):
        """写入月度数据"""
        start_cell = config['start_cell']
        orientation = config.get('orientation', 'vertical')
        data_format = config.get('data_format', {})

        # 解析起始单元格
        start_row,start_col = openpyxl.utils.cell.coordinate_to_tuple(start_cell)

        # 写入数据行
        for row_idx, row_data in enumerate(monthly_data):
            for col_idx, value in enumerate(row_data):
                col_letter = get_column_letter(start_col + col_idx)
                cell = self.sheet[f"{col_letter}{start_row + row_idx}"]
                cell.value = value

                # 应用通用格式
                if 'general' in data_format:
                    self.apply_formatting(cell, data_format['general'])

                # 应用列特定格式
                """
                if 'columns' in data_format:
                    # 获取列标题（从headers配置中）
                    headers_config = self.config['data_positions']['headers']['columns']
                    if col_idx < len(headers_config):
                        col_name = headers_config[col_idx]['header']
                        if col_name in data_format['columns']:
                            self.apply_formatting(cell, data_format['columns'][col_name])
                            """

    def write_summary(self, config, summary_data):
        """写入季度摘要"""
        start_cell = config['start_cell']
        orientation = config.get('orientation', 'vertical')
        labels = config.get('labels', [])
        values_format = config.get('values_format', {})

        # 解析起始单元格
        start_col, start_row = openpyxl.utils.cell.coordinate_to_tuple(start_cell)

        # 写入标签
        for idx, label in enumerate(labels):
            cell = self.sheet.cell(row=start_row + idx, column=start_col)
            cell.value = label

        # 写入值
        for idx, value in enumerate(summary_data):
            cell = self.sheet.cell(row=start_row + idx, column=start_col + 1)
            cell.value = value
            self.apply_formatting(cell, values_format)

    def write_footer_notes(self, config, note_text):
        """写入页脚注释"""
        cell_ref = config['cell']
        format_config = config.get('format', {})

        # 写入注释文本
        self.sheet[cell_ref] = note_text

        # 应用格式
        self.apply_formatting(self.sheet[cell_ref], format_config)

        # 设置行高
        if 'height' in config:
            row_idx = openpyxl.utils.cell.coordinate_to_tuple(cell_ref)[1]
            self.sheet.row_dimensions[row_idx].height = config['height']

    def apply_post_processing(self):
        """应用后处理操作"""
        if not self.config.get('post_processing'):
            return

        pp_config = self.config['post_processing']

        # 自动调整列宽
        if pp_config.get('autofit_columns', False):
            for column in self.sheet.columns:
                max_length = 0
                column_letter = get_column_letter(column[0].column)

                # 计算最大列宽
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass

                # 设置列宽（增加一点缓冲）
                adjusted_width = (max_length + 2) * 1.2
                self.sheet.column_dimensions[column_letter].width = adjusted_width

        # 冻结窗格
        if 'freeze_panes' in pp_config:
            self.sheet.freeze_panes = pp_config['freeze_panes']

        # 添加图表
        if 'add_chart' in pp_config:
            chart_config = pp_config['add_chart']
            self.add_chart(chart_config)

    def add_chart(self, config):
        """添加图表到工作表"""
        # 创建图表对象
        if config['type'] == 'bar':
            chart = BarChart()
        else:
            # 默认为柱状图
            chart = BarChart()

        # 设置图表标题
        chart.title = config['title']

        # 获取数据范围
        data_range = config['data_range']
        data = Reference(self.sheet, range_string=data_range)

        # 添加数据到图表
        chart.add_data(data, titles_from_data=True)

        # 设置图表位置
        self.sheet.add_chart(chart, config['position'])

        return chart


if __name__ == "__main__":
    # 创建数据写入器实例
    writer = ExcelDataWriter(r'D:\Python\config.json')

    # 准备要写入的数据（由Python代码指定）
    data_to_write = {
        "measure_datas": [
            [1, "样品1", 1, 1, 1, 1, 1, 1, 1, 1],
            [2, "样品2", 2, 2, 2, 2, 2, 2, 2, 2],
            [3, "样品3", 3, 3, 3, 3, 3, 3, 3, 3],
            [4, "样品4", 4, 4, 4, 4, 4, 4, 4, 4],
            [5, "样品5", 5, 5, 5, 5, 5, 5, 5, 5],
            [6, "样品6", 6, 6, 6, 6, 6, 6, 6, 6],
            [7, "样品7", 7, 7, 7, 7, 7, 7, 7, 7],
            [8, "样品8", 8, 8, 8, 8, 8, 8, 8, 8],
            [9, "样品9", 9, 9, 9, 9, 9, 9, 9, 9],
            [10, "样品10", 10, 10, 10, 10, 10, 10, 10, 10]
        ],
        "report_title": "水质总氮分析原始记录表",
        "sampleType":"标准样品",
        "measureName":"定量测定",
        "measureDate":"2025/6/5",
        "measureMethod":"水质定量测定",
        "deviceType":"紫外仪器",
        "deviceModel":"T600",
        "SN":"TEST001002"
    }

    # 写入数据到Excel
    try:
        output_path = writer.write_data(data_to_write)
        print(f"报告已成功生成: {os.path.abspath(output_path)}")
    except Exception as e:
        print(f"生成报告时出错: {str(e)}")
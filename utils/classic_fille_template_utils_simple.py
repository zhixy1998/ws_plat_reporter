import os
import re
import base64
import importlib
import urllib.parse
from decimal import Decimal
from io import BytesIO
from typing import List, Dict
from dotenv import load_dotenv

import requests
import matplotlib
matplotlib.use('Agg')  # 使用非交互式后端
import matplotlib.pyplot as plt
from docx.shared import Cm
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
from docxtpl import InlineImage, DocxTemplate

from config import config
from exceptions.error import ErrorCode
from constants.template_constant import MeasureType
from exceptions.command_exception import APIException
from app.template_doc.model.template_bookmark import TemplateBookmark
from utils.table_data_processor import TableDataProcessor

common_data_mapping = {
    # 光谱
    MeasureType.spectral_scanning.decs: {
        '仪器型号': 'instrumentModel',
        '仪器序号': 'instrumentSerialNumber',
        '光谱带宽': 'spectrumBandwidth',
        '扫描范围': 'scanRange',
        '光度模式': 'luminosityMode',
        '增益': 'gain',
        '扫描间隔': 'timeInterval',
        '扫描速度': 'scanSpeed',
        '能量灯': 'energyLight',
        '数据文件': 'taskName',
        '分析时间': 'detectionEndTime',
        '方法名称': 'methodName',
        '检测项目': 'project',
        '备注': 'remark',
        '光谱扫描图片': 'spectrumScanImage'
    },
    # 时间
    MeasureType.time_scanning.decs: {
        '仪器型号': 'instrumentModel',
        '仪器序号': 'instrumentSerialNumber',
        '光谱带宽': 'spectrumBandwidth',
        '光度模式': 'luminosityMode',
        '时间单位': 'timeUnit',
        '扫描时间': 'scanTime',
        '时间间隔': 'timeInterval',
        '扫描速度': 'scanSpeed',
        '采样数': 'totalNumber',
        '测量波长': 'instrumentWavelength',
        '数据文件': 'taskName',
        '分析时间': 'detectionEndTime',
        '方法名称': 'methodName',
        '检测项目': 'project',
        '备注': 'remark',
        '时间扫描图片': 'timeScanImage'
    },
    # 定量测定
    MeasureType.quantitative_determination.decs: {
        '切换样品池' : 'autoChangeSamplePool',
        '零点插入': 'insertZeroPoint', 
        '测量波长': 'instrumentWavelength',
        '强制过零点': 'forceZeroPoint',
        '数据文件': 'taskName',
        '分析时间': 'detectionEndTime',
        '波长模式': 'luminosityMode',
        '曲线方程': 'equationType',
        '方程次数': 'curveType',
        '公式': 'curveFormula',
        '方法名称': 'methodName',
        # 'k0': '',
        # 'k1': '',
        # 'k2': '',
        # 'k3': '',
        'r2': 'r2',
        'r': 'r',
        '重复测量': 'repetitionPattern',
        'k': 'curveParams',
        '标准浓度': 'standardConcentration',
    },
    # 光度测定
    MeasureType.photometric_measurement.decs: {
        '仪器型号': 'instrumentModel',
        '仪器序号': 'instrumentSerialNumber',
        '光谱带宽': 'spectrumBandwidth',
        '数据文件': 'taskName',
        '分析时间': 'detectionEndTime',
        '方法名称': 'methodName',
        '检测项目': 'project',
        '备注': 'remark',
    },
}

load_dotenv(override=True)

class ClassicFillDataUtils():
    def __init__(self, name, template_id, measure_type):
        self.name = name
        self.sample_id = None
        private_mod = None
        self.template_id = template_id
        self.common_val = None   # 代表通用数据接口返回的数据
        self.common_key = None   # 代表通用数据的描述
        self.private_key = None  # 代表私有数据的描述
        self.python_jinja_mapping = {}
        self.table_contexts = {}
        self.end_point_header_and_data = None
        self.measure_type = measure_type
        self.single_sample = False

    async def fill_data(self, doc_stream, task_id, sample_id=None, serial_number=None, image_base64=None, analysis_id=None, all_display=0, is_repeat_mode=0, digit=None):
        common_val = self.get_common_data_by_endpoint(task_id, analysis_id)
        if analysis_id and len(analysis_id.split(',')) == 1:
            self.single_sample = True

        end_point_header_and_data = self.get_table_head_data_from_endpoint(task_id, analysis_id, all_display, digit)
        self.end_point_header_and_data = end_point_header_and_data

        tpl = DocxTemplate(doc_stream)
        flag, contexts = await self.get_context(tpl, image_base64)
        if not flag:
            return None
        tpl.render(context=contexts)
        output_stream = BytesIO()
        tpl.save(output_stream)
        output_stream.seek(0)  # 很重要：回到开头，供后续读取

        return output_stream

    async def get_context(self, tpl, image_base64):
        contexts = {}
        # print(self.end_point_header_and_data)
        if self.measure_type is None:
            return False, {}
        # 光谱扫描
        if self.measure_type == MeasureType.spectral_scanning.decs:
            contexts = await self.get_spectral_scanning_context(tpl, image_base64, contexts)
        # 时间扫描
        if self.measure_type == MeasureType.time_scanning.decs:
            contexts = await self.get_time_scanning_context(tpl, image_base64, contexts)
        # 定量
        if self.measure_type  == MeasureType.quantitative_determination.decs:
            contexts = await self.get_quantitative_determination_context(tpl, contexts)
        # 光度测量
        if self.measure_type  == MeasureType.photometric_measurement.decs:
            contexts = await self.photometric_measurement_context(tpl, contexts)
        return True, contexts
    
    async def get_spectral_scanning_context(self, tpl, image_base64, contexts):
        spectral_scanning_mapping = common_data_mapping.get(self.measure_type)
        for jinja_val, common_val_key in spectral_scanning_mapping.items():
            if jinja_val == '光谱扫描图片':
                contexts[jinja_val] = await self.decode_base64_image(tpl, image_base64)
            elif jinja_val == '扫描范围':
                scan_range = self.common_val.get('startWaveLength', '')  + '至' + self.common_val.get('endWaveLength', '')
                contexts[jinja_val] = scan_range
            else:
                contexts[jinja_val] = self.common_val.get(common_val_key) if self.common_val.get(common_val_key) else ''
        table_data = self.handle_spectral_scanning_table(self.end_point_header_and_data)
        # 兼容旧模板（仍可用 Jinja 循环渲染）
        contexts['table_data'] = table_data
        # 新方式：预先用 python-docx 生成表格，再通过 docxtpl subdoc 插入（只改光谱）
        try:
            contexts['spectral_table_subdoc'] = self._build_table_subdoc(tpl, table_data)
        except Exception as e:
            print(f"生成光谱表格subdoc失败: {e}")
            contexts['spectral_table_subdoc'] = ''
        return contexts

    def _build_table_subdoc(self, tpl: DocxTemplate, table_data: dict):
        """用 python-docx 在 subdoc 中构造表格，供 docxtpl 插入。"""
        subdoc = tpl.new_subdoc()
        headers = (table_data or {}).get('header') or (table_data or {}).get('headers') or []
        row_data = (table_data or {}).get('row_data') or []

        # 无数据时给一个空段落，避免模板渲染出错
        if not headers:
            subdoc.add_paragraph('')
            return subdoc

        table = subdoc.add_table(rows=1, cols=len(headers))
        table.style = 'Table Grid'
        table.alignment = WD_TABLE_ALIGNMENT.CENTER

        # 表头
        hdr_cells = table.rows[0].cells
        for i, h in enumerate(headers):
            hdr_cells[i].text = '' if h is None else str(h)
            hdr_cells[i].vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            if hdr_cells[i].paragraphs:
                hdr_cells[i].paragraphs[0].alignment = WD_PARAGRAPH_ALIGNMENT.CENTER

        # 数据行
        for row in row_data:
            cells = table.add_row().cells
            # row 可能长度不齐，做 padding
            padded = list(row) + [''] * (len(headers) - len(row))
            for i in range(len(headers)):
                v = padded[i]
                cells[i].text = '' if v is None else str(v)
                cells[i].vertical_alignment = WD_ALIGN_VERTICAL.CENTER
                if cells[i].paragraphs:
                    cells[i].paragraphs[0].alignment = WD_PARAGRAPH_ALIGNMENT.CENTER

        return subdoc
    
    async def get_time_scanning_context(self, tpl, image_base64, contexts):
        time_scanning_mapping = common_data_mapping.get(self.measure_type)
        for jinja_val, common_val_key in time_scanning_mapping.items():
            if jinja_val != '时间扫描图片':
                contexts[jinja_val] = self.common_val.get(common_val_key) if self.common_val.get(common_val_key) else ''
            else:
                contexts[jinja_val] = await self.decode_base64_image(tpl, image_base64)
        table_data = self.handle_time_scanning_table(self.end_point_header_and_data)
        contexts['table_data'] = table_data
        try:
            contexts['time_table_subdoc'] = self._build_table_subdoc(tpl, table_data)
        except Exception as e:
            print(f"生成时间表格subdoc失败: {e}")
            contexts['time_table_subdoc'] = ''
        return contexts
    
    async def get_quantitative_determination_context(self, tpl, contexts):
        # 定量测定
        # 普通值
        quantitative_determination = common_data_mapping.get(self.measure_type)
        if self.common_val:
            for jinja_val, common_val_key in quantitative_determination.items():
                    contexts[jinja_val] = self.common_val.get(common_val_key) if self.common_val.get(common_val_key) else ''
            # 处理图片
            curve_info = self.end_point_header_and_data.get('curveInfo')
            if curve_info:
                image_data_list = curve_info.get('dataList') or []
                image_stand_point_list = curve_info.get('standPoints') or []
                image_unknown_point_list = curve_info.get('unknowPoints') or []
                if image_data_list:
                    quantitative_image = await self.generate_quantitative_chart(
                        image_data_list, 
                        image_stand_point_list, 
                        image_unknown_point_list,
                        tpl
                    )
                    contexts['定量分析图片'] = quantitative_image if quantitative_image else ''
                else:
                    contexts['定量分析图片'] = ''
            else:
                contexts['定量分析图片'] = ''
            # k
            k_str = self.common_val.get('curveParams')
            if k_str:
                k_parts = (k_str.split(',') + [None] * 5)[:5]
                
                for i, value in enumerate(k_parts):
                    if value:
                        value = str(Decimal(value))
                        contexts[f'k{i}'] = f'k{i}: '
                        contexts[f'k{i}_v'] = value
            k_values = []
            if contexts.get('k0'):  # k0 非空
                k_values.append({'label': contexts['k0'], 'value': contexts['k0_v']})
            if contexts.get('k1'):
                k_values.append({'label': contexts['k1'], 'value': contexts['k1_v']})
            if contexts.get('k2'):
                k_values.append({'label': contexts['k2'], 'value': contexts['k2_v']})
            if contexts.get('k3'):
                k_values.append({'label': contexts['k3'], 'value': contexts['k3_v']})
            if contexts.get('k4'):
                k_values.append({'label': contexts['k4'], 'value': contexts['k4_v']})
            contexts['k_values'] = k_values
        if self.end_point_header_and_data:
            # 标准样品表格
            standard_header_list = self.end_point_header_and_data.get('standHeadList')
            standard_data_list = self.end_point_header_and_data.get('standDataList')
            knows_header, knows_data_list = self.get_quantitative_determination_standard_table(standard_header_list, standard_data_list)
            knows_table_data = {'headers': knows_header, 'row_data': knows_data_list}
            contexts['knows_table_data'] = knows_table_data

            # abs_identity = None
            # same_number_identity = 'sampleNumber'
            # for header in standard_header_list:
            #     if header.get('locate') == 'measure' and 'Abs' in header.get('name') and '-' in header.get('identity'):
            #         abs_identity = header.get('identity')

            # contexts['波长'] = str(abs_identity.split('-')[0]) if abs_identity and '-' in abs_identity else ''

            # 未知样品表格
            unknown_data_list = self.end_point_header_and_data.get('unknowDataList')
            unknown_header_list = self.end_point_header_and_data.get('unknowHeadList')
            unknown_header, unknown_data_list = self.get_quantitative_determination_unknown_table(unknown_header_list, unknown_data_list)
            unknown_table_data = {'headers': unknown_header, 'row_data': unknown_data_list}
            contexts['unknown_table_data'] = unknown_table_data
            try:
                contexts['knows_table_subdoc'] = self._build_table_subdoc(tpl, knows_table_data)
                contexts['unknown_table_subdoc'] = self._build_table_subdoc(tpl, unknown_table_data)
            except Exception as e:
                print(f"生成定量表格subdoc失败: {e}")
                contexts['knows_table_subdoc'] = ''
                contexts['unknown_table_subdoc'] = ''
        else:
            contexts['knows_table_data'] = {'headers': [], 'row_data': []}
            contexts['unknown_table_data'] = {'headers': [], 'row_data': []}
            try:
                contexts['knows_table_subdoc'] = self._build_table_subdoc(tpl, contexts['knows_table_data'])
                contexts['unknown_table_subdoc'] = self._build_table_subdoc(tpl, contexts['unknown_table_data'])
            except Exception as e:
                print(f"生成定量表格subdoc失败: {e}")
                contexts['knows_table_subdoc'] = ''
                contexts['unknown_table_subdoc'] = ''
        return contexts
    
    async def photometric_measurement_context(self, tpl, contexts):
        # 光度测量
        if self.common_val:
            photometric_measurement = common_data_mapping.get(self.measure_type)
            for jinja_val, common_val_key in photometric_measurement.items():
                contexts[jinja_val] = self.common_val.get(common_val_key) if self.common_val.get(common_val_key) else ''
        if self.end_point_header_and_data:
            header_list = self.end_point_header_and_data.get('headList')
            data_list = self.end_point_header_and_data.get('dataList')
            headers, row_data = self.photometric_measurement_table_data(header_list, data_list)
            table_data = {'headers': headers, 'row_data': row_data}
            contexts['table_data'] = table_data
            try:
                contexts['photometric_table_subdoc'] = self._build_table_subdoc(tpl, table_data)
            except Exception as e:
                print(f"生成光度表格subdoc失败: {e}")
                contexts['photometric_table_subdoc'] = ''
        else:
            contexts['table_data'] = {'headers': [], 'row_data': []}
            try:
                contexts['photometric_table_subdoc'] = self._build_table_subdoc(tpl, contexts['table_data'])
            except Exception as e:
                print(f"生成光度表格subdoc失败: {e}")
                contexts['photometric_table_subdoc'] = ''
        return contexts
        

    async def generate_quantitative_chart(self, data_points, stand_points, unknown_points, tpl):
        """
        生成定量分析图表
        
        Args:
            data_points: 数据点列表 [{'x': 123, 'y': 456}, ...]
            stand_points: 标准点列表 [{'x': 123, 'y': 456}, ...]
            unknown_points: 未知点列表 [{'x': 123, 'y': 456}, ...]
            tpl: DocxTemplate 对象
            
        Returns:
            InlineImage 对象或 None
        """
        # try:
        # 过滤掉 x 或 y 为 None 的点
        def filter_valid_points(points):
            """过滤掉 x 或 y 为 None 的点"""
            return [point for point in points if point.get('x') is not None and point.get('y') is not None]
        
        data_points = filter_valid_points(data_points)
        stand_points = filter_valid_points(stand_points) if stand_points else []
        unknown_points = filter_valid_points(unknown_points) if unknown_points else []
        
        # 调试信息
        # print(f"DEBUG: 过滤后数据点数量: {len(data_points)}")
        # print(f"DEBUG: 过滤后标准点数量: {len(stand_points)}")
        # print(f"DEBUG: 过滤后未知点数量: {len(unknown_points)}")
        
        # if data_points:
            # print(f"DEBUG: 数据点范围 - X: {min(p['x'] for p in data_points)} ~ {max(p['x'] for p in data_points)}")
            # print(f"DEBUG: 数据点范围 - Y: {min(p['y'] for p in data_points)} ~ {max(p['y'] for p in data_points)}")
        
        # if stand_points:
        #     print(f"DEBUG: 标准点示例: {stand_points[:3]}")
        
        # if unknown_points:
        #     print(f"DEBUG: 未知点示例: {unknown_points[:3]}")
        
        if not data_points:
            return None
                
        # 提取数据点的 x, y 坐标
        x_data = [point.get('x', 0) for point in data_points]
        y_data = [point.get('y', 0) for point in data_points]
            
        # 创建图形
        plt.figure(figsize=(10, 6))
        plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']  # 支持中文
        plt.rcParams['axes.unicode_minus'] = False
            
        # 绘制主要数据线（只用线条，不用散点，避免视觉重叠）
        plt.plot(x_data, y_data, 'k-', linewidth=0.5, label='数据曲线')
            
        # 标记标准点（蓝色）
        if stand_points:
            # 转换为数字类型
            stand_x = [float(point.get('x', 0)) for point in stand_points]
            stand_y = [float(point.get('y', 0)) for point in stand_points]
            plt.scatter(stand_x, stand_y, c='blue', s=120, marker='o', 
                        label=f'标准点 ({len(stand_points)}个)', zorder=10, edgecolors='darkblue', linewidth=2)
            
        # 标记未知点（红色）
        if unknown_points:
            # 转换为数字类型
            unknown_x = [float(point.get('x', 0)) for point in unknown_points]
            unknown_y = [float(point.get('y', 0)) for point in unknown_points]
            plt.scatter(unknown_x, unknown_y, c='red', s=120, marker='s', 
                        label=f'未知点 ({len(unknown_points)}个)', zorder=10, edgecolors='darkred', linewidth=2)
            
        # 设置图表样式
        plt.xlabel('浓度', fontsize=12)
        plt.ylabel('吸光度', fontsize=12)
        plt.title('定量分析标准曲线', fontsize=14, fontweight='bold')
        plt.grid(True, alpha=0.3)
        plt.legend(loc='best', fontsize=10)
            
        # 设置坐标轴范围 - 模拟 ECharts 的自动范围计算
        # 必须同时考虑数据点、标准点和未知点的范围！
        if x_data and y_data:
            all_x = x_data.copy()
            all_y = y_data.copy()
            
            # 添加标准点的坐标到范围计算中
            if stand_points:
                all_x.extend([float(point.get('x', 0)) for point in stand_points])
                all_y.extend([float(point.get('y', 0)) for point in stand_points])
            
            # 添加未知点的坐标到范围计算中
            if unknown_points:
                all_x.extend([float(point.get('x', 0)) for point in unknown_points])
                all_y.extend([float(point.get('y', 0)) for point in unknown_points])
            
            x_min, x_max = min(all_x), max(all_x)
            y_min, y_max = min(all_y), max(all_y)
            
            # 模拟 ECharts 的自动范围：两端各留约 10% 边距
            x_range = x_max - x_min if x_max != x_min else max(abs(x_max), 1)
            y_range = y_max - y_min if y_max != y_min else max(abs(y_max), 1)
            
            # ECharts 风格：无论最小值是多少，都留 10% 边距（可以是负值）
            margin_x = x_range * 0.1
            margin_y = y_range * 0.1
            
            x_axis_min = x_min - margin_x
            x_axis_max = x_max + margin_x
            y_axis_min = y_min - margin_y
            y_axis_max = y_max + margin_y
            
            plt.xlim(x_axis_min, x_axis_max)
            plt.ylim(y_axis_min, y_axis_max)
            
        # 保存图片到内存
        img_buffer = BytesIO()
        plt.savefig(img_buffer, format='png', dpi=300, bbox_inches='tight', 
                    facecolor='white', edgecolor='none')
        plt.close()  # 关闭图形以释放内存
            
        img_buffer.seek(0)
        cm = self.get_cm() 
        # 转换为 InlineImage
        return InlineImage(tpl, img_buffer, width=Cm(cm))
            
        # except Exception as e:
        #     print(f"生成定量图表失败: {e}")
        #     return None

    def get_common_data_by_endpoint(self, task_id, analysis_id):
        template_common_url = config.classic_template_common_var_url + '?taskId=' + urllib.parse.quote(str(task_id), safe='') + '&analysisId=' + urllib.parse.quote(str(analysis_id), safe='')
        # print(f"DEBUG: 请求URL: {template_common_url}")
        # print(f"DEBUG: 原始task_id: {repr(task_id)}")
        try:
            res = requests.get(template_common_url, timeout=5, verify=False)
            if res.status_code == 200:
                try:
                    res_json = res.json()
                    if res_json.get('code') == 200:
                        common_val = res_json.get('data')
                    else:
                        common_val = {}
                except Exception as e:
                    print(e)
                    common_val = {}
            else:
                print("请求通用数据失败, url:", template_common_url)
                common_val = {}
        except requests.exceptions.Timeout:
            print(f"请求超时，跳过: {template_common_url}")
            common_val = {}
        except Exception as e:
            print(f"请求异常，跳过: {e}")
            common_val = {}
        
        self.common_val = common_val
        return common_val
        

    # 处理children children代表这个数据获取的描述方法。
    async def handle_children(self, private_k, children, value_list, connect_str=''):
        final_val_list = []
        for child in children:
            get_desc = self.common_key.get(child)
            if get_desc and get_desc.get('position'):
                val = await self.get_common_val_by_private_position(get_desc.get('position'))
                if val:
                    final_val_list.append(val)
        if final_val_list:
            self.python_jinja_mapping[private_k] = connect_str.join(final_val_list)
            value_list.append(connect_str.join(final_val_list))
        
    def fill_template_by_jinja(self, tpl):
        """
        """
        # 合并context
        final_context = self.python_jinja_mapping.copy()
        # if additional_context:
        #     final_context.update(self.table_contexts)
            # print("Merged context:", final_context)
        # 处理python jinja语法变量
        tpl.render(context=final_context)
        # 写入内存流，返回
        output_stream = BytesIO()
        tpl.save(output_stream)
        output_stream.seek(0)  # 很重要：回到开头，供后续读取
        
        # 移除表格中的空行
        output_stream = self.remove_empty_table_rows(output_stream)
        
        return output_stream
    
    def is_base64(self, s: str) -> bool:
        if not isinstance(s, str):
            return False
        try:
            # base64 字符长度必须是4的倍数
            if len(s) % 4 != 0:
                return False
            # 符合 base64 编码字符集
            if not re.match(r'^[A-Za-z0-9+/=\s]+$', s):
                return False
            # 能否成功 decode
            base64.b64decode(s, validate=True)
            return True
        except Exception:
            return False
    
    async def decode_base64_image(self, tpl, val):
        try:
            # 移除可能的data URI前缀
            if val.startswith('data:image'):
                val = val.split(',', 1)[1]
            
            # 移除所有空白字符
            val = val.strip().replace('\n', '').replace('\r', '').replace(' ', '')
        
            # 检查并添加padding
            padding = len(val) % 4
            if padding:
                val += '=' * (4 - padding)
            
            # 验证base64字符集
            import re
            if not re.match(r'^[A-Za-z0-9+/]*={0,2}$', val):
                print("base64字符串包含无效字符")
                return None
            
            image_data = base64.b64decode(val)
            image_stream = BytesIO(image_data)
            cm = self.get_cm()
            return InlineImage(tpl, image_stream, width=Cm(cm))
        except Exception as e:
            print(f"图片解码失败: {e}")
            print(f"base64字符串长度: {len(val) if val else 0}")
            return None

    def filter_table_header(self, private_header, table_header_data_mapping):
        private_header = self.handle_table_header(private_header)
        new_table_header_data_mapping = {}
        for header in private_header:
            if header in table_header_data_mapping:
                new_table_header_data_mapping[header] = table_header_data_mapping[header]
        return new_table_header_data_mapping
    
    def handle_table_header(self, headers):
        """
        数据库存储的表头可能是嵌套的，需要处理
        两层嵌套，就用 '-' 把同一列连接起来。
        """
        if len(headers) == 1:
            return headers[0]
        else:
            return ["-".join(map(str, group)) for group in zip(*headers)]
    

    async def get_all_child_bookmarks(self, parent_id):
        """
        递归获取所有子标签，组成一维列表
        
        Args:
            parent_id: 父标签的ID
            
        Returns:
            list: 所有子标签的一维列表
        """
        all_children = []
        
        # 获取直接子标签
        direct_children = await TemplateBookmark.filter(
            parent_id=parent_id, 
            template_doc_id=self.template_id, 
            is_del=0
        ).all()
        
        for child in direct_children:
            # 添加当前子标签到列表
            all_children.append(child)
            
            # 递归获取这个子标签的所有子标签
            grandchildren = await self.get_all_child_bookmarks(child.id)
            all_children.extend(grandchildren)
        
        return all_children
    
    def fill_template_jinja_custom_info(self,doc_stream, custom_info=None, additional_context=None):
        """
        doc_stream    模板文件流
        custom_info   自定义标签信息
        """
        module_name = "template_structure." + self.name
        try:
            private_mod = importlib.import_module(module_name)
        except Exception as e:
            private_mod = None
        if private_mod and hasattr(private_mod, 'custom_bookmark'):
            custom_bookmark=private_mod.custom_bookmark
        else:
            custom_bookmark = {'note': '备注', 'project_name': '项目名称'}

        try:
            from docxtpl import DocxTemplate
            from io import BytesIO

            # 创建DocxTemplate对象
            tpl = DocxTemplate(doc_stream)

            # 获取模板中所有未声明的变量
            undeclared_vars = tpl.get_undeclared_template_variables()

            blank_context = {}
            for var in undeclared_vars:
                blank_context[var] = ""
            if custom_info:
                for i in undeclared_vars:
                    if i in custom_bookmark['project_name']:
                        blank_context[i] = custom_info.get('project_name')
                    if i in custom_bookmark['note']:
                        blank_context[i] = custom_info.get('note')

            # 为所有未声明的变量创建空字符串映射

            # 如果没有未声明的变量，直接返回原文档
            if not blank_context:
                doc_stream.seek(0)
                return doc_stream
            if additional_context:
                blank_context.update(additional_context)
            # 使用空字符串上下文渲染模板
            tpl.render(blank_context)

            # 保存到新的BytesIO流
            output_stream = BytesIO()
            tpl.save(output_stream)
            output_stream.seek(0)

            return output_stream

        except Exception as e:
            # 出错时返回原文档
            doc_stream.seek(0)
            return doc_stream
    
    async def get_quantitative_determination_photometric_measurement_from_endpoint(self, doc_stream, task_id, origin_header_real_header_mapping={}, tpl_context={}):
        table_data_processor = TableDataProcessor(self.name)
        table_fields = table_data_processor.get_table_fields()
        if table_fields:
            if not hasattr(table_data_processor.handler_instance, 'HEADER_M_MAPPING'):
                raise APIException(error=ErrorCode.TABLE_DATA_HANDLER_NOT_FOUND)
            HEADER_M_MAPPING = table_data_processor.handler_instance.HEADER_M_MAPPING  # 每个私有文件都要声明的
            TABLE_NAME_MAP_REVERSE = table_data_processor.handler_instance.TABLE_NAME_MAP_REVERSE
            # get_header_and_data_class_instance = GetHeaderAndData(task_id)
            # await get_header_and_data_class_instance._get_all_headers()
            self.HEADER_M_MAPPING = HEADER_M_MAPPING
            # total_handler_list = table_data_processor.list_available_handlers()
            # for handler in total_handler_list:
            #     handler()
            standard = table_data_processor.handler_instance.standard
            if not standard:
                standard = []
            origin_header_data_mapping = {}
            last_unknown_origin_header = None
            print('TABLE_NAME_MAP_REVERSE', TABLE_NAME_MAP_REVERSE)
            for table_name, origin_header_list in TABLE_NAME_MAP_REVERSE.items():
                table_origin_header_data_mapping = {}  # 每个表格单独的数据映射
                for origin_header in origin_header_list:
                    m = HEADER_M_MAPPING.get(origin_header)
                    if origin_header in standard:
                        # 标准样处理
                        handler = getattr(table_data_processor.handler_instance, 'handle_' + origin_header)
                        real_header, sample_data = handler(self.end_point_header_and_data, m)
                        for index, data in enumerate(sample_data):
                            tpl_context[origin_header + '_' + str(index)] = data
                            origin_header_real_header_mapping[origin_header] = real_header if real_header else '' # old_header 标签名字
                    else:
                        # 未知样处理
                        real_header, identity = self.get_unknown_sample_header(m)
                        origin_header_real_header_mapping[origin_header] = real_header if real_header else ''
                        if identity:
                            data = self.get_unknown_sample_data(identity)
                            table_origin_header_data_mapping[origin_header] = data
                
                # 为每个表格生成行数据
                if table_origin_header_data_mapping:
                    rows = self.columns_to_rows(table_origin_header_data_mapping)
                    rows_name = table_name + '_rows'
                    tpl_context[rows_name] = rows
        return origin_header_real_header_mapping, tpl_context
    
    def get_table_head_data_from_endpoint(self, task_id, analysis_id, all_display=0, digit=None):
        if all_display:
            all_display=True
        else:
            all_display=False
            
        if digit is not None:
            template_common_url = config.classic_template_table_head_data_url + '?taskId=' + urllib.parse.quote(str(task_id), safe='') + '&analysisId=' + urllib.parse.quote(str(analysis_id), safe='') + '&allDisplay=' + urllib.parse.quote(str(all_display), safe='') + '&digit=' + urllib.parse.quote(str(digit), safe='')
        else:
            template_common_url = config.classic_template_table_head_data_url + '?taskId=' + urllib.parse.quote(str(task_id), safe='') + '&analysisId=' + urllib.parse.quote(str(analysis_id), safe='') + '&allDisplay=' + urllib.parse.quote(str(all_display), safe='')
        # print(f"DEBUG: 请求表头数据URL: {template_common_url}")
        # print(f"DEBUG: 原始task_id: {repr(task_id)}, sample_id: {repr(sample_id)}")
        try:
            res = requests.get(template_common_url, timeout=10, verify=False)
            if res.status_code == 200:
                try:
                    res_json = res.json()
                    if res_json.get('code') == 200:
                        table_head_data = res_json.get('data')
                    else:
                        table_head_data = {}
                except Exception as e:
                    print(e)
                    table_head_data = {}
            else:
                print("请求表头数据失败, url:", template_common_url)
                table_head_data = {}
        except requests.exceptions.Timeout:
            print(f"请求超时，跳过: {template_common_url}")
            table_head_data = {}
        except Exception as e:
            print(f"请求异常，跳过: {e}")
            table_head_data = {}
        
        return table_head_data
    
    def get_unknown_sample_header(self, m):
        """
        未知样品:
            头: 
                1 去mapRelation list[dict] 里面取  paramIdentity=m 然后取headIdentity = identity 
                    真实表头 paramName
                    if paramName is None:
                        拿  identity  去 unknowHeadList 匹配 identity 取 printTitle 就是真实的表头
                2 去unknowHeadList 里面找
                    identity = m    printTitle就是真实的表头
            数据:
                unknowDataList 
                根据identity取数据
        """
        identity = None
        real_header = None
        if self.end_point_header_and_data:
            map_relation = self.end_point_header_and_data.get('mapRelation')
            for one_map_relation in map_relation:
                if one_map_relation.get('paramIdentity') == m:
                    identity = one_map_relation.get('headIdentity')
                    real_header = one_map_relation.get('paramName')
                    if not real_header:
                        unknown_header_list = self.end_point_header_and_data.get('unknowHeadList')
                        for one_unknown_header in unknown_header_list:
                            if one_unknown_header.get('identity') == identity:
                                real_header = one_unknown_header.get('printTitle')
        if identity is None and real_header is None:
            unknown_header_list = self.end_point_header_and_data.get('unknowHeadList')
            for one_unknown_header in unknown_header_list:
                if one_unknown_header.get('identity') == m:
                    real_header = one_unknown_header.get('printTitle')
                    identity = m
        return real_header, identity


    def get_unknown_sample_data(self, identity: str) -> List[str]:
        """
        未知样品:
            头: 
                1 去mapRelation list[dict] 里面取  paramIdentity=m 然后取headIdentity = identity 
                    真实表头 paramName
                    if paramName is None:
                        拿  identity  去 unknowHeadList 匹配 identity 取 printTitle 就是真实的表头
                2 去unknowHeadList 里面找
                    identity = m    printTitle就是真实的表头
            数据:
                unknowDataList 
                根据identity取数据
        """
        data = []
        for one_unknown_data in self.end_point_header_and_data.get('unknowDataList'):
            if one_unknown_data.get(identity) or one_unknown_data.get(identity) == '':
                data.append(one_unknown_data.get(identity))
        return data
    
    @staticmethod
    def columns_to_rows(data: Dict[str, List]) -> List[Dict]:
        """
        将 {'a':[1,2,3], 'b':[4,5,6], 'c':[7,8,9]}
        转成 [{'a':1,'b':4,'c':7}, {'a':2,'b':5,'c':8}, {'a':3,'b':6,'c':9}]
        """
        if not data:
            return []
        keys = list(data.keys())
        columns = [data[k] for k in keys]
        return [dict(zip(keys, row)) for row in zip(*columns)]
    
    def get_cm(self):
        name_cm_mapping = {
            '定量_曲线在左上': 7,
            '光谱_曲线在右上': 7,
            '光谱_曲线在左上': 7,
            '光度': 7,
            '时间': 7
        }
        return name_cm_mapping.get(self.name, 16)
    
    def handle_spectral_scanning_table(self, end_point_header_and_data):
        head_list = end_point_header_and_data.get('headList')
        data_list = end_point_header_and_data.get('dataList')
        if self.single_sample:
            identity_list = []
            header = []
            row_data = []
            if head_list:
                for head_mapping in head_list:
                    header.append(head_mapping.get('name'))
                    identity_list.append(head_mapping.get('identity'))
                for data in data_list:
                    row = []
                    for index, identity in enumerate(identity_list):
                        if data.get(identity):
                            row.append(data.get(identity))
                        else:
                            row.append('')
                    row_data.append(row)
        else:
            sample_num = 0 # 样品数量
            sample_name = []
            row_data = []
            if head_list:
                for i in head_list:
                    if i.get('identity') == 'sampleNumber':
                        sample_num += 1
                        sample_name.append(i.get('name'))
                header = [h.get("name") for h in head_list]
                # header = ['编号', '波长']
                # for name in sample_name:
                #     header.append(name)
                #     header.append('峰谷')
                for wave_length_data_mapping in data_list:
                    row = []
                    for wave_length, data in wave_length_data_mapping.items():
                        row.append(data.get('id'))
                        row.append(wave_length)
                        for index, sample_num in enumerate(data.get('sampleNumber')):
                            row.append(sample_num)
                            row.append(data.get('peakValley')[index])
                    row_data.append(row)
            else:
                row_data = []
        # if row_data:
        #     data_row_1 = row_data[0]
        #     for index, data in enumerate(data_row_1):
        #         data_len = len(str(data))
        #         if index < len(header):
        #             head_len = len(header[index])
        #             if data_len > head_len:
        #                 len_dis = data_len - head_len
        #                 header[index] = header[index] + '\u00a0' * (len_dis + 1)

        return {'header': header, 'row_data': row_data}
    
    def handle_time_scanning_table(self, end_point_header_and_data):
        head_list = end_point_header_and_data.get('headList')
        data_list = end_point_header_and_data.get('dataList')
        if self.single_sample:
            identity_list = []
            header = []
            for head_mapping in head_list:
                header.append(head_mapping.get('name'))
                identity_list.append(head_mapping.get('identity'))
            row_data = []
            for data in data_list:
                row = []
                for index, identity in enumerate(identity_list):
                    if data.get(identity):
                        row.append(data.get(identity))
                    else:
                        row.append('')
                row_data.append(row)
        else:
            sample_num = 0 # 样品数量
            sample_name = []
            for i in head_list:
                if i.get('identity') == 'sampleNumber':
                    sample_num += 1
                    sample_name.append(i.get('name'))
            header = [h.get("name") for h in head_list]
            row_data = []
            # for name in sample_name:
            #     header.append(name)
            #     header.append('峰谷')
            for wave_length_data_mapping in data_list:
                row = []
                for time, data in wave_length_data_mapping.items():
                    row.append(data.get('id'))
                    row.append(time)
                    for index, sample_num in enumerate(data.get('sampleNumber')):
                        row.append(sample_num)
                        if data.get('peakValley')[index]:
                            row.append(data.get('peakValley')[index])
                        else:
                            row.append('')
                row_data.append(row)

        return {'header': header, 'row_data': row_data}
        

    def get_quantitative_determination_standard_table(self, standard_header_list, standard_data_list):
        name_identity_mapping = {header.get('name'): header.get('identity') for header in standard_header_list}
        headers = []
        for h in standard_header_list:
            if h.get('printTitle'):
                headers.append(h.get('printTitle'))
            else:
                headers.append(h.get('name'))
        row_data = []
        for data in standard_data_list:
            row = []
            for _, identity in name_identity_mapping.items():
                row_value = data.get(identity)
                if row_value:
                    row.append(row_value)
                else:
                    row.append('')
            row_data.append(row)
            if data.get('children', []):
                for children_data in data.get('children', []):
                    row = []
                    for _, identity in name_identity_mapping.items():
                        row_value = children_data.get(identity)
                        if row_value:
                            row.append(row_value)
                        else:
                            row.append('')
                    row_data.append(row)
        return headers, row_data
        # has_sum_abs = False
        # header_name = ['序号', '样品编号', '样品名称', '样品类型', '标准浓度', 'ΔAbs']
        # knows_data_list = []
        # header_identity_mapping = {}
        # for header in header_name:
        #     for header_data in standard_header_list:
        #         if header_data.get('name') == header:
        #             header_identity_mapping[header] = header_data.get('identity')
        #     if header not in header_identity_mapping:
        #         header_identity_mapping[header] = ''
        # for index, standard_data in enumerate(standard_data_list):
        #     row = []
        #     for inside_index, name in enumerate(header_name):
        #         if name == '序号':
        #             row.append(str(index + 1))
        #         elif name == 'ΔAbs':
        #             sum_abs = standard_data.get('sumAbs')
        #             if sum_abs is not None:
        #                 has_sum_abs = True
        #                 row.append(sum_abs)
        #             else:
        #                 row.append('')
        #         else:
        #             row.append(standard_data.get(header_identity_mapping.get(name)))
        #     knows_data_list.append(row)
        # if has_sum_abs is False:
        #     for index, name in enumerate(header_name):
        #         if name == 'ΔAbs':
        #             del_index = index
        #         else:
        #             header_name[index] = name
        #     header_name.pop(del_index)
        #     for row in knows_data_list:
        #         row.pop(del_index)
        # return header_name, knows_data_list
    
    def get_quantitative_determination_unknown_table(self, unknown_header_list, unknown_data_list):
        name_identity_mapping = {header.get('name'): header.get('identity') for header in unknown_header_list}
        headers = []
        for h in unknown_header_list:
            if h.get('printTitle'):
                headers.append(h.get('printTitle'))
            else:
                headers.append(h.get('name'))
        row_data = []
        for data in unknown_data_list:
            row = []
            for _, identity in name_identity_mapping.items():
                row_value = data.get(identity)
                if row_value:
                    row.append(row_value)
                else:
                    row.append('')
            row_data.append(row)
            if data.get('children', []):
                for children_data in data.get('children', []):
                    row = []
                    for _, identity in name_identity_mapping.items():
                        row_value = children_data.get(identity)
                        if row_value:
                            row.append(row_value)
                        else:
                            row.append('')
                    row_data.append(row)
        return headers, row_data
        # has_sum_abs = False
        # header_name = ['序号', '样品编号', '样品名称', '样品类型', 'Abs[wavelength]', 'Abs', '拟合浓度', '采样时间', 'ΔAbs']
        # return_unknown_data_list = []
        # header_identity_mapping = {}
        # for index, header in enumerate(header_name):
        #     for header_data in unknown_header_list:
        #         if header_data.get('name') == header:
        #             header_identity_mapping[header] = header_data.get('identity')
        #     if header not in header_identity_mapping:
        #         if header == 'Abs[wavelength]':
        #             for header_data in unknown_header_list:
        #                 if 'Abs[' in header_data.get('name'):
        #                     header_name[index] = header_data.get('name')
        #                     header_identity_mapping[header_data.get('name')] = header_data.get('identity')
        #                     break
        #         else:
        #             header_identity_mapping[header] = ''
        # for index, unknown_data in enumerate(unknown_data_list):
        #     row = []
        #     for inside_index, name in enumerate(header_name):
        #         if name == '序号':
        #             row.append(str(index + 1))
        #         elif name == 'ΔAbs':
        #             sum_abs = unknown_data.get('sumAbs')
        #             if sum_abs is not None:
        #                 has_sum_abs = True
        #                 row.append(sum_abs)
        #             else:
        #                 row.append('')
        #         else:
        #             row.append(unknown_data.get(header_identity_mapping.get(name), ''))
        #     return_unknown_data_list.append(row)
        # if has_sum_abs is False:
        #     for index, name in enumerate(header_name):
        #         if name == 'ΔAbs':
        #             del_index = index
        #         else:
        #             header_name[index] = name
        #     header_name.pop(del_index)
        #     for row in return_unknown_data_list:
        #         row.pop(del_index)
        # return header_name, return_unknown_data_list
    
    def photometric_measurement_table_data(self, header_list, data_list):
        name_identity_mapping = {header.get('name'): header.get('identity') for header in header_list}
        headers = []
        for h in header_list:
            if h.get('printTitle'):
                headers.append(h.get('printTitle'))
            else:
                headers.append(h.get('name'))
        row_data = []
        for data in data_list:
            row = []
            for _, identity in name_identity_mapping.items():
                row_value = data.get(identity)
                if row_value:
                    row.append(row_value)
                else:
                    row.append('')
            row_data.append(row)
            if data.get('children', []):
                for children_data in data.get('children', []):
                    row = []
                    for name in headers:
                        identity = name_identity_mapping.get(name)
                        if identity:
                            row_value = children_data.get(identity)
                            if row_value:
                                row.append(row_value)
                            else:
                                row.append('')
                    row_data.append(row)
        return headers, row_data
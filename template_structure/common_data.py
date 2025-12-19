title_mapping = { # 全部加t
    'project': '检测项目',
    'instrument_num': '仪器编号',
    'trh': '环境条件', # Temperature and Humidity
    'detection_time': '分析日期', 
    'storage_condition': '存放条件', # Storage Conditions
    'instrument_name': '仪器名称',
    'detection_basis': '检测依据',
    'sample_status': '样品状态',
    'standard_solution_number': '标准溶液及编号',
    'solution_concentration': '溶液浓度()',
    'regression_equation': '回归方程', # Regression equation
    'calculation_formula': '计算公式',
    'remark': '备注'
}



data = {

    "instrument_num": {"fill_type": 0, 'get_type': 0, 'position': ['instrumentSerialNumber']}, # 仪器编号
    "光度模式": {"fill_type": 0, 'get_type': 0, 'position': ['luminosityMode']},
    "光谱带宽": {"fill_type": 0, 'get_type': 0, 'position': ['spectrumBandwidth']},
    "光谱扫描图片": {"fill_type": 0, 'get_type': 0, 'position': ['spectrumScanImage']},
    "时间扫描图片": {"fill_type": 0, 'get_type': 0, 'position': ['timeScanImage']},
    "原始数据": {"fill_type": 0, 'get_type': 0, 'position': ['originalData']},
    "增益": {"fill_type": 0, 'get_type': 0, 'position': ['gain']},
    "扫描范围": {"fill_type": 0, 'get_type': 0, 'position': ['scanRange']},
    "扫描速度": {"fill_type": 0, 'get_type': 0, 'position': ['scanSpeed']},
    "扫描间隔": {"fill_type": 0, 'get_type': 0, 'position': ['scanInterval']},
    "数据类型": {"fill_type": 0, 'get_type': 0, 'position': ['dataType']},
    "方法信息": {"fill_type": 0, 'get_type': 0, 'position': ['methodName']},
    "project": {"fill_type": 0, 'get_type': 0, 'position': ['project']}, # 检测项目
    "项目": {"fill_type": 0, 'get_type': 0, 'position': ['project']},
    "注释": {"fill_type": 0, 'get_type': 0, 'position': ['remark']},
    "仪器波长": {"fill_type": 0, 'get_type': 0, 'position': ['instrumentWavelength']},
    "参考方法": {"fill_type": 0, 'get_type': 0, 'position': ['referenceMethod']},
    "参考标准": {"fill_type": 0, 'get_type': 0, 'position': ['referenceStandard']},
    "备注": {"fill_type": 0, 'get_type': 0, 'position': ['remark']},
    "收样名称": {"fill_type": 0, 'get_type': 0, 'position': ['sampleName']},
    "样品编号": {"fill_type": 0, 'get_type': 0, 'position': ['sampleNumber']},
    "检测开始时间": {"fill_type": 0, 'get_type': 0, 'position': ['detectionStartTime']},
    "检测结束时间": {"fill_type": 0, 'get_type': 0, 'position': ['detectionEndTime']},
    "检测者": {"fill_type": 0, 'get_type': 0, 'position': ['detector']},
    "检测人": {"fill_type": 0, 'get_type': 0, 'position': ['detector']},
    "能量灯": {"fill_type": 0, 'get_type': 0, 'position': ['energyLight']},
    "calculation_formula": {"fill_type": 0, 'get_type': 0, 'position': ['calculationFormula']},
    "阶梯矫正": {"fill_type": 0, 'get_type': 0, 'position': ['stairCorrection']},
    "阶梯校正": {"fill_type": 0, 'get_type': 0, 'position': ['stairCorrection']},
    "样品名称": {"fill_type": 0, 'get_type': 0, 'position': ['sampleName']},
    "方法名称": {"fill_type": 0, 'get_type': 0, 'position': ['methodName']},
    "操作步骤": {"fill_type": 0, 'get_type': 0, 'position': ['steps']},
    "instrument_name": {"fill_type": 0, 'get_type': 0, 'position': ['instrumentName']},
    "仪器型号": {"fill_type": 0, 'get_type': 0, 'position': ['instrumentModel']},
    "t": {"fill_type": 0, 'get_type': 0, 'position': ['ambientTemperature']}, # 温度
    "rh": {"fill_type": 0, 'get_type': 0, 'position': ['relativeHumidity']}, # 湿度
    "质量等级": {"fill_type": 0, 'get_type': 0, 'position': ['qualityLevel']},
    "比色皿光程": {"fill_type": 0, 'get_type': 0, 'position': ['colorPlateWavelength']},
    "式中": {"fill_type": 0, 'get_type': 0, 'position': ['formulaParams']},
    "收样日期": {"fill_type": 0, 'get_type': 0, 'position': ['samplingTime']},
    "sample_status": {"fill_type": 0, 'get_type': 0, 'position': ['sampleState']}, # □固态  □气态  □半固态  □液态
    "接样日期": {"fill_type": 0, 'get_type': 0, 'position': ['samplingTime']},
    "detection_time": {"fill_type": 0, 'get_type': 0, 'position': ['detectionEndTime']}, # 分析日期
    "仪器名称及型号": {"fill_type": 0, 'get_type': 0, 'children': ['instrument_name', '仪器型号'], 'connect_str': ' '},
    "分析方法及编号": {"fill_type": 0, 'get_type': 0, 'children': ['方法名称', '方法编号'], 'connect_str': ' '},
    'step': {"fill_type": 0, 'get_type': 0, 'position': ['steps']}, # 步骤
    'formula_params': {"fill_type": 0, 'get_type': 0, 'position': ['formulaParams']}, # 公式参数
    "sample_preparation": {"fill_type": 0, 'get_type': 0, 'children': ['step', 'formula_params'], 'connect_str': ' '}, 
    'storage_condition': {"fill_type": 0, 'get_type': 0, 'position': ['storageConditions']}, # 存放条件 □室温   □冷藏   冷冻
    'standard_solution_number': {"fill_type": 0, 'get_type': 0, 'position': ['standardSolutionInfo']}, # 标准溶液及编号
    'regression_equation': {"fill_type": 0, 'get_type': 0, 'position': ['regressionEquation']}, # 回归方程

}

table_name_list = {
    '光度测量表格': {},
    '定量测量表格': {},
    '光谱扫描表格': {
        "名称": {'position': ['name']},
        "波峰": {'position': ['peak']},
        "波谷": {'position': ['valley']},
        "标记点": {'position': ['markPoint']},
        "参数设置": {'position': []},
        "参数数据": {'position': ['parameterData']},
        "数据类型": {'position': ['dataType']}
    },
    '时间扫描表格': {},
    '光度测量原始记录表格': {}
    }


    
def handle_endpoint_data_to_table_row(table_fields: list, common_table_val) -> list:
    header_row = list(table_fields.keys())
    table_row = [header_row]
    table_row_key = []
    for k, v in table_fields.items():
        if v.get('position'):
            table_row_key.append(v.get('position')[0])
        else:
            table_row_key.append('')
    for row in common_table_val:
        row_data = []
        for k in table_row_key:
            v = row.get(k)
            if v:
                if isinstance(v, list): 
                    v = v[0]
            else:
                v = ''
            row_data.append(v)
        table_row.append(row_data)
    return table_row


class BaseTableDataHandler():

    def get_standard_head_and_data(self, data, m):
        header = None
        result_standard_data_list = []
        stand_head_list = data.get('standHeadList')
        for stand_head in stand_head_list:
            if stand_head.get('identity') == m:
                header = stand_head.get('name')
        standard_data_list = data.get('standDataList')
        for standard_data in standard_data_list:
            result_standard_data_list.append(standard_data.get(m))
        return header, result_standard_data_list
    
    def REVERS_TABLE_NAME_MAP(self, TABLE_NAME_MAP):
        l = {}
        for book_mark_name, table_name in TABLE_NAME_MAP.items():
            if table_name not in l:
                l[table_name] = []
            l[table_name].append(book_mark_name)
        return l

             
def checkbox(checked: bool) -> str:
    CHECKED = "☑"
    UNCHECKED = "☐"
    """返回复选框符号"""
    return CHECKED if checked else UNCHECKED
        
        
data = {

    "仪器编号": {"fill_type": 0, 'get_type': 0, 'position': ['instrumentSerialNumber']},
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
    "检测项目": {"fill_type": 0, 'get_type': 0, 'position': ['project']},
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
    "计算公式": {"fill_type": 0, 'get_type': 0, 'position': ['calculationFormula']},
    "阶梯矫正": {"fill_type": 0, 'get_type': 0, 'position': ['stairCorrection']},
    "阶梯校正": {"fill_type": 0, 'get_type': 0, 'position': ['stairCorrection']},
    "样品名称": {"fill_type": 0, 'get_type': 0, 'position': ['sampleName']},
    "方法名称": {"fill_type": 0, 'get_type': 0, 'position': ['methodName']},
    "操作步骤": {"fill_type": 0, 'get_type': 0, 'position': ['steps']},
    "仪器名称": {"fill_type": 0, 'get_type': 0, 'position': ['instrumentName']},
    "仪器型号": {"fill_type": 0, 'get_type': 0, 'position': ['instrumentModel']},
    "环境温度": {"fill_type": 0, 'get_type': 0, 'position': ['ambientTemperature']},
    "相对湿度": {"fill_type": 0, 'get_type': 0, 'position': ['relativeHumidity']},
    "质量等级": {"fill_type": 0, 'get_type': 0, 'position': ['qualityLevel']},
    "比色皿光程": {"fill_type": 0, 'get_type': 0, 'position': ['colorPlateWavelength']},
    "式中": {"fill_type": 0, 'get_type': 0, 'position': ['formulaParams']},
    "收样日期": {"fill_type": 0, 'get_type': 0, 'position': ['samplingTime']},
    "样品状态": {"fill_type": 0, 'get_type': 0, 'position': ['sampleState']},
    "接样日期": {"fill_type": 0, 'get_type': 0, 'position': ['samplingTime']},
    "分析日期": {"fill_type": 0, 'get_type': 0, 'position': ['detectionEndTime']},
    "仪器名称及型号": {"fill_type": 0, 'get_type': 0, 'children': ['仪器名称', '仪器型号'], 'connect_str': ' '},
    "分析方法及编号": {"fill_type": 0, 'get_type': 0, 'children': ['方法名称', '方法编号'], 'connect_str': ' '}
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
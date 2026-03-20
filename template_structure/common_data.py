

title_mapping = { # 全部加t
    'project_t': {'name': '检测项目', 'font': '宋体', 'font_size': 12},
    'instrument_num_t': {'name': '仪器编号', 'font': '宋体', 'font_size': 12},
    'trh_t': {'name': '环境条件', 'font': '宋体', 'font_size': 12}, # Temperature and Humidity
    'detection_time_t': {'name': '分析日期', 'font': '宋体', 'font_size': 12},
    'storage_condition_t': {'name': '存放条件', 'font': '宋体', 'font_size': 12}, # Storage Conditions
    'instrument_name_t': {'name': '仪器名称', 'font': '宋体', 'font_size': 12},
    'detection_basis_t': {'name': '检测依据', 'font': '宋体', 'font_size': 12},
    'sample_status_t': {'name': '样品状态', 'font': '宋体', 'font_size': 12},
    'standard_solution_number_t': {'name': '标准溶液及编号', 'font': '宋体', 'font_size': 12},
    'solution_concentration_t': {'name': '溶液浓度()', 'font': '宋体', 'font_size': 12},
    'regression_equation_t': {'name': '回归方程', 'font': '宋体', 'font_size': 12}, # Regression equation
    'calculation_formula_t': {'name': '计算公式', 'font': '宋体', 'font_size': 12},
    'remark_t': {'name': '备注', 'font': '宋体', 'font_size': 12},
    'sample_preparation_t': {'name': '样品前处理', 'font': '宋体', 'font_size': 12},

    # 原始数据模板用 也可能在原始记录中用
    # 光谱
    '仪器型号_t': {'name': '仪器型号', 'font': '宋体', 'font_size': 12},
    '仪器序号_t': {'name': '仪器序号', 'font': '宋体', 'font_size': 12},
    '光谱带宽_t': {'name': '光谱带宽', 'font': '宋体', 'font_size': 12},
    '扫描范围_t': {'name': '扫描范围', 'font': '宋体', 'font_size': 12},
    '光度模式_t': {'name': '光度模式', 'font': '宋体', 'font_size': 12},
    '增益_t': {'name': '增益', 'font': '宋体', 'font_size': 12},
    '扫描间隔_t': {'name': '扫描间隔', 'font': '宋体', 'font_size': 12},
    '扫描速度_t': {'name': '扫描速度', 'font': '宋体', 'font_size': 12},
    '能量灯_t': {'name': '能量灯', 'font': '宋体', 'font_size': 12},
    '数据文件_t': {'name': '数据文件', 'font': '宋体', 'font_size': 12},
    '分析时间_t': {'name': '分析时间', 'font': '宋体', 'font_size': 12},
    '方法名称_t': {'name': '方法名称', 'font': '宋体', 'font_size': 12},
    '检测项目_t': {'name': '检测项目', 'font': '宋体', 'font_size': 12},
    '备注_t': {'name': '备注', 'font': '宋体', 'font_size': 12},
    '光谱扫描图片_t': {'name': '光谱扫描图片', 'font': '宋体', 'font_size': 12},
    # 定量
    '切换样品池_t' : {'name': '切换样品池', 'font': '宋体', 'font_size': 12},
    '零点插入_t': {'name': '零点插入', 'font': '宋体', 'font_size': 12},
    '测量波长_t': {'name': '测量波长', 'font': '宋体', 'font_size': 12},
    '强制过零点_t': {'name': '强制过零点', 'font': '宋体', 'font_size': 12},
    '数据文件_t': {'name': '数据文件', 'font': '宋体', 'font_size': 12},
    '分析时间_t': {'name': '分析时间', 'font': '宋体', 'font_size': 12},
    '波长模式_t': {'name': '波长模式', 'font': '宋体', 'font_size': 12},
    '曲线方程_t': {'name': '曲线方程', 'font': '宋体', 'font_size': 12},
    '方程次数_t': {'name': '方程次数', 'font': '宋体', 'font_size': 12},
    '公式_t': {'name': '公式', 'font': '宋体', 'font_size': 12},
    '方法名称_t': {'name': '方法名称', 'font': '宋体', 'font_size': 12},
    # 'k0': '',
    # 'k1': '',
    # 'k2': '',
    # 'k3': '',
    # 'r2_t': {'name': 'r2', 'font': '宋体', 'font_size': 12},
    # 'r_t': {'name': 'r', 'font': '宋体', 'font_size': 12},
    '重复测量_t': {'name': '重复测量', 'font': '宋体', 'font_size': 12},
    'k_t': {'name': 'k', 'font': '宋体', 'font_size': 12},
    '标准浓度_t': {'name': '标准浓度', 'font': '宋体', 'font_size': 12},

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
    "a": {"fill_type": 0, 'get_type': 0, 'position': ['curveParams']},
    "b": {"fill_type": 0, 'get_type': 0, 'position': ['curveParams']},
    "r": {"fill_type": 0, 'get_type': 0, 'position': ['r']},
    "regression_equation": {"fill_type": 0, 'get_type': 0, 'position': ['curveFormula']}, # 回归方程
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
    "sample_preparation_1": {"fill_type": 0, 'get_type': 0, 'position': ['steps']}, 
    "sample_preparation_2": {"fill_type": 0, 'get_type': 0, 'position': ['formulaParams']}, 
    'storage_condition': {"fill_type": 0, 'get_type': 0, 'position': ['storageConditions']}, # 存放条件 □室温   □冷藏   冷冻
    'standard_solution_number': {"fill_type": 0, 'get_type': 0, 'position': ['standardSolutionInfo']}, # 标准溶液及编号
    'regression_equation': {"fill_type": 0, 'get_type': 0, 'position': ['curveFormula']}, # 回归方程


    "增益": {"fill_type": 0, 'get_type': 0, 'position': ['gain']},
    "备注": {"fill_type": 0, 'get_type': 0, 'position': ['remark']},
    "扫描速度": {"fill_type": 0, 'get_type': 0, 'position': ['scanSpeed']},
    "重复次数": {"fill_type": 0},
    "能量灯": {"fill_type": 0, 'get_type': 0, 'position': ['energyLight']},
    "table_data": {"fill_type": 0},
    "扫描范围": {"fill_type": 0, 'get_type': 0, 'position': ['scanRange']},
    "仪器型号": {"fill_type": 0, 'get_type': 0, 'position': ['instrumentModel']},
    "重复模式": {"fill_type": 0},
    "光度模式": {"fill_type": 0, 'get_type': 0, 'position': ['luminosityMode']},
    "波长间隔": {"fill_type": 0},
    "扫描间隔": {"fill_type": 0, 'get_type': 0, 'position': ['timeInterval']},
    "is_repeat": {"fill_type": 0},
    "数据文件": {"fill_type": 0, 'get_type': 0, 'position': ['taskName']},
    "光谱扫描图片": {"fill_type": 0, 'get_type': 0, 'position': ['spectrumScanImage']},
    "仪器序号": {"fill_type": 0, 'get_type': 0, 'position': ['instrumentSerialNumber']},
    "方法名称": {"fill_type": 0, 'get_type': 0, 'position': ['methodName']},
    "光谱带宽": {"fill_type": 0, 'get_type': 0, 'position': ['spectrumBandwidth']},
    "show_gain": {"fill_type": 0},
    "分析时间": {"fill_type": 0, 'get_type': 0, 'position': ['detectionEndTime']},
    "show_energy_light": {"fill_type": 0}

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

    def columns_to_rows(self, data):
        """
        将 {'a':[1,2,3], 'b':[4,5,6], 'c':[7,8,9]}
        转成 [{'a':1,'b':4,'c':7}, {'a':2,'b':5,'c':8}, {'a':3,'b':6,'c':9}]
        """
        if not data:
            return []
        keys = list(data.keys())
        columns = [data[k] for k in keys]
        return [dict(zip(keys, row)) for row in zip(*columns)]
    
    
    def table_handle_get_unknown_sample_header(self, m):
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
            if map_relation:
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
    

    def table_handle_get_unknown_sample_data(self, identity: str):
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

             
def checkbox(checked: bool) -> str:
    CHECKED = "☑"
    UNCHECKED = "☐"
    """返回复选框符号"""
    return CHECKED if checked else UNCHECKED
        
        

# 模板字段定义
# fill_type: 0 表示从模板中提取的字段, fill_type: 1 表示表格截取的字段

# get_type: 0: 表示从通用数据中取, 1: 表示从接口中取 2: 表从数据库中取

python_template_var = {
    "检测开始时间": {"fill_type": 0},
    "备注": {"fill_type": 0},
    "式中": {"fill_type": 0},
    "光谱带宽": {"fill_type": 0},
    "能量灯": {"fill_type": 0},
    "收样名称": {"fill_type": 0},
    "参考方法": {"fill_type": 0},
    "参考标准": {"fill_type": 0},
    "收样日期": {"fill_type": 0},
    "检测依据": {"fill_type": 0},
    "样品编号": {"fill_type": 0},
    "光度模式": {"fill_type": 0},
    "检测者": {"fill_type": 0},
    "检测结束时间": {"fill_type": 0},
    "计算公式": {"fill_type": 0},
    "参照": {"fill_type": 0},
    "复核者": {"fill_type": 0},
    "制备设备": {"fill_type": 0},
    "仪器编号": {"fill_type": 0},
    "阶梯矫正": {"fill_type": 0},
    "检测项目": {"fill_type": 0},
    "判定依据": {"fill_type": 0},
    "仪器波长": {"fill_type": 0}
}
table_fields = [
    {
        "headers": [
            [
                "名称",
                "波峰",
                "波谷",
                "标记点",
                "参数数据",
                "数据类型"
            ]
        ],
        "col_count": 6,
        "data_rows": [
            [
                "",
                "",
                "",
                "",
                "",
                ""
            ]
        ],
        "row_count": 2,
        "table_name": "光谱扫描表格",
        "column_width": [
            None,
            None,
            None,
            None,
            None,
            None
        ],
        "structure_type": 0
    }
]


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
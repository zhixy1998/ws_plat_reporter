# 模板字段定义
# fill_type: 0 表示从模板中提取的字段, fill_type: 1 表示表格截取的字段

# get_type: 0: 表示从通用数据中取, 1: 表示从接口中取 2: 表从数据库中取

python_template_var = {
    "方法信息": {"fill_type": 0},
    "光度模式": {"fill_type": 0},
    "扫描范围": {"fill_type": 0},
    "时间扫描图片": {"fill_type": 0},
    "分析时间": {"fill_type": 0},
    "仪器型号": {"fill_type": 0},
    "数据类型": {"fill_type": 0},
    "分析员": {"fill_type": 0},
    "审核员": {"fill_type": 0},
    "检测项目": {"fill_type": 0},
    "数据文件名": {"fill_type": 0},
    "注释": {"fill_type": 0},
    "扫描速度": {"fill_type": 0},
    "原始数据": {"fill_type": 0},
    "扫描间隔": {"fill_type": 0},
    "仪器编号": {"fill_type": 0},
    "光谱带宽": {"fill_type": 0}
}
table_fields = [
    {
        "headers": [
            [
                "序号",
                "峰/谷",
                "波长(nm)",
                "Abs",
                "注释"
            ]
        ],
        "col_count": 5,
        "data_rows": [
            [
                "",
                "",
                "",
                "",
                ""
            ],
            [
                "",
                "",
                "",
                "",
                ""
            ],
            [
                "",
                "",
                "",
                "",
                ""
            ]
        ],
        "row_count": 4,
        "table_name": "时间扫描表格",
        "column_width": [
            1082040,
            1082040,
            1082040,
            1082675,
            1082675
        ],
        "structure_type": 0
    }
]


def handle_endpoint_data_to_table_row(table_header_data_mapping: list, common_table_val) -> list:
    try:
        headers_data_mapping = {}
        row = []

        header_row = []
        for header_info in common_table_val.get('headList'):
            headers_data_mapping[header_info.get('name')] = header_info.get('identity')
            header_row.append(header_info.get('name')) 
        row.append(header_row)
        for data_info in common_table_val.get('dataList'):
            one_row = []
            for header_name in header_row:
                row_data = data_info.get(headers_data_mapping.get(header_name))
                if row_data:
                    one_row.append(row_data)
                else:
                    one_row.append('')
            row.append(one_row)
        # print(common_table_val)
        return row
    except Exception as e:
        return []
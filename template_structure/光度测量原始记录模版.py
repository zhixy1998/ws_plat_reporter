# 模板字段定义
# fill_type: 0 表示从模板中提取的字段, fill_type: 1 表示表格截取的字段

# get_type: 0: 表示从通用数据中取, 1: 表示从接口中取 2: 表从数据库中取

python_template_var = {
    "分析时间": {"fill_type": 0},
    "审核员": {"fill_type": 0},
    "方法信息": {"fill_type": 0},
    "注释": {"fill_type": 0},
    "仪器型号": {"fill_type": 0},
    "光谱带宽": {"fill_type": 0},
    "数据类型": {"fill_type": 0},
    "数据文件": {"fill_type": 0},
    "检测项目": {"fill_type": 0},
    "仪器序号": {"fill_type": 0},
    "分析员": {"fill_type": 0}
}
table_fields = [
    {
        "headers": [
            [
                "序号",
                "编号",
                "模式",
                "A 350.00nm",
                "B313.00 nm",
                "C 257.00 nm",
                "D 235.00 nm"
            ]
        ],
        "col_count": 7,
        "data_rows": [
            [
                "",
                "",
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
                "",
                "",
                ""
            ],
            [
                "",
                "",
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
                "",
                "",
                ""
            ]
        ],
        "row_count": 5,
        "table_name": "光度测量原始记录表格",
        "column_width": [
            542925,
            540385,
            528320,
            842010,
            868045,
            1043305,
            1046480
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
    
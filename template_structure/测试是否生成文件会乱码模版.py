# 模板字段定义
# fill_type: 0 表示从模板中提取的字段, fill_type: 1 表示表格截取的字段

# get_type: 0: 表示从通用数据中取, 1: 表示从接口中取 2: 表从数据库中取

python_template_var = {
    "样品名称": {"fill_type": 0},
    "备注": {"fill_type": 0},
    "单项判定": {"fill_type": 0},
    "仪器名称": {"fill_type": 0},
    "计算公式": {"fill_type": 0},
    "比色皿光程": {"fill_type": 0},
    "检测方法": {"fill_type": 0},
    "仪器编号": {"fill_type": 0},
    "检测开始时间": {"fill_type": 0},
    "判定依据": {"fill_type": 0},
    "检测项目": {"fill_type": 0},
    "式中": {"fill_type": 0},
    "样品状态": {"fill_type": 0},
    "检测结束时间": {"fill_type": 0},
    "质量等级": {"fill_type": 0},
    "技术要求": {"fill_type": 0},
    "环境温度": {"fill_type": 0},
    "仪器型号": {"fill_type": 0},
    "检测者": {"fill_type": 0},
    "复核者": {"fill_type": 0},
    "操作步骤": {"fill_type": 0},
    "收样日期": {"fill_type": 0},
    "样品编号": {"fill_type": 0},
    "仪器波长": {"fill_type": 0},
    "光度模式": {"fill_type": 0},
    "计算方法": {"fill_type": 0},
    "相对湿度": {"fill_type": 0}
}
table_fields = [
    {
        "headers": [
            [
                "",
                "检测时间和对应的吸光值",
                "T\n(min)",
                "X\nml/(g·h)",
                "平均值\nml/(g·h)",
                "报告值\nml/(g·h)"
            ]
        ],
        "col_count": 6,
        "data_rows": [
            [
                "1",
                "",
                "",
                "",
                "",
                ""
            ],
            [
                "2",
                "",
                "",
                "",
                "",
                ""
            ]
        ],
        "row_count": 3,
        "table_name": "光度测量表格",
        "column_width": [
            180975,
            3119120,
            450215,
            629920,
            630555,
            629920
        ],
        "structure_type": 0
    }
]

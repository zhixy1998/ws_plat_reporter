# 模板字段定义
# fill_type: 0 表示从模板中提取的字段, fill_type: 1 表示表格截取的字段

# get_type: 0: 表示从通用数据中取, 1: 表示从接口中取 2: 表从数据库中取

python_template_var = {
    "复核者": {"fill_type": 0},
    "收样日期": {"fill_type": 0},
    "检测项目": {"fill_type": 0},
    "光谱带宽": {"fill_type": 0},
    "参照": {"fill_type": 0},
    "判定依据": {"fill_type": 0},
    "检测开始时间": {"fill_type": 0},
    "能量灯": {"fill_type": 0},
    "收样名称": {"fill_type": 0},
    "样品编号": {"fill_type": 0},
    "制备设备": {"fill_type": 0},
    "备注": {"fill_type": 0},
    "检测者": {"fill_type": 0},
    "检测结束时间": {"fill_type": 0},
    "计算公式": {"fill_type": 0},
    "仪器波长": {"fill_type": 0},
    "参考方法": {"fill_type": 0},
    "参考标准": {"fill_type": 0},
    "仪器编号": {"fill_type": 0},
    "式中": {"fill_type": 0},
    "光度模式": {"fill_type": 0},
    "检测依据": {"fill_type": 0},
    "阶梯矫正": {"fill_type": 0},
    "": {"fill_type": 1},
    "名称": {"fill_type": 1},
    "波峰": {"fill_type": 1},
    "波谷": {"fill_type": 1},
    "标记点": {"fill_type": 1},
    "参数设置": {"fill_type": 1},
    "参数数据": {"fill_type": 1},
    "数据类型": {"fill_type": 1}
}

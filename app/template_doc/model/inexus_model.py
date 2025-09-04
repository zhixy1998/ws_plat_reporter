from tortoise import fields, models


class T_GmpPermission(models.Model):
    """系统权限表"""
    id = fields.CharField(primary_key=True, max_length=64, description='主键id')
    device_type_id = fields.IntField(null=True, description='仪器类型id')
    sid = fields.IntField(null=True, description='权限序号')
    permission_name = fields.CharField(max_length=255, null=True, description='权限名称')
    permission_type = fields.CharField(max_length=255, null=True, description='权限类型')
    remark = fields.TextField(null=True, description='备注')
    create_time = fields.DatetimeField(null=True, description='创建时间')
    update_time = fields.DatetimeField(null=True, description='修改时间')
    create_user = fields.CharField(max_length=20, null=True, description='创建者')
    update_user = fields.CharField(max_length=20, null=True, description='修改者')

    class Meta:
        table = "t_gmp_permission"
        # primary_key = "id" # Tortoise ORM 默认会将 primary_key=True 的字段作为主键

    def __str__(self):
        return f"Permission: {self.permission_name}"


class T_GmpUserGroup(models.Model):
    """用户组表"""
    id = fields.CharField(primary_key=True, max_length=64, description='主键id')
    user_type = fields.CharField(max_length=255, null=True, description='组名称')
    password_valid = fields.IntField(null=True, description='密码时效性，0，不设置为0，以天为单位')
    password_rule = fields.CharField(max_length=200, null=True, description='密码复杂度')
    login_error_time = fields.IntField(null=True, description='登录错误次数')
    login_error_done = fields.CharField(max_length=255, null=True, description='登陆错误处理')
    is_valid = fields.SmallIntField(null=True, description='是否有效') # tinyint(4)
    remark = fields.TextField(null=True, description='备注')
    reason = fields.TextField(null=True, description='操作原因')
    system_permission_list = fields.CharField(max_length=255, null=True, description='系统权限')
    create_time = fields.DatetimeField(null=True, description='创建时间')
    update_time = fields.DatetimeField(null=True, description='修改时间')
    create_user = fields.CharField(max_length=20, null=True, description='创建者')
    update_user = fields.CharField(max_length=20, null=True, description='修改者')

    class Meta:
        table = "t_gmp_user_group"

    def __str__(self):
        return f"UserGroup: {self.user_type}"


class T_InsAutoInjector(models.Model):
    id = fields.CharField(primary_key=True, max_length=64)
    device_serial_number = fields.CharField(max_length=32, description='仪器序列号')
    message_port = fields.CharField(max_length=10, null=True, description='通信端口')
    connect_status = fields.SmallIntField(null=True, description='联机状态') # tinyint(2)
    is_start_init = fields.SmallIntField(null=True, description='是否开机对进样器初始化， 0-否，1-是') # tinyint(4)
    enter_speed = fields.SmallIntField(null=True, description='进样速度') # tinyint(4)
    enter_time = fields.CharField(max_length=10, null=True, description='进样时间')
    wash_speed = fields.SmallIntField(null=True, description='清洗速度') # tinyint(4)
    wash_time = fields.CharField(max_length=10, null=True, description='清洗时间')
    waiting_time = fields.CharField(max_length=10, null=True, description='停泵等待时间')
    is_wash_before_enter = fields.SmallIntField(null=True, description='是否进样前清洗，0-否，1，是') # tinyint(4)
    create_time = fields.DatetimeField(null=True, description='创建时间')
    update_time = fields.DatetimeField(null=True, description='修改时间')
    create_user = fields.CharField(max_length=20, null=True, description='创建者')
    update_user = fields.CharField(max_length=20, null=True, description='修改者')

    class Meta:
        table = "t_ins_auto_injector"


class T_InsCalibrationConfig(models.Model):
    """校正类型默认表，记录不同仪器所具备的校正类型"""
    id = fields.IntField(primary_key=True) # AUTO_INCREMENT
    calibration_name = fields.CharField(max_length=255, null=True)
    calibration_type = fields.IntField(null=True)
    device_type = fields.CharField(max_length=255, null=True)

    class Meta:
        table = "t_ins_calibration_config"

    def __str__(self):
        return f"CalibrationConfig: {self.calibration_name}"


class T_InsCalibrationParam(models.Model):
    """校正类型对应的参数表"""
    id = fields.IntField(primary_key=True) # AUTO_INCREMENT
    calibration_type = fields.IntField(null=True)
    param_name = fields.CharField(max_length=64, null=True)
    param = fields.CharField(max_length=64, null=True)
    param_type = fields.IntField(null=True, description='参数类型，0-固定值，1-输入框，2-下拉框')

    class Meta:
        table = "t_ins_calibration_param"

    def __str__(self):
        return f"CalibrationParam: {self.param_name}"


class T_InsCalibrationTemp(models.Model):
    """校正参数记录表"""
    id = fields.CharField(primary_key=True, max_length=64)
    device_serial_number = fields.CharField(max_length=64, null=True)
    calibration_type = fields.IntField(null=True)
    param = fields.CharField(max_length=255, null=True)
    param_value = fields.CharField(max_length=255, null=True)
    create_time = fields.DatetimeField(null=True, description='创建时间')
    update_time = fields.DatetimeField(null=True, description='修改时间')
    create_user = fields.CharField(max_length=20, null=True, description='创建者')
    update_user = fields.CharField(max_length=20, null=True, description='修改者')

    class Meta:
        table = "t_ins_calibration_temp"


class T_InsCalibrationValue(models.Model):
    """参数类型和默认值表"""
    id = fields.IntField(primary_key=True) # AUTO_INCREMENT
    param_id = fields.IntField(null=True)
    param_key = fields.CharField(max_length=64, null=True)
    param_value = fields.CharField(max_length=10, null=True)

    class Meta:
        table = "t_ins_calibration_value"


class T_InsConfigSetting(models.Model):
    """仪器系统配置"""
    id = fields.CharField(primary_key=True, max_length=64, description='主键id')
    device_serial_number = fields.CharField(max_length=255, null=True)
    is_time_startup = fields.SmallIntField(null=True, description='是否自动开机') # tinyint(4)
    startup_time = fields.CharField(max_length=20, null=True, description='自动开机时间')
    message_port = fields.SmallIntField(null=True, description='通讯端口') # tinyint(4)
    annex_setting = fields.SmallIntField(null=True, description='附件设置') # tinyint(4)
    band_width = fields.FloatField(null=True, description='光谱带宽')
    create_time = fields.DatetimeField(null=True, description='创建时间')
    update_time = fields.DatetimeField(null=True, description='修改时间')
    create_user = fields.CharField(max_length=20, null=True, description='创建者')
    update_user = fields.CharField(max_length=20, null=True, description='修改者')

    class Meta:
        table = "t_ins_config_setting"


class T_InsInfoTemp(models.Model):
    """设备信息表"""
    id = fields.CharField(primary_key=True, max_length=64)
    device_serial_number = fields.CharField(max_length=64, null=True)
    device_ip = fields.CharField(max_length=64, null=True)
    connect_status = fields.SmallIntField(null=True) # tinyint(4)
    machine_ip = fields.CharField(max_length=64, null=True)
    device_port = fields.IntField(null=True)
    is_inited = fields.SmallIntField(null=True, description='0：未完成；1：自检成功； 2：自检失败； 3：自检进行中') # tinyint(4)
    is_dev_opened = fields.SmallIntField(null=True, description='0-未开机，1-已开机') # tinyint(4)
    create_time = fields.DatetimeField(null=True, description='创建时间')
    update_time = fields.DatetimeField(null=True, description='修改时间')
    create_user = fields.CharField(max_length=20, null=True, description='创建者')
    update_user = fields.CharField(max_length=20, null=True, description='修改者')

    class Meta:
        table = "t_ins_info_temp"


class T_InsInitTemp(models.Model):
    """自检任务表"""
    id = fields.CharField(primary_key=True, max_length=64)
    device_info_id = fields.CharField(max_length=64, null=True)
    device_serial_number = fields.CharField(max_length=64, null=True, description='序列号')
    init_task_num = fields.IntField(null=True, description='初始化条目')
    init_status = fields.SmallIntField(null=True, description='初始化状态') # tinyint(4)
    create_time = fields.DatetimeField(null=True, description='创建时间')
    update_time = fields.DatetimeField(null=True, description='修改时间')
    create_user = fields.CharField(max_length=20, null=True, description='创建者')
    update_user = fields.CharField(max_length=20, null=True, description='修改者')

    class Meta:
        table = "t_ins_init_temp"


class T_IntInjectionTrayParam(models.Model):
    """进样盘参数表"""
    id = fields.CharField(primary_key=True, max_length=64)
    device_serial_number = fields.CharField(max_length=31, null=True, description='仪器序列号')
    panel = fields.CharField(max_length=10, null=True, description='盘区设定')
    is_selected = fields.SmallIntField(null=True, description='是否选中') # tinyint(4)
    plate_rail = fields.IntField(null=True, description='盘架设定')
    num_info = fields.CharField(max_length=20, null=True, description='编号信息')
    create_time = fields.DatetimeField(null=True, description='创建时间')
    update_time = fields.DatetimeField(null=True, description='修改时间')
    create_user = fields.CharField(max_length=20, null=True, description='创建者')
    update_user = fields.CharField(max_length=20, null=True, description='修改者')

    class Meta:
        table = "t_int_injection_tray_param"


class T_MeasureAnalysisData(models.Model):
    """分析数据表"""
    id = fields.CharField(primary_key=True, max_length=36, description='分析数据id')
    analysis_name = fields.CharField(max_length=255, null=True, description='分析名称')
    task_id = fields.CharField(max_length=255, null=True, description='测量任务id')
    sample_key = fields.CharField(max_length=255, null=True, description='样品id')
    analysis_param = fields.TextField(null=True, description='分析参数')
    analysis_result = fields.JSONField(null=True, description='分析结果') # json
    analysis_type = fields.CharField(max_length=255, null=True, description='变换类型')
    gauge_point = fields.JSONField(null=True, description='标记点') # json
    peak = fields.JSONField(null=True, description='峰') # json
    grain = fields.JSONField(null=True, description='谷') # json
    color = fields.CharField(max_length=255, null=True, description='颜色')
    analysis_data_image = fields.BinaryField(null=True, description='分析数据图像') # longblob
    is_delete = fields.CharField(max_length=255, null=True, description='是否删除(0.正常,1.已删除)')

    class Meta:
        table = "t_measure_analysis_data"


class T_MeasureData(models.Model):
    """测量数据表"""
    id = fields.CharField(primary_key=True, max_length=36, description='测量数据id')
    task_id = fields.CharField(max_length=255, null=True, description='测量任务id')
    sample_key = fields.CharField(max_length=255, null=True, description='样品Key')
    instrument_data = fields.JSONField(null=True, description='仪器数据') # json
    original_calculation_data = fields.JSONField(null=True, description='原始计算数据') # json
    measurement_start_time = fields.DatetimeField(null=True, description='测量开始时间')
    measurement_end_time = fields.DatetimeField(null=True, description='测量结束时间')
    gauge_point = fields.JSONField(null=True, description='标记点') # json
    peak = fields.JSONField(null=True, description='峰') # json
    grain = fields.JSONField(null=True, description='谷') # json
    sampling_time = fields.DatetimeField(null=True, description='采样时间')
    data_image = fields.BinaryField(null=True, description='数据图像') # longblob
    remark = fields.CharField(max_length=255, null=True, description='备注')
    is_delete = fields.CharField(max_length=255, null=True, description='是否删除')

    class Meta:
        table = "t_measure_data"
        indexes = (("measurement_start_time",),) # Added for idx_measurement_start_time


class T_MeasureMethod(models.Model):
    """测量方法表"""
    id = fields.CharField(primary_key=True, max_length=36, description='方法id')
    preprocess_key = fields.CharField(max_length=768, null=True, description='前处理Key')
    multiple_calculation_formula_key = fields.CharField(max_length=768, null=True, description='多个计算公式Key')
    project_item_key = fields.CharField(max_length=255, null=True, description='所属项目Key(当选用的是公共方法则项目key为空)')
    method_name = fields.CharField(max_length=255, null=True, description='方法名称')
    measurement_type = fields.CharField(max_length=255, null=True, description='测量类型')
    measurement_param_info = fields.JSONField(null=True, description='测量参数信息') # json
    is_sharing_method = fields.CharField(max_length=255, null=True, description='是否共享方法')
    method_create_time = fields.DatetimeField(null=True, description='方法创建时间')
    method_creator = fields.CharField(max_length=255, null=True, description='方法创建人')
    field2 = fields.CharField(max_length=255, null=True, description='预留字段2')
    field3 = fields.CharField(max_length=255, null=True, description='预留字段3')
    field4 = fields.CharField(max_length=255, null=True, description='预留字段4')
    field5 = fields.CharField(max_length=255, null=True, description='预留字段5')

    class Meta:
        table = "t_measure_method"


class T_MeasureProject(models.Model):
    """项目表"""
    id = fields.CharField(primary_key=True, max_length=36, description='项目id')
    project_name = fields.CharField(max_length=255, null=True, description='项目名称')
    create_time = fields.DatetimeField(null=True, description='创建时间')
    creator_key = fields.CharField(max_length=255, null=True, description='创建人Key')
    remark = fields.CharField(max_length=255, null=True, description='备注')
    last_updated_by = fields.CharField(max_length=255, null=True, description='最近更新人')
    last_updated_time = fields.DatetimeField(null=True, description='最近更新时间')
    field3 = fields.CharField(max_length=255, null=True, description='预留字段3')
    field4 = fields.CharField(max_length=255, null=True, description='预留字段4')
    field5 = fields.CharField(max_length=255, null=True, description='预留字段5')

    class Meta:
        table = "t_measure_project"


class T_MeasureSample(models.Model):
    """样品信息表"""
    id = fields.CharField(primary_key=True, max_length=36, description='样品id')
    sample_number = fields.CharField(max_length=255, null=True, description='样品编号')
    sample_type = fields.CharField(max_length=255, null=True, description='样品类型(0.空白样品,1.标准样品)')
    sample_kind = fields.CharField(max_length=255, null=True, description='样品种类(0.标准样品 1.未知样品)')
    sample_name = fields.CharField(max_length=255, null=True, description='样品名称')
    dilution_ratio = fields.CharField(max_length=255, null=True, description='稀释倍数')
    sample_volume = fields.CharField(max_length=255, null=True, description='取样量')
    constant_volume = fields.CharField(max_length=255, null=True, description='定容体积')
    normal_concentration = fields.CharField(max_length=255, null=True, description='标准浓度')
    sample_location = fields.CharField(max_length=255, null=True, description='样品位置')
    sample_description = fields.TextField(null=True, description='样品描述')
    input_data = fields.TextField(null=True, description='输入数据')
    color = fields.CharField(max_length=255, null=True, description='颜色')

    class Meta:
        table = "t_measure_sample"


class T_MeasureTask(models.Model):
    """测量任务表"""
    id = fields.CharField(primary_key=True, max_length=36, description='任务id')
    user_id = fields.CharField(max_length=50, null=True, description='用户id')
    task_name = fields.CharField(max_length=255, null=True, description='任务名称')
    create_time = fields.DatetimeField(null=True, description='创建时间')
    collection_start_time = fields.DatetimeField(null=True, description='采集起始时间')
    method_key = fields.CharField(max_length=255, null=True, description='方法Key')
    sample_key = fields.JSONField(null=True, description='样品key') # json
    project_item_key = fields.CharField(max_length=255, null=True, description='所属项目Key')
    start_time = fields.DatetimeField(null=True, description='开始时间')
    end_time = fields.DatetimeField(null=True, description='结束时间')
    device_serial_number = fields.CharField(max_length=255, null=True, description='序列号')
    is_delete = fields.CharField(max_length=255, null=True, description='是否删除')

    class Meta:
        table = "t_measure_task"


class T_ReportCalculationFormulas(models.Model):
    """计算公式表"""
    id = fields.IntField(primary_key=True) # AUTO_INCREMENT
    detection_id = fields.CharField(max_length=50, description='标准标识')
    result_identity = fields.CharField(max_length=50, description='结果标识')
    result_name = fields.CharField(max_length=100, description='结果名称')
    unit = fields.CharField(max_length=20, description='单位')
    input_param1_name = fields.CharField(max_length=100, description='输入参数1名称')
    input_param1_identity = fields.CharField(max_length=100, description='输入参数1标识')
    input_param2_name = fields.CharField(max_length=100, null=True, description='输入参数2名称')
    input_param2_identity = fields.CharField(max_length=100, null=True, description='输入参数2标识')
    input_param3_name = fields.CharField(max_length=100, null=True, description='输入参数3名称')
    input_param3_identity = fields.CharField(max_length=100, null=True, description='输入参数3标识')
    input_param4_name = fields.CharField(max_length=100, null=True, description='输入参数4名称')
    input_param4_identity = fields.CharField(max_length=100, null=True, description='输入参数4标识')
    input_param5_name = fields.CharField(max_length=100, null=True, description='输入参数5名称')
    input_param5_identity = fields.CharField(max_length=100, null=True, description='输入参数5标识')
    input_param6_name = fields.CharField(max_length=100, null=True, description='输入参数6名称')
    input_param6_identity = fields.CharField(max_length=100, null=True, description='输入参数6标识')
    input_param7_name = fields.CharField(max_length=100, null=True, description='输入参数7名称')
    input_param7_identity = fields.CharField(max_length=100, null=True, description='输入参数7标识')
    input_param8_name = fields.CharField(max_length=100, null=True, description='输入参数8名称')
    input_param8_identity = fields.CharField(max_length=100, null=True, description='输入参数8标识')
    input_param9_name = fields.CharField(max_length=100, null=True, description='输入参数9名称')
    input_param9_identity = fields.CharField(max_length=100, null=True, description='输入参数9标识')
    input_param10_name = fields.CharField(max_length=100, null=True, description='输入参数10名称')
    input_param10_identity = fields.CharField(max_length=100, null=True, description='输入参数10标识')
    formula_text = fields.TextField(null=True, description='公式文本')
    formula_image = fields.TextField(null=True, description='公式图片') # longtext
    detection_limit = fields.CharField(max_length=255, null=True, description='检出限')

    class Meta:
        table = "t_report_calculation_formulas"
        indexes = (("detection_id",),) # idx_standard_identity


class T_ReportQualityControl(models.Model):
    """质量控制表"""
    id = fields.IntField(primary_key=True) # AUTO_INCREMENT
    detection_id = fields.CharField(max_length=50, description='标准标识')
    control_type = fields.CharField(max_length=50, null=True, description='质控类型')
    control_description = fields.TextField(null=True, description='质控描述')
    control_formula = fields.CharField(max_length=255, null=True, description='质控公式')
    create_datetime = fields.DatetimeField(auto_now_add=True, description='创建时间') # timestamp with default CURRENT_TIMESTAMP
    update_datetime = fields.DatetimeField(auto_now=True, description='更新时间') # timestamp with default CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP

    class Meta:
        table = "t_report_quality_control"
        indexes = (("detection_id",),) # idx_standard_identity


class T_ReportRoundingRules(models.Model):
    """修约表"""
    id = fields.IntField(primary_key=True) # AUTO_INCREMENT
    detection_id = fields.CharField(max_length=100, description='标准标识')
    result_identity = fields.CharField(max_length=50, null=True, description='结果标识')
    rounding_type = fields.CharField(max_length=50, description='修约类型')
    rounding_condition = fields.CharField(max_length=100, null=True, description='修约条件')
    decimal_places = fields.IntField(default=0, description='保留小数位数')

    class Meta:
        table = "t_report_rounding_rules"
        indexes = (("detection_id",),) # idx_standard_identity


class T_ReportStandardDetection(models.Model):
    """标准信息表"""
    id = fields.IntField(primary_key=True) # AUTO_INCREMENT
    standard_identity = fields.CharField(max_length=150, description='标准标识')
    industry = fields.CharField(max_length=50, description='行业')
    detection_type = fields.CharField(max_length=50, description='检测类型')
    detection_instrument = fields.CharField(max_length=50, description='检测仪器')
    standard_number = fields.CharField(max_length=100, description='标准号')
    standard_name = fields.CharField(max_length=200, null=True, description='标准名称')
    detection_item = fields.CharField(max_length=50, description='检测项目')
    method_number = fields.CharField(max_length=20, null=True, description='第几法')
    remark = fields.CharField(max_length=500, null=True, description='备注')
    detection_parameters = fields.TextField(null=True, description='检测参数')
    release_date = fields.DatetimeField(null=True, description='发布时间')
    expiration_date = fields.DatetimeField(null=True, description='失效时间')
    effective_date = fields.DatetimeField(null=True, description='实施时间')
    release_status = fields.CharField(max_length=200, null=True, description='状态')
    industry_type = fields.CharField(max_length=50, null=True, description='类型')

    class Meta:
        table = "t_report_standard_detection"
        indexes = (("standard_identity",),) # idx_standard_identity


class T_ReportStandardPretreatment(models.Model):
    """标准前处理表"""
    id = fields.IntField(primary_key=True) # AUTO_INCREMENT
    detection_id = fields.CharField(max_length=100, description='标准标识id')
    pretreatment_description = fields.TextField(null=True, description='前处理描述')

    class Meta:
        table = "t_report_standard_pretreatment"
        indexes = (("detection_id",),) # idx_standard_identity


class T_ReportUpgradeVersion(models.Model):
    """升级版本记录表"""
    id = fields.IntField(primary_key=True, description='主键') # AUTO_INCREMENT
    version = fields.CharField(max_length=50, unique=True, description='版本号（如v2.1.3）')
    update_description = fields.TextField(null=True)
    create_time = fields.DatetimeField(auto_now_add=True, description='创建时间') # DEFAULT CURRENT_TIMESTAMP

    class Meta:
        table = "t_report_upgrade_version"
        # unique_together = (("version",),) # Unique constraint handled by unique=True on field


class T_SysconfigUser(models.Model):
    """系统用户表"""
    id = fields.CharField(primary_key=True, max_length=64, description='主键id')
    user_name = fields.CharField(max_length=100, unique=True, description='用户名（账号）')
    password = fields.CharField(max_length=50, description='密码')
    token = fields.CharField(max_length=500, null=True, description='记录当前token')
    user_real_name = fields.CharField(max_length=20, null=True, description='真实姓名')
    user_position = fields.CharField(max_length=50, null=True, description='用户职务')
    remark = fields.TextField(null=True, description='备注')
    group_name = fields.CharField(max_length=255, null=True, description='所属组')
    group_id = fields.CharField(max_length=64, null=True, description='组id')
    system_identity_id = fields.CharField(max_length=64, null=True, description='系统身份id')
    logo = fields.CharField(max_length=255, null=True, description='标志')
    digital_signature = fields.CharField(max_length=255, null=True, description='电子签名')
    digital_signature_path = fields.TextField(null=True, description='电子签名路径')
    is_valid = fields.SmallIntField(null=True, description='是否有效') # tinyint(4)
    is_login = fields.SmallIntField(null=True, description='是否已登陆') # tinyint(4)
    login_fail_count = fields.IntField(null=True, description='登陆失败次数')
    change_password_time = fields.DatetimeField(null=True, description='修改密码时间')
    reason = fields.TextField(null=True, description='修改密码原因')
    create_time = fields.DatetimeField(null=True, description='创建时间')
    update_time = fields.DatetimeField(null=True, description='修改时间')
    create_user = fields.CharField(max_length=20, null=True, description='创建者')
    update_user = fields.CharField(max_length=20, null=True, description='修改者')

    class Meta:
        table = "t_sysconfig_user"
        # unique_together = (("user_name",),) # Unique constraint handled by unique=True on field


class T_SystemAlgorithmConf(models.Model):
    """系统算法配置表"""
    id = fields.CharField(primary_key=True, max_length=64)
    integrating_sphere_k = fields.CharField(max_length=20, null=True, description='透过率门限系数k')
    transmittance_k = fields.CharField(max_length=20, null=True, description='积分球门限系数k')
    abs_k = fields.CharField(max_length=10, null=True, description='Abs门限系数k')
    create_time = fields.DatetimeField(null=True, description='创建时间')
    update_time = fields.DatetimeField(null=True, description='修改时间')
    create_user = fields.CharField(max_length=20, null=True, description='创建者')
    update_user = fields.CharField(max_length=20, null=True, description='修改者')

    class Meta:
        table = "t_system_algorithm_conf"


class T_SystemBusinessParam(models.Model):
    id = fields.CharField(primary_key=True, max_length=64)
    peak_interval = fields.CharField(max_length=20, null=True, description='峰间距')
    peak_valley_diff = fields.CharField(max_length=20, null=True, description='峰谷差')
    create_time = fields.DatetimeField(null=True, description='创建时间')
    update_time = fields.DatetimeField(null=True, description='修改时间')
    create_user = fields.CharField(max_length=20, null=True, description='创建者')
    update_user = fields.CharField(max_length=20, null=True, description='修改者')

    class Meta:
        table = "t_system_business_param"


class T_SystemDatabase(models.Model):
    """系统数据库配置"""
    id = fields.CharField(primary_key=True, max_length=64)
    global_port = fields.CharField(max_length=10, null=True)
    fast_login_switch = fields.BooleanField(null=True, description='快捷登录开关') # bit(1)
    main_database_ip = fields.CharField(max_length=20, null=True)
    main_database_port = fields.CharField(max_length=10, null=True)
    main_database_username = fields.CharField(max_length=64, null=True)
    main_database_password = fields.CharField(max_length=100, null=True)
    spare_database_ip = fields.CharField(max_length=20, null=True)
    spare_database_port = fields.CharField(max_length=10, null=True)
    spare_database_username = fields.CharField(max_length=100, null=True)
    spare_database_password = fields.CharField(max_length=100, null=True)
    create_time = fields.DatetimeField(null=True, description='创建时间')
    update_time = fields.DatetimeField(null=True, description='修改时间')
    create_user = fields.CharField(max_length=20, null=True, description='创建者')
    update_user = fields.CharField(max_length=20, null=True, description='修改者')

    class Meta:
        table = "t_system_database"


class T_SystemLogSwitch(models.Model):
    """系统日志开关配置"""
    id = fields.CharField(primary_key=True, max_length=64)
    dev_usage_total_switch = fields.BooleanField(null=True, description='设备使用统计总开关') # bit(1)
    stat_usage_enabled = fields.BooleanField(null=True, description='仪器使用率统计开关') # bit(1)
    stat_user_enabled = fields.BooleanField(null=True, description='用户使用率统计开关') # bit(1)
    stat_type_enabled = fields.BooleanField(null=True, description='检测类型分项统计开关') # bit(1)
    stat_item_enabled = fields.BooleanField(null=True, description='检测项目分项统计开关') # bit(1)
    stat_detail_enabled = fields.BooleanField(null=True, description='检测任务详细信息开关') # bit(1)
    dev_usage_record_switch = fields.BooleanField(null=True, description='仪器使用记录开关') # bit(1)
    create_time = fields.DatetimeField(null=True, description='创建时间')
    update_time = fields.DatetimeField(null=True, description='修改时间')
    create_user = fields.CharField(max_length=20, null=True, description='创建者')
    update_user = fields.CharField(max_length=20, null=True, description='修改者')

    class Meta:
        table = "t_system_log_switch"


class T_SystemManage(models.Model):
    id = fields.CharField(primary_key=True, max_length=64)
    language = fields.CharField(max_length=20, null=True, description='语言')
    remote_control = fields.BooleanField(null=True, description='是否允许远程控制') # bit(1)
    remote_control_num = fields.IntField(null=True, description='远程控制数量上限')
    remote_data_access = fields.BooleanField(null=True, description='远程数据访问') # bit(1)
    remote_data_access_num = fields.IntField(null=True, description='远程数据访问用户上限')
    device_use_mode = fields.SmallIntField(null=True, description='仪器使用模式') # tinyint(4)
    device_resource_auto_release_time = fields.IntField(null=True, description='仪器资源自动释放时间(min)')
    create_time = fields.DatetimeField(null=True, description='创建时间')
    update_time = fields.DatetimeField(null=True, description='修改时间')
    create_user = fields.CharField(max_length=20, null=True, description='创建者')
    update_user = fields.CharField(max_length=20, null=True, description='修改者')

    class Meta:
        table = "t_system_manage"


class T_SystemPanelConf(models.Model):
    id = fields.CharField(primary_key=True, max_length=64)
    method_list_switch = fields.BooleanField(null=True, description='方法列表面板开关') # bit(1)
    project_statistics_switch = fields.BooleanField(null=True, description='项目统计面板开关') # bit(1)
    create_time = fields.DatetimeField(null=True, description='创建时间')
    update_time = fields.DatetimeField(null=True, description='修改时间')
    create_user = fields.CharField(max_length=20, null=True, description='创建者')
    update_user = fields.CharField(max_length=20, null=True, description='修改者')

    class Meta:
        table = "t_system_panel_conf"


class T_SystemRole(models.Model):
    """系统角色表"""
    id = fields.CharField(primary_key=True, max_length=64, description='主键id')
    system_role_name = fields.CharField(max_length=20, null=True, description='系统角色名')
    system_role_num = fields.IntField(null=True, description='系统角色序号')
    permission_list = fields.TextField(null=True, description='角色权限')
    create_time = fields.DatetimeField(null=True, description='创建时间')
    update_time = fields.DatetimeField(null=True, description='修改时间')
    create_user = fields.CharField(max_length=20, null=True, description='创建者')
    update_user = fields.CharField(max_length=20, null=True, description='修改者')

    class Meta:
        table = "t_system_role"


class T_SystemUserGroupManage(models.Model):
    """用户组表"""
    id = fields.CharField(primary_key=True, max_length=64, description='主键id')
    group_name = fields.CharField(max_length=255, null=True, description='组名称')
    group_no = fields.CharField(max_length=32, description='组编号')
    group_desc = fields.CharField(max_length=200, null=True, description='组描述')
    system_identity_id = fields.IntField(description='系统身份')
    is_valid = fields.SmallIntField(null=True, description='是否有效') # tinyint(4)
    reason = fields.TextField(null=True, description='操作原因')
    group_permission_list = fields.CharField(max_length=255, null=True, description='系统权限')
    create_time = fields.DatetimeField(null=True, description='创建时间')
    update_time = fields.DatetimeField(null=True, description='修改时间')
    create_user = fields.CharField(max_length=20, null=True, description='创建者')
    update_user = fields.CharField(max_length=20, null=True, description='修改者')

    class Meta:
        table = "t_system_user_group_manage"


class T_SystemUserManage(models.Model):
    """系统用户表"""
    id = fields.CharField(primary_key=True, max_length=64, description='主键id')
    user_name = fields.CharField(max_length=100, unique=True, description='用户名（账号）')
    password = fields.CharField(max_length=50, description='密码')
    token = fields.CharField(max_length=500, null=True, description='记录当前token')
    user_real_name = fields.CharField(max_length=20, null=True, description='真实姓名')
    user_position = fields.CharField(max_length=50, null=True, description='用户职务')
    remark = fields.TextField(null=True, description='备注')
    group_name = fields.CharField(max_length=255, null=True, description='所属组')
    group_no = fields.CharField(max_length=64, null=True, description='组id')
    system_identity_id = fields.CharField(max_length=64, null=True, description='系统身份id')
    logo = fields.CharField(max_length=255, null=True, description='标志')
    phone = fields.CharField(max_length=20, null=True, description='电话')
    email = fields.CharField(max_length=32, null=True, description='邮箱')
    is_valid = fields.SmallIntField(null=True, description='是否有效') # tinyint(4)
    is_login = fields.SmallIntField(null=True, description='是否已登陆') # tinyint(4)
    login_fail_count = fields.IntField(null=True, description='登陆失败次数')
    change_password_time = fields.DatetimeField(null=True, description='修改密码时间')
    reason = fields.TextField(null=True, description='修改密码原因')
    user_permission_list = fields.TextField(null=True, description='用户权限列表')
    create_time = fields.DatetimeField(null=True, description='创建时间')
    update_time = fields.DatetimeField(null=True, description='修改时间')
    create_user = fields.CharField(max_length=20, null=True, description='创建者')
    update_user = fields.CharField(max_length=20, null=True, description='修改者')

    class Meta:
        table = "t_system_user_manage"
        # unique_together = (("user_name",),) # Unique constraint handled by unique=True on field


class T_SystemUserPermission(models.Model):
    """系统权限表"""
    id = fields.CharField(primary_key=True, max_length=64, description='主键id')
    sid = fields.IntField(unique=True, description='权限序号') # AUTO_INCREMENT and UNIQUE KEY sid_index
    permission_name = fields.CharField(max_length=255, null=True, description='权限名称')
    permission_type = fields.CharField(max_length=255, null=True, description='权限类型')
    interface_name = fields.CharField(max_length=64, null=True, description='权限对应的接口名')
    remark = fields.TextField(null=True, description='备注')
    create_time = fields.DatetimeField(null=True, description='创建时间')
    update_time = fields.DatetimeField(null=True, description='修改时间')
    create_user = fields.CharField(max_length=20, null=True, description='创建者')
    update_user = fields.CharField(max_length=20, null=True, description='修改者')

    class Meta:
        table = "t_system_user_permission"
        # unique_together = (("sid",),) # Unique constraint handled by unique=True on field
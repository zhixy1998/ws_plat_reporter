from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS `t_gmp_permission` (
    `id` VARCHAR(64) NOT NULL PRIMARY KEY COMMENT '主键id',
    `device_type_id` INT   COMMENT '仪器类型id',
    `sid` INT   COMMENT '权限序号',
    `permission_name` VARCHAR(255)   COMMENT '权限名称',
    `permission_type` VARCHAR(255)   COMMENT '权限类型',
    `remark` LONGTEXT   COMMENT '备注',
    `create_time` DATETIME(6)   COMMENT '创建时间',
    `update_time` DATETIME(6)   COMMENT '修改时间',
    `create_user` VARCHAR(20)   COMMENT '创建者',
    `update_user` VARCHAR(20)   COMMENT '修改者'
) CHARACTER SET utf8mb4 COMMENT='系统权限表';
        CREATE TABLE IF NOT EXISTS `t_gmp_user_group` (
    `id` VARCHAR(64) NOT NULL PRIMARY KEY COMMENT '主键id',
    `user_type` VARCHAR(255)   COMMENT '组名称',
    `password_valid` INT   COMMENT '密码时效性，0，不设置为0，以天为单位',
    `password_rule` VARCHAR(200)   COMMENT '密码复杂度',
    `login_error_time` INT   COMMENT '登录错误次数',
    `login_error_done` VARCHAR(255)   COMMENT '登陆错误处理',
    `is_valid` SMALLINT   COMMENT '是否有效',
    `remark` LONGTEXT   COMMENT '备注',
    `reason` LONGTEXT   COMMENT '操作原因',
    `system_permission_list` VARCHAR(255)   COMMENT '系统权限',
    `create_time` DATETIME(6)   COMMENT '创建时间',
    `update_time` DATETIME(6)   COMMENT '修改时间',
    `create_user` VARCHAR(20)   COMMENT '创建者',
    `update_user` VARCHAR(20)   COMMENT '修改者'
) CHARACTER SET utf8mb4 COMMENT='用户组表';
        CREATE TABLE IF NOT EXISTS `t_ins_auto_injector` (
    `id` VARCHAR(64) NOT NULL PRIMARY KEY,
    `device_serial_number` VARCHAR(32) NOT NULL COMMENT '仪器序列号',
    `message_port` VARCHAR(10)   COMMENT '通信端口',
    `connect_status` SMALLINT   COMMENT '联机状态',
    `is_start_init` SMALLINT   COMMENT '是否开机对进样器初始化， 0-否，1-是',
    `enter_speed` SMALLINT   COMMENT '进样速度',
    `enter_time` VARCHAR(10)   COMMENT '进样时间',
    `wash_speed` SMALLINT   COMMENT '清洗速度',
    `wash_time` VARCHAR(10)   COMMENT '清洗时间',
    `waiting_time` VARCHAR(10)   COMMENT '停泵等待时间',
    `is_wash_before_enter` SMALLINT   COMMENT '是否进样前清洗，0-否，1，是',
    `create_time` DATETIME(6)   COMMENT '创建时间',
    `update_time` DATETIME(6)   COMMENT '修改时间',
    `create_user` VARCHAR(20)   COMMENT '创建者',
    `update_user` VARCHAR(20)   COMMENT '修改者'
) CHARACTER SET utf8mb4;
        CREATE TABLE IF NOT EXISTS `t_ins_calibration_config` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `calibration_name` VARCHAR(255),
    `calibration_type` INT,
    `device_type` VARCHAR(255)
) CHARACTER SET utf8mb4 COMMENT='校正类型默认表，记录不同仪器所具备的校正类型';
        CREATE TABLE IF NOT EXISTS `t_ins_calibration_param` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `calibration_type` INT,
    `param_name` VARCHAR(64),
    `param` VARCHAR(64),
    `param_type` INT   COMMENT '参数类型，0-固定值，1-输入框，2-下拉框'
) CHARACTER SET utf8mb4 COMMENT='校正类型对应的参数表';
        CREATE TABLE IF NOT EXISTS `t_ins_calibration_temp` (
    `id` VARCHAR(64) NOT NULL PRIMARY KEY,
    `device_serial_number` VARCHAR(64),
    `calibration_type` INT,
    `param` VARCHAR(255),
    `param_value` VARCHAR(255),
    `create_time` DATETIME(6)   COMMENT '创建时间',
    `update_time` DATETIME(6)   COMMENT '修改时间',
    `create_user` VARCHAR(20)   COMMENT '创建者',
    `update_user` VARCHAR(20)   COMMENT '修改者'
) CHARACTER SET utf8mb4 COMMENT='校正参数记录表';
        CREATE TABLE IF NOT EXISTS `t_ins_calibration_value` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `param_id` INT,
    `param_key` VARCHAR(64),
    `param_value` VARCHAR(10)
) CHARACTER SET utf8mb4 COMMENT='参数类型和默认值表';
        CREATE TABLE IF NOT EXISTS `t_ins_config_setting` (
    `id` VARCHAR(64) NOT NULL PRIMARY KEY COMMENT '主键id',
    `device_serial_number` VARCHAR(255),
    `is_time_startup` SMALLINT   COMMENT '是否自动开机',
    `startup_time` VARCHAR(20)   COMMENT '自动开机时间',
    `message_port` SMALLINT   COMMENT '通讯端口',
    `annex_setting` SMALLINT   COMMENT '附件设置',
    `band_width` DOUBLE   COMMENT '光谱带宽',
    `create_time` DATETIME(6)   COMMENT '创建时间',
    `update_time` DATETIME(6)   COMMENT '修改时间',
    `create_user` VARCHAR(20)   COMMENT '创建者',
    `update_user` VARCHAR(20)   COMMENT '修改者'
) CHARACTER SET utf8mb4 COMMENT='仪器系统配置';
        CREATE TABLE IF NOT EXISTS `t_ins_info_temp` (
    `id` VARCHAR(64) NOT NULL PRIMARY KEY,
    `device_serial_number` VARCHAR(64),
    `device_ip` VARCHAR(64),
    `connect_status` SMALLINT,
    `machine_ip` VARCHAR(64),
    `device_port` INT,
    `is_inited` SMALLINT   COMMENT '0：未完成；1：自检成功； 2：自检失败； 3：自检进行中',
    `is_dev_opened` SMALLINT   COMMENT '0-未开机，1-已开机',
    `create_time` DATETIME(6)   COMMENT '创建时间',
    `update_time` DATETIME(6)   COMMENT '修改时间',
    `create_user` VARCHAR(20)   COMMENT '创建者',
    `update_user` VARCHAR(20)   COMMENT '修改者'
) CHARACTER SET utf8mb4 COMMENT='设备信息表';
        CREATE TABLE IF NOT EXISTS `t_ins_init_temp` (
    `id` VARCHAR(64) NOT NULL PRIMARY KEY,
    `device_info_id` VARCHAR(64),
    `device_serial_number` VARCHAR(64)   COMMENT '序列号',
    `init_task_num` INT   COMMENT '初始化条目',
    `init_status` SMALLINT   COMMENT '初始化状态',
    `create_time` DATETIME(6)   COMMENT '创建时间',
    `update_time` DATETIME(6)   COMMENT '修改时间',
    `create_user` VARCHAR(20)   COMMENT '创建者',
    `update_user` VARCHAR(20)   COMMENT '修改者'
) CHARACTER SET utf8mb4 COMMENT='自检任务表';
        CREATE TABLE IF NOT EXISTS `t_int_injection_tray_param` (
    `id` VARCHAR(64) NOT NULL PRIMARY KEY,
    `device_serial_number` VARCHAR(31)   COMMENT '仪器序列号',
    `panel` VARCHAR(10)   COMMENT '盘区设定',
    `is_selected` SMALLINT   COMMENT '是否选中',
    `plate_rail` INT   COMMENT '盘架设定',
    `num_info` VARCHAR(20)   COMMENT '编号信息',
    `create_time` DATETIME(6)   COMMENT '创建时间',
    `update_time` DATETIME(6)   COMMENT '修改时间',
    `create_user` VARCHAR(20)   COMMENT '创建者',
    `update_user` VARCHAR(20)   COMMENT '修改者'
) CHARACTER SET utf8mb4 COMMENT='进样盘参数表';
        CREATE TABLE IF NOT EXISTS `t_measure_analysis_data` (
    `id` VARCHAR(36) NOT NULL PRIMARY KEY COMMENT '分析数据id',
    `analysis_name` VARCHAR(255)   COMMENT '分析名称',
    `task_id` VARCHAR(255)   COMMENT '测量任务id',
    `sample_key` VARCHAR(255)   COMMENT '样品id',
    `analysis_param` LONGTEXT   COMMENT '分析参数',
    `analysis_result` JSON   COMMENT '分析结果',
    `analysis_type` VARCHAR(255)   COMMENT '变换类型',
    `gauge_point` JSON   COMMENT '标记点',
    `peak` JSON   COMMENT '峰',
    `grain` JSON   COMMENT '谷',
    `color` VARCHAR(255)   COMMENT '颜色',
    `analysis_data_image` LONGBLOB   COMMENT '分析数据图像',
    `is_delete` VARCHAR(255)   COMMENT '是否删除(0.正常,1.已删除)'
) CHARACTER SET utf8mb4 COMMENT='分析数据表';
        CREATE TABLE IF NOT EXISTS `t_measure_data` (
    `id` VARCHAR(36) NOT NULL PRIMARY KEY COMMENT '测量数据id',
    `task_id` VARCHAR(255)   COMMENT '测量任务id',
    `sample_key` VARCHAR(255)   COMMENT '样品Key',
    `instrument_data` JSON   COMMENT '仪器数据',
    `original_calculation_data` JSON   COMMENT '原始计算数据',
    `measurement_start_time` DATETIME(6)   COMMENT '测量开始时间',
    `measurement_end_time` DATETIME(6)   COMMENT '测量结束时间',
    `gauge_point` JSON   COMMENT '标记点',
    `peak` JSON   COMMENT '峰',
    `grain` JSON   COMMENT '谷',
    `sampling_time` DATETIME(6)   COMMENT '采样时间',
    `data_image` LONGBLOB   COMMENT '数据图像',
    `remark` VARCHAR(255)   COMMENT '备注',
    `is_delete` VARCHAR(255)   COMMENT '是否删除',
    KEY `idx_t_measure_d_measure_7d7c38` (`measurement_start_time`)
) CHARACTER SET utf8mb4 COMMENT='测量数据表';
        CREATE TABLE IF NOT EXISTS `t_measure_method` (
    `id` VARCHAR(36) NOT NULL PRIMARY KEY COMMENT '方法id',
    `preprocess_key` VARCHAR(768)   COMMENT '前处理Key',
    `multiple_calculation_formula_key` VARCHAR(768)   COMMENT '多个计算公式Key',
    `project_item_key` VARCHAR(255)   COMMENT '所属项目Key(当选用的是公共方法则项目key为空)',
    `method_name` VARCHAR(255)   COMMENT '方法名称',
    `measurement_type` VARCHAR(255)   COMMENT '测量类型',
    `measurement_param_info` JSON   COMMENT '测量参数信息',
    `is_sharing_method` VARCHAR(255)   COMMENT '是否共享方法',
    `method_create_time` DATETIME(6)   COMMENT '方法创建时间',
    `method_creator` VARCHAR(255)   COMMENT '方法创建人',
    `field2` VARCHAR(255)   COMMENT '预留字段2',
    `field3` VARCHAR(255)   COMMENT '预留字段3',
    `field4` VARCHAR(255)   COMMENT '预留字段4',
    `field5` VARCHAR(255)   COMMENT '预留字段5'
) CHARACTER SET utf8mb4 COMMENT='测量方法表';
        CREATE TABLE IF NOT EXISTS `t_measure_project` (
    `id` VARCHAR(36) NOT NULL PRIMARY KEY COMMENT '项目id',
    `project_name` VARCHAR(255)   COMMENT '项目名称',
    `create_time` DATETIME(6)   COMMENT '创建时间',
    `creator_key` VARCHAR(255)   COMMENT '创建人Key',
    `remark` VARCHAR(255)   COMMENT '备注',
    `last_updated_by` VARCHAR(255)   COMMENT '最近更新人',
    `last_updated_time` DATETIME(6)   COMMENT '最近更新时间',
    `field3` VARCHAR(255)   COMMENT '预留字段3',
    `field4` VARCHAR(255)   COMMENT '预留字段4',
    `field5` VARCHAR(255)   COMMENT '预留字段5'
) CHARACTER SET utf8mb4 COMMENT='项目表';
        CREATE TABLE IF NOT EXISTS `t_measure_sample` (
    `id` VARCHAR(36) NOT NULL PRIMARY KEY COMMENT '样品id',
    `sample_number` VARCHAR(255)   COMMENT '样品编号',
    `sample_type` VARCHAR(255)   COMMENT '样品类型(0.空白样品,1.标准样品)',
    `sample_kind` VARCHAR(255)   COMMENT '样品种类(0.标准样品 1.未知样品)',
    `sample_name` VARCHAR(255)   COMMENT '样品名称',
    `dilution_ratio` VARCHAR(255)   COMMENT '稀释倍数',
    `sample_volume` VARCHAR(255)   COMMENT '取样量',
    `constant_volume` VARCHAR(255)   COMMENT '定容体积',
    `normal_concentration` VARCHAR(255)   COMMENT '标准浓度',
    `sample_location` VARCHAR(255)   COMMENT '样品位置',
    `sample_description` LONGTEXT   COMMENT '样品描述',
    `input_data` LONGTEXT   COMMENT '输入数据',
    `color` VARCHAR(255)   COMMENT '颜色'
) CHARACTER SET utf8mb4 COMMENT='样品信息表';
        CREATE TABLE IF NOT EXISTS `t_measure_task` (
    `id` VARCHAR(36) NOT NULL PRIMARY KEY COMMENT '任务id',
    `user_id` VARCHAR(50)   COMMENT '用户id',
    `task_name` VARCHAR(255)   COMMENT '任务名称',
    `create_time` DATETIME(6)   COMMENT '创建时间',
    `collection_start_time` DATETIME(6)   COMMENT '采集起始时间',
    `method_key` VARCHAR(255)   COMMENT '方法Key',
    `sample_key` JSON   COMMENT '样品key',
    `project_item_key` VARCHAR(255)   COMMENT '所属项目Key',
    `start_time` DATETIME(6)   COMMENT '开始时间',
    `end_time` DATETIME(6)   COMMENT '结束时间',
    `device_serial_number` VARCHAR(255)   COMMENT '序列号',
    `is_delete` VARCHAR(255)   COMMENT '是否删除'
) CHARACTER SET utf8mb4 COMMENT='测量任务表';
        CREATE TABLE IF NOT EXISTS `t_report_calculation_formulas` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `detection_id` VARCHAR(50) NOT NULL COMMENT '标准标识',
    `result_identity` VARCHAR(50) NOT NULL COMMENT '结果标识',
    `result_name` VARCHAR(100) NOT NULL COMMENT '结果名称',
    `unit` VARCHAR(20) NOT NULL COMMENT '单位',
    `input_param1_name` VARCHAR(100) NOT NULL COMMENT '输入参数1名称',
    `input_param1_identity` VARCHAR(100) NOT NULL COMMENT '输入参数1标识',
    `input_param2_name` VARCHAR(100)   COMMENT '输入参数2名称',
    `input_param2_identity` VARCHAR(100)   COMMENT '输入参数2标识',
    `input_param3_name` VARCHAR(100)   COMMENT '输入参数3名称',
    `input_param3_identity` VARCHAR(100)   COMMENT '输入参数3标识',
    `input_param4_name` VARCHAR(100)   COMMENT '输入参数4名称',
    `input_param4_identity` VARCHAR(100)   COMMENT '输入参数4标识',
    `input_param5_name` VARCHAR(100)   COMMENT '输入参数5名称',
    `input_param5_identity` VARCHAR(100)   COMMENT '输入参数5标识',
    `input_param6_name` VARCHAR(100)   COMMENT '输入参数6名称',
    `input_param6_identity` VARCHAR(100)   COMMENT '输入参数6标识',
    `input_param7_name` VARCHAR(100)   COMMENT '输入参数7名称',
    `input_param7_identity` VARCHAR(100)   COMMENT '输入参数7标识',
    `input_param8_name` VARCHAR(100)   COMMENT '输入参数8名称',
    `input_param8_identity` VARCHAR(100)   COMMENT '输入参数8标识',
    `input_param9_name` VARCHAR(100)   COMMENT '输入参数9名称',
    `input_param9_identity` VARCHAR(100)   COMMENT '输入参数9标识',
    `input_param10_name` VARCHAR(100)   COMMENT '输入参数10名称',
    `input_param10_identity` VARCHAR(100)   COMMENT '输入参数10标识',
    `formula_text` LONGTEXT   COMMENT '公式文本',
    `formula_image` LONGTEXT   COMMENT '公式图片',
    `detection_limit` VARCHAR(255)   COMMENT '检出限',
    KEY `idx_t_report_ca_detecti_385f81` (`detection_id`)
) CHARACTER SET utf8mb4 COMMENT='计算公式表';
        CREATE TABLE IF NOT EXISTS `t_report_quality_control` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `detection_id` VARCHAR(50) NOT NULL COMMENT '标准标识',
    `control_type` VARCHAR(50)   COMMENT '质控类型',
    `control_description` LONGTEXT   COMMENT '质控描述',
    `control_formula` VARCHAR(255)   COMMENT '质控公式',
    `create_datetime` DATETIME(6) NOT NULL COMMENT '创建时间' DEFAULT CURRENT_TIMESTAMP(6),
    `update_datetime` DATETIME(6) NOT NULL COMMENT '更新时间' DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    KEY `idx_t_report_qu_detecti_94b3e1` (`detection_id`)
) CHARACTER SET utf8mb4 COMMENT='质量控制表';
        CREATE TABLE IF NOT EXISTS `t_report_rounding_rules` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `detection_id` VARCHAR(100) NOT NULL COMMENT '标准标识',
    `result_identity` VARCHAR(50)   COMMENT '结果标识',
    `rounding_type` VARCHAR(50) NOT NULL COMMENT '修约类型',
    `rounding_condition` VARCHAR(100)   COMMENT '修约条件',
    `decimal_places` INT NOT NULL COMMENT '保留小数位数' DEFAULT 0,
    KEY `idx_t_report_ro_detecti_171556` (`detection_id`)
) CHARACTER SET utf8mb4 COMMENT='修约表';
        CREATE TABLE IF NOT EXISTS `t_report_standard_detection` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `standard_identity` VARCHAR(150) NOT NULL COMMENT '标准标识',
    `industry` VARCHAR(50) NOT NULL COMMENT '行业',
    `detection_type` VARCHAR(50) NOT NULL COMMENT '检测类型',
    `detection_instrument` VARCHAR(50) NOT NULL COMMENT '检测仪器',
    `standard_number` VARCHAR(100) NOT NULL COMMENT '标准号',
    `standard_name` VARCHAR(200)   COMMENT '标准名称',
    `detection_item` VARCHAR(50) NOT NULL COMMENT '检测项目',
    `method_number` VARCHAR(20)   COMMENT '第几法',
    `remark` VARCHAR(500)   COMMENT '备注',
    `detection_parameters` LONGTEXT   COMMENT '检测参数',
    `release_date` DATETIME(6)   COMMENT '发布时间',
    `expiration_date` DATETIME(6)   COMMENT '失效时间',
    `effective_date` DATETIME(6)   COMMENT '实施时间',
    `release_status` VARCHAR(200)   COMMENT '状态',
    `industry_type` VARCHAR(50)   COMMENT '类型',
    KEY `idx_t_report_st_standar_c53130` (`standard_identity`)
) CHARACTER SET utf8mb4 COMMENT='标准信息表';
        CREATE TABLE IF NOT EXISTS `t_report_standard_pretreatment` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `detection_id` VARCHAR(100) NOT NULL COMMENT '标准标识id',
    `pretreatment_description` LONGTEXT   COMMENT '前处理描述',
    KEY `idx_t_report_st_detecti_12485a` (`detection_id`)
) CHARACTER SET utf8mb4 COMMENT='标准前处理表';
        CREATE TABLE IF NOT EXISTS `t_report_upgrade_version` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT COMMENT '主键',
    `version` VARCHAR(50) NOT NULL UNIQUE COMMENT '版本号（如v2.1.3）',
    `update_description` LONGTEXT,
    `create_time` DATETIME(6) NOT NULL COMMENT '创建时间' DEFAULT CURRENT_TIMESTAMP(6)
) CHARACTER SET utf8mb4 COMMENT='升级版本记录表';
        CREATE TABLE IF NOT EXISTS `t_sysconfig_user` (
    `id` VARCHAR(64) NOT NULL PRIMARY KEY COMMENT '主键id',
    `user_name` VARCHAR(100) NOT NULL UNIQUE COMMENT '用户名（账号）',
    `password` VARCHAR(50) NOT NULL COMMENT '密码',
    `token` VARCHAR(500)   COMMENT '记录当前token',
    `user_real_name` VARCHAR(20)   COMMENT '真实姓名',
    `user_position` VARCHAR(50)   COMMENT '用户职务',
    `remark` LONGTEXT   COMMENT '备注',
    `group_name` VARCHAR(255)   COMMENT '所属组',
    `group_id` VARCHAR(64)   COMMENT '组id',
    `system_identity_id` VARCHAR(64)   COMMENT '系统身份id',
    `logo` VARCHAR(255)   COMMENT '标志',
    `digital_signature` VARCHAR(255)   COMMENT '电子签名',
    `digital_signature_path` LONGTEXT   COMMENT '电子签名路径',
    `is_valid` SMALLINT   COMMENT '是否有效',
    `is_login` SMALLINT   COMMENT '是否已登陆',
    `login_fail_count` INT   COMMENT '登陆失败次数',
    `change_password_time` DATETIME(6)   COMMENT '修改密码时间',
    `reason` LONGTEXT   COMMENT '修改密码原因',
    `create_time` DATETIME(6)   COMMENT '创建时间',
    `update_time` DATETIME(6)   COMMENT '修改时间',
    `create_user` VARCHAR(20)   COMMENT '创建者',
    `update_user` VARCHAR(20)   COMMENT '修改者'
) CHARACTER SET utf8mb4 COMMENT='系统用户表';
        CREATE TABLE IF NOT EXISTS `t_system_algorithm_conf` (
    `id` VARCHAR(64) NOT NULL PRIMARY KEY,
    `integrating_sphere_k` VARCHAR(20)   COMMENT '透过率门限系数k',
    `transmittance_k` VARCHAR(20)   COMMENT '积分球门限系数k',
    `abs_k` VARCHAR(10)   COMMENT 'Abs门限系数k',
    `create_time` DATETIME(6)   COMMENT '创建时间',
    `update_time` DATETIME(6)   COMMENT '修改时间',
    `create_user` VARCHAR(20)   COMMENT '创建者',
    `update_user` VARCHAR(20)   COMMENT '修改者'
) CHARACTER SET utf8mb4 COMMENT='系统算法配置表';
        CREATE TABLE IF NOT EXISTS `t_system_business_param` (
    `id` VARCHAR(64) NOT NULL PRIMARY KEY,
    `peak_interval` VARCHAR(20)   COMMENT '峰间距',
    `peak_valley_diff` VARCHAR(20)   COMMENT '峰谷差',
    `create_time` DATETIME(6)   COMMENT '创建时间',
    `update_time` DATETIME(6)   COMMENT '修改时间',
    `create_user` VARCHAR(20)   COMMENT '创建者',
    `update_user` VARCHAR(20)   COMMENT '修改者'
) CHARACTER SET utf8mb4;
        CREATE TABLE IF NOT EXISTS `t_system_database` (
    `id` VARCHAR(64) NOT NULL PRIMARY KEY,
    `global_port` VARCHAR(10),
    `fast_login_switch` BOOL   COMMENT '快捷登录开关',
    `main_database_ip` VARCHAR(20),
    `main_database_port` VARCHAR(10),
    `main_database_username` VARCHAR(64),
    `main_database_password` VARCHAR(100),
    `spare_database_ip` VARCHAR(20),
    `spare_database_port` VARCHAR(10),
    `spare_database_username` VARCHAR(100),
    `spare_database_password` VARCHAR(100),
    `create_time` DATETIME(6)   COMMENT '创建时间',
    `update_time` DATETIME(6)   COMMENT '修改时间',
    `create_user` VARCHAR(20)   COMMENT '创建者',
    `update_user` VARCHAR(20)   COMMENT '修改者'
) CHARACTER SET utf8mb4 COMMENT='系统数据库配置';
        CREATE TABLE IF NOT EXISTS `t_system_log_switch` (
    `id` VARCHAR(64) NOT NULL PRIMARY KEY,
    `dev_usage_total_switch` BOOL   COMMENT '设备使用统计总开关',
    `stat_usage_enabled` BOOL   COMMENT '仪器使用率统计开关',
    `stat_user_enabled` BOOL   COMMENT '用户使用率统计开关',
    `stat_type_enabled` BOOL   COMMENT '检测类型分项统计开关',
    `stat_item_enabled` BOOL   COMMENT '检测项目分项统计开关',
    `stat_detail_enabled` BOOL   COMMENT '检测任务详细信息开关',
    `dev_usage_record_switch` BOOL   COMMENT '仪器使用记录开关',
    `create_time` DATETIME(6)   COMMENT '创建时间',
    `update_time` DATETIME(6)   COMMENT '修改时间',
    `create_user` VARCHAR(20)   COMMENT '创建者',
    `update_user` VARCHAR(20)   COMMENT '修改者'
) CHARACTER SET utf8mb4 COMMENT='系统日志开关配置';
        CREATE TABLE IF NOT EXISTS `t_system_manage` (
    `id` VARCHAR(64) NOT NULL PRIMARY KEY,
    `language` VARCHAR(20)   COMMENT '语言',
    `remote_control` BOOL   COMMENT '是否允许远程控制',
    `remote_control_num` INT   COMMENT '远程控制数量上限',
    `remote_data_access` BOOL   COMMENT '远程数据访问',
    `remote_data_access_num` INT   COMMENT '远程数据访问用户上限',
    `device_use_mode` SMALLINT   COMMENT '仪器使用模式',
    `device_resource_auto_release_time` INT   COMMENT '仪器资源自动释放时间(min)',
    `create_time` DATETIME(6)   COMMENT '创建时间',
    `update_time` DATETIME(6)   COMMENT '修改时间',
    `create_user` VARCHAR(20)   COMMENT '创建者',
    `update_user` VARCHAR(20)   COMMENT '修改者'
) CHARACTER SET utf8mb4;
        CREATE TABLE IF NOT EXISTS `t_system_panel_conf` (
    `id` VARCHAR(64) NOT NULL PRIMARY KEY,
    `method_list_switch` BOOL   COMMENT '方法列表面板开关',
    `project_statistics_switch` BOOL   COMMENT '项目统计面板开关',
    `create_time` DATETIME(6)   COMMENT '创建时间',
    `update_time` DATETIME(6)   COMMENT '修改时间',
    `create_user` VARCHAR(20)   COMMENT '创建者',
    `update_user` VARCHAR(20)   COMMENT '修改者'
) CHARACTER SET utf8mb4;
        CREATE TABLE IF NOT EXISTS `t_system_role` (
    `id` VARCHAR(64) NOT NULL PRIMARY KEY COMMENT '主键id',
    `system_role_name` VARCHAR(20)   COMMENT '系统角色名',
    `system_role_num` INT   COMMENT '系统角色序号',
    `permission_list` LONGTEXT   COMMENT '角色权限',
    `create_time` DATETIME(6)   COMMENT '创建时间',
    `update_time` DATETIME(6)   COMMENT '修改时间',
    `create_user` VARCHAR(20)   COMMENT '创建者',
    `update_user` VARCHAR(20)   COMMENT '修改者'
) CHARACTER SET utf8mb4 COMMENT='系统角色表';
        CREATE TABLE IF NOT EXISTS `t_system_user_group_manage` (
    `id` VARCHAR(64) NOT NULL PRIMARY KEY COMMENT '主键id',
    `group_name` VARCHAR(255)   COMMENT '组名称',
    `group_no` VARCHAR(32) NOT NULL COMMENT '组编号',
    `group_desc` VARCHAR(200)   COMMENT '组描述',
    `system_identity_id` INT NOT NULL COMMENT '系统身份',
    `is_valid` SMALLINT   COMMENT '是否有效',
    `reason` LONGTEXT   COMMENT '操作原因',
    `group_permission_list` VARCHAR(255)   COMMENT '系统权限',
    `create_time` DATETIME(6)   COMMENT '创建时间',
    `update_time` DATETIME(6)   COMMENT '修改时间',
    `create_user` VARCHAR(20)   COMMENT '创建者',
    `update_user` VARCHAR(20)   COMMENT '修改者'
) CHARACTER SET utf8mb4 COMMENT='用户组表';
        CREATE TABLE IF NOT EXISTS `t_system_user_manage` (
    `id` VARCHAR(64) NOT NULL PRIMARY KEY COMMENT '主键id',
    `user_name` VARCHAR(100) NOT NULL UNIQUE COMMENT '用户名（账号）',
    `password` VARCHAR(50) NOT NULL COMMENT '密码',
    `token` VARCHAR(500)   COMMENT '记录当前token',
    `user_real_name` VARCHAR(20)   COMMENT '真实姓名',
    `user_position` VARCHAR(50)   COMMENT '用户职务',
    `remark` LONGTEXT   COMMENT '备注',
    `group_name` VARCHAR(255)   COMMENT '所属组',
    `group_no` VARCHAR(64)   COMMENT '组id',
    `system_identity_id` VARCHAR(64)   COMMENT '系统身份id',
    `logo` VARCHAR(255)   COMMENT '标志',
    `phone` VARCHAR(20)   COMMENT '电话',
    `email` VARCHAR(32)   COMMENT '邮箱',
    `is_valid` SMALLINT   COMMENT '是否有效',
    `is_login` SMALLINT   COMMENT '是否已登陆',
    `login_fail_count` INT   COMMENT '登陆失败次数',
    `change_password_time` DATETIME(6)   COMMENT '修改密码时间',
    `reason` LONGTEXT   COMMENT '修改密码原因',
    `user_permission_list` LONGTEXT   COMMENT '用户权限列表',
    `create_time` DATETIME(6)   COMMENT '创建时间',
    `update_time` DATETIME(6)   COMMENT '修改时间',
    `create_user` VARCHAR(20)   COMMENT '创建者',
    `update_user` VARCHAR(20)   COMMENT '修改者'
) CHARACTER SET utf8mb4 COMMENT='系统用户表';
        CREATE TABLE IF NOT EXISTS `t_system_user_permission` (
    `id` VARCHAR(64) NOT NULL PRIMARY KEY COMMENT '主键id',
    `sid` INT NOT NULL UNIQUE COMMENT '权限序号',
    `permission_name` VARCHAR(255)   COMMENT '权限名称',
    `permission_type` VARCHAR(255)   COMMENT '权限类型',
    `interface_name` VARCHAR(64)   COMMENT '权限对应的接口名',
    `remark` LONGTEXT   COMMENT '备注',
    `create_time` DATETIME(6)   COMMENT '创建时间',
    `update_time` DATETIME(6)   COMMENT '修改时间',
    `create_user` VARCHAR(20)   COMMENT '创建者',
    `update_user` VARCHAR(20)   COMMENT '修改者'
) CHARACTER SET utf8mb4 COMMENT='系统权限表';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return
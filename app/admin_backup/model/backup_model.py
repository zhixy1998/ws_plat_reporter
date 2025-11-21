# models_backup.py
from tortoise import fields
from tortoise.models import Model


class FTMeasureAnalysisData(Model):
    __tablename__ = 'f_t_measure_analysis_data'
    __table_args__ = {'comment': '分析数据表'}

    id = fields.CharField(max_length=36, pk=True, default='', description='分析数据id')
    analysis_number = fields.IntField(null=True, description='分析编号')
    analysis_name = fields.CharField(max_length=255, null=True, description='分析名称')
    task_id = fields.CharField(max_length=255, null=True, description='测量任务id')
    sample_key = fields.CharField(max_length=255, null=True, description='样品id')
    measure_data_id = fields.CharField(max_length=255, null=True, description='测量数据id')
    data_version = fields.IntField(null=True, description='版本号')
    analysis_param = fields.JSONField(null=True, description='分析参数')
    analysis_result = fields.JSONField(null=True, description='分析结果')
    analysis_type = fields.CharField(max_length=255, null=True, description='变换类型')
    gauge_point = fields.JSONField(null=True, description='标记点')
    peak = fields.JSONField(null=True, description='峰')
    grain = fields.JSONField(null=True, description='谷')
    color = fields.CharField(max_length=255, null=True, description='颜色')
    analysis_data_image = fields.BinaryField(null=True, description='分析数据图像')
    is_save = fields.CharField(max_length=255, null=True, description='是否保存(0.保存,1.不保存)')
    is_delete = fields.CharField(max_length=255, null=True, description='是否删除(0.正常,1.已删除)')

    class Meta:
        app = "backup"
        table = "f_t_measure_analysis_data"


class FTMeasureAnalysisImage(Model):
    __tablename__ = 'f_t_measure_analysis_image'
    __table_args__ = {'comment': '分析图片表'}

    id = fields.CharField(max_length=255, pk=True, description='图片ID')
    analysis_id = fields.CharField(max_length=255, null=True, description='关联的分析数据ID')
    image_base64 = fields.BinaryField(null=True, description='图片的Base64编码')
    image_name = fields.CharField(max_length=255, null=True, description='图片名称')
    image_type = fields.CharField(max_length=50, null=True, description='图片类型(jpg/png等)')
    create_time = fields.DatetimeField(auto_now_add=True, description='创建时间')
    remarks = fields.CharField(max_length=255, null=True, description='备注信息')

    class Meta:
        app = "backup"
        table = "f_t_measure_analysis_image"


class FTMeasureData(Model):
    __tablename__ = 'f_t_measure_data'
    __table_args__ = {'comment': '测量数据表'}

    id = fields.CharField(max_length=36, pk=True, default='', description='测量数据id')
    task_id = fields.CharField(max_length=255, null=True, description='测量任务id')
    serial_number = fields.IntField(default=0, description='序号')
    sample_key = fields.CharField(max_length=255, null=True, description='样品Key')
    instrument_data = fields.JSONField(null=True, description='仪器数据')
    original_calculation_data = fields.JSONField(null=True, description='原始计算数据')
    measurement_start_time = fields.DatetimeField(null=True, description='测量开始时间')
    measurement_end_time = fields.DatetimeField(null=True, description='测量结束时间')
    gauge_point = fields.JSONField(null=True, description='标记点')
    peak = fields.JSONField(null=True, description='峰')
    grain = fields.JSONField(null=True, description='谷')
    sampling_time = fields.CharField(max_length=64, null=True, description='采样时间')
    data_image = fields.BinaryField(null=True, description='数据图像')
    remark = fields.CharField(max_length=255, null=True, description='备注')
    is_save = fields.CharField(max_length=255, null=True, description='是否保存')
    is_delete = fields.CharField(max_length=255, null=True, description='是否删除')

    class Meta:
        app = "backup"
        table = "f_t_measure_data"


class FTMeasureEqualSample(Model):
    __tablename__ = 'f_t_measure_equal_sample'
    __table_args__ = {'comment': '平行样表'}

    id = fields.BigIntField(pk=True, description='平行样id（自增主键）')
    task_id = fields.CharField(max_length=255, null=True, description='任务id')
    sample_id = fields.JSONField(null=True, description='样品id（JSON类型，存储样品相关信息）')
    create_user = fields.CharField(max_length=100, null=True, description='创建人')
    create_time = fields.DatetimeField(null=True, description='创建时间')
    update_user = fields.CharField(max_length=100, null=True, description='修改人')
    update_time = fields.DatetimeField(null=True, description='更新时间')
    equal_sample_key = fields.CharField(max_length=200, unique=True, description='平行样唯一标识')

    class Meta:
        app = "backup"
        table = "f_t_measure_equal_sample"


class FTMeasureMethod(Model):
    __tablename__ = 'f_t_measure_method'
    __table_args__ = {'comment': '测量方法表'}

    id = fields.CharField(max_length=36, pk=True, default='', description='方法id')
    preprocess_key = fields.CharField(max_length=768, null=True, description='前处理Key')
    multiple_calculation_formula_key = fields.CharField(max_length=768, null=True, description='多个计算公式Key')
    project_item_key = fields.CharField(max_length=255, null=True, description='所属项目Key(当选用的是公共方法则项目key为空)')
    method_name = fields.CharField(max_length=255, null=True, description='方法名称')
    measurement_type = fields.CharField(max_length=255, null=True, description='测量类型')
    measurement_param_info = fields.JSONField(null=True, description='测量参数信息')
    is_sharing_method = fields.CharField(max_length=255, null=True, description='是否共享方法(0.否 1.是)')
    method_create_time = fields.DatetimeField(null=True, description='方法创建时间')
    method_creator = fields.CharField(max_length=255, null=True, description='方法创建人')
    method_use_time = fields.DatetimeField(null=True, description='方法使用时间')
    is_draft = fields.CharField(max_length=255, null=True, description='是否草稿(0.不是草稿 1.是草稿)')
    use_state = fields.CharField(max_length=255, null=True, description='使用状态')
    field5 = fields.CharField(max_length=255, null=True, description='预留字段5')

    class Meta:
        app = "backup"
        table = "f_t_measure_method"


class FTMeasureSample(Model):
    __tablename__ = 'f_t_measure_sample'
    __table_args__ = {'comment': '样品信息表'}

    id = fields.CharField(max_length=36, pk=True, default='', description='样品id')
    sample_number = fields.CharField(max_length=255, null=True, description='样品编号')
    sample_type = fields.CharField(max_length=255, null=True, description='样品类型(0.空白样品,1.标准样品)')
    sample_kind = fields.CharField(max_length=255, null=True, description='样品种类(0.标准样品 1.未知样品)')
    sample_name = fields.CharField(max_length=255, null=True, description='样品名称')
    parallel_group_id = fields.CharField(max_length=255, null=True, description='平行样组id')
    dilution_ratio = fields.CharField(max_length=255, null=True, description='稀释倍数')
    sample_volume = fields.CharField(max_length=255, null=True, description='取样量')
    constant_volume = fields.CharField(max_length=255, null=True, description='定容体积')
    normal_concentration = fields.CharField(max_length=255, null=True, description='标准浓度')
    sample_location = fields.CharField(max_length=255, null=True, description='样品位置')
    sample_description = fields.TextField(null=True, description='样品描述')
    input_data = fields.TextField(null=True, description='输入数据')
    color = fields.CharField(max_length=255, null=True, description='颜色')
    heads = fields.TextField(null=True, description='表头信息')
    new_col_data = fields.TextField(null=True, description='新的列数据')
    data_bulk = fields.BigIntField(null=True, description='数据数量')

    class Meta:
        app = "backup"
        table = "f_t_measure_sample"


class FTMeasureSampleHead(Model):
    __tablename__ = 'f_t_measure_sample_head'
    __table_args__ = {'comment': '样品头信息表'}

    id = fields.CharField(max_length=64, pk=True, description='主键id')
    template_name = fields.CharField(max_length=50, null=True, description='样品模板名称')
    template_desc = fields.CharField(max_length=255, null=True, description='样品模板描述')
    measure_type = fields.CharField(max_length=20, null=True, description='测量类型')
    heads = fields.JSONField(null=True, description='表头信息')
    create_time = fields.DatetimeField(null=True, description='创建时间')
    update_time = fields.DatetimeField(null=True, description='修改时间')
    create_user = fields.CharField(max_length=20, null=True, description='创建者')
    update_user = fields.CharField(max_length=20, null=True, description='修改者')

    class Meta:
        app = "backup"
        table = "f_t_measure_sample_head"


class FTMeasureTask(Model):
    __tablename__ = 'f_t_measure_task'
    __table_args__ = {'comment': '测量任务表'}

    id = fields.CharField(max_length=36, pk=True, default='', description='任务id')
    user_id = fields.CharField(max_length=50, null=True, description='用户id')
    task_name = fields.CharField(max_length=255, null=True, description='任务名称')
    create_time = fields.DatetimeField(null=True, description='创建时间')
    method_key = fields.CharField(max_length=255, null=True, description='方法Key')
    sample_key = fields.JSONField(null=True, description='样品key')
    sample_auto_num = fields.IntField(null=True, description='自动生成样品的序号编号')
    measure_type = fields.CharField(max_length=255, null=True, description='测量类型')
    project_item_key = fields.CharField(max_length=255, null=True, description='所属项目Key')
    zero_param = fields.JSONField(null=True, description='校零参数')
    fitting_param = fields.JSONField(null=True, description='拟合参数')
    table_info = fields.JSONField(null=True, description='表格信息，保护映射信息和样品表头信息')
    end_save_time = fields.DatetimeField(null=True, description='最后保存时间')
    device_serial_number = fields.CharField(max_length=255, null=True, description='序列号')
    image_data = fields.JSONField(null=True, description='图片数据')
    is_save = fields.CharField(max_length=255, null=True, description='是否保存(0.未保存,1.保存)')
    is_delete = fields.CharField(max_length=255, null=True, description='是否删除')

    class Meta:
        app = "backup"
        table = "f_t_measure_task"


class FTMeasureTaskAttachment(Model):
    __tablename__ = 'f_t_measure_task_attachment'
    __table_args__ = {'comment': '任务附属表'}

    id = fields.CharField(max_length=36, pk=True, default='', description='附属id')
    task_id = fields.CharField(max_length=255, null=True, description='任务id')
    data_param = fields.JSONField(null=True, description='数据配置')
    parallel_sample = fields.JSONField(null=True, description='平行样')
    overlap_image = fields.BinaryField(null=True, description='重叠图像')
    tiled_image = fields.BinaryField(null=True, description='平铺图像')
    addr_image = fields.BinaryField(null=True, description='3D图像')

    class Meta:
        app = "backup"
        table = "f_t_measure_task_attachment"
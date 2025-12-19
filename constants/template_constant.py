from .base_constant import StorageInfo, MessageType


class TemplateBookMarkType(StorageInfo):
    text = MessageType(decs='文字', value=0, name='text')
    sheet = MessageType(decs='表格', value=1, name='sheet')
    img = MessageType(decs='图片', value=2, name='img')


class TemplateType(StorageInfo):
    original_records = MessageType(decs='原始数据模版', value=0, name='default')
    report_template = MessageType(decs='报告模版', value=1, name='report_template')
    calibration_template = MessageType(decs='校准模版', value=2, name='calibration_template')
    installation_acceptance_template = MessageType(decs='安装验收模版', value=3, name='installation_acceptance_template')


class ExperimentType(StorageInfo):
    spectral_scanning = MessageType(decs='光谱扫描', value=0, name="spectral_scanning")
    time_scanning = MessageType(decs='时间扫描', value=1, name='time_scanning')
    quantitative_determination = MessageType(decs='定量测定', value=2, name='quantitative_determination')
    photometric_measurement = MessageType(decs='光度测量', value=3, name='photometric_measurement')


class StructureType(StorageInfo):
    Horizontal = MessageType(decs='横向表头', value=0, name='Horizontal')
    Vertical = MessageType(decs='纵向表头', value=1, name='Vertical')



class WordFontType(StorageInfo):
    songti = MessageType(decs="宋体", value="宋体", name="songti")
    fangsong = MessageType(decs="仿宋", value="仿宋_GB2312", name="fangsong")
    heiti = MessageType(decs="黑体", value="黑体", name="heiti")
    kaiti = MessageType(decs="楷体", value="楷体_GB2312", name="kaiti")
    yahei = MessageType(decs="微软雅黑", value="微软雅黑", name="yahei")
    lishu = MessageType(decs="隶书", value="隶书", name="lishu")
    youyuan = MessageType(decs="幼圆", value="幼圆", name="youyuan")
    huazhong = MessageType(decs="华文中宋", value="华文中宋", name="huazhong")
    huafang = MessageType(decs="华文仿宋", value="华文仿宋", name="huafang")
    huakaiti = MessageType(decs="华文楷体", value="华文楷体", name="huakaiti")
    dengxian = MessageType(decs="等线", value="等线", name="dengxian")
    fzshuti = MessageType(decs="方正舒体", value="方正舒体", name="fzshuti")
    fzyaoti = MessageType(decs="方正姚体", value="方正姚体", name="fzyaoti")


class WordFontSize(StorageInfo):
    size2pt = MessageType(decs="2 磅", value=2, name="size2")
    size4pt = MessageType(decs="4 磅", value=4, name="size4")
    size6pt = MessageType(decs="6 磅", value=6, name="size6pt")
    size8pt = MessageType(decs="8 磅", value=8, name="size8pt")
    size10pt = MessageType(decs="10 磅", value=10, name="size10pt")
    size11pt = MessageType(decs="11 磅", value=11, name="size11pt")
    size12pt = MessageType(decs="12 磅", value=12, name="size12pt")
    size14pt = MessageType(decs="14 磅", value=14, name="size14pt")
    size16pt = MessageType(decs="16 磅", value=16, name="size16pt")
    size18pt = MessageType(decs="18 磅", value=18, name="size18pt")
    size20pt = MessageType(decs="20 磅", value=20, name="size20pt")
    size22pt = MessageType(decs="22 磅", value=22, name="size22pt")
    size24pt = MessageType(decs="24 磅", value=24, name="size24pt")
    size26pt = MessageType(decs="26 磅", value=26, name="size26pt")
    size28pt = MessageType(decs="28 磅", value=28, name="size28pt")
    size30pt = MessageType(decs="30 磅", value=30, name="size30pt")
    size32pt = MessageType(decs="32 磅", value=32, name="size32pt")
    size34pt = MessageType(decs="34 磅", value=34, name="size34pt")
    size36pt = MessageType(decs="36 磅", value=36, name="size36pt")
    size38pt = MessageType(decs="38 磅", value=38, name="size38pt")
    size40pt = MessageType(decs="40 磅", value=40, name="size40pt")

class WordImageSizeType(StorageInfo):
    size10cm = MessageType(decs="宽度 10 厘米", value=10.0, name="size10cm")
    size12cm = MessageType(decs="宽度 12 厘米", value=12.0, name="size12cm")
    size14cm = MessageType(decs="宽度 14 厘米", value=14.0, name="size14cm")  # 默认值
    size16cm = MessageType(decs="宽度 16 厘米", value=16.0, name="size16cm")
    size18cm = MessageType(decs="宽度 18 厘米", value=18.0, name="size18cm")
    size20cm = MessageType(decs="宽度 20 厘米", value=20.0, name="size20cm")
    size22cm = MessageType(decs="宽度 22 厘米", value=22.0, name="size22cm")
    size24cm = MessageType(decs="宽度 24 厘米", value=24.0, name="size24cm")
    size26cm = MessageType(decs="宽度 26 厘米", value=26.0, name="size26cm")
    size28cm = MessageType(decs="宽度 28 厘米", value=28.0, name="size28cm")
    size30cm = MessageType(decs="宽度 30 厘米", value=30.0, name="size30cm")
    size32cm = MessageType(decs="宽度 32 厘米", value=32.0, name="size32cm")
    size34cm = MessageType(decs="宽度 34 厘米", value=34.0, name="size34cm")
    size36cm = MessageType(decs="宽度 36 厘米", value=36.0, name="size36cm")
    size38cm = MessageType(decs="宽度 38 厘米", value=38.0, name="size38cm")
    size40cm = MessageType(decs="宽度 40 厘米", value=40.0, name="size40cm")

class GetTypeConstant(StorageInfo):
    common = MessageType(decs='从接口取', value=0, name="default")
    endpoint = MessageType(decs='从接口取', value=1, name="default")
    database = MessageType(decs='从数据库取', value=2, name='database')


class FillTypeConstant(StorageInfo):
    jinja = MessageType(decs='jinja填充', value=0, name="jinja")
    bookmark = MessageType(decs='标签填充', value=1, name="bookmark")


class MeasureType(StorageInfo):
    spectral_scanning = MessageType(decs='光谱扫描', value=0, name="spectral_scanning")
    time_scanning = MessageType(decs='时间扫描', value=1, name='time_scanning')
    quantitative_determination = MessageType(decs='定量测定', value=2, name='quantitative_determination')
    photometric_measurement = MessageType(decs='光度测量', value=3, name='photometric_measurement')


class TemplateOriginType(StorageInfo):
    system_default = MessageType(decs='系统默认模板', value=0, name="system_default")
    user_change = MessageType(decs='用户另存为模板', value=1, name="user_change")
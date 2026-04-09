import os
from .html_report_base import BaseHtmlReportBuilder

class InstallationHtmlBuilder(BaseHtmlReportBuilder):
    """
    专门为“安装验收单”提供数据的Builder。
    继承自BaseHtmlReportBuilder，将后端组织好的表单数据映射给Jinja2。
    """

    def __init__(self, context_data: dict, template_html: str = None, **kwargs):
        """
        Args:
            context_data: view 中组织好的上下文字典，包含诸如 wavelength_mpe_standard 等变量
            template_html: 数据库存储的自定义 HTML，非必需
        """
        super().__init__(template_html=template_html, template_file='installation_acceptance.html')
        self.context_data = context_data or {}

    def _build_context(self) -> dict:
        """
        由于在此场景下，外层(View)已经把数据摊平为了我们直接需要的字段映射，
        所以直接将 None 转换为空字符串并返回给 Jinja2 即可。
        """
        safe_context = {}
        for k, v in self.context_data.items():
            safe_context[k] = v if v is not None else ""
        return safe_context

"""本地验证：向导 HTML 模板渲染 PDF（fake 数据）。

用法（在项目根目录运行）:
    python scripts/one_time/test_guide_html_render.py "模板名" [输出pdf路径]
"""
import sys
import os
import base64
import importlib
import asyncio

sys.path.insert(0, os.getcwd())
sys.path.insert(0, os.path.join(os.getcwd(), 'ws_plat_reporter'))

from jinja2 import Environment
from config import config

TEMPLATE_NAME = sys.argv[1] if len(sys.argv) > 1 else '亚硝酸盐_萘乙二胺分光光度法_原始记录报告模板'
OUT_PDF = sys.argv[2] if len(sys.argv) > 2 else os.path.join(config.deploy_python_path or '.', 'output', 'guide_html_test.pdf')

HTML_DIR = os.path.join(config.deploy_python_path or '.', 'template_structure', 'html_templates')


def load_template_module(name):
    from utils.template_utils import import_template_module
    return import_template_module(config.structure_module, name)


def build_fake_contexts(private_mod):
    contexts = {}
    tm = getattr(private_mod, 'title_mapping', {}) or {}
    for key, info in tm.items():
        if isinstance(info, dict):
            contexts[key] = info.get('name', '')
            if info.get('font_size') and key.endswith('_t'):
                contexts[key[:-2] + '_fs'] = info['font_size']

    # 值字段 fake 填充
    pv = getattr(private_mod, 'python_template_var', {}) or {}
    for key in pv:
        if not key.endswith('_t') and key not in ('table_1_rows', 'known_sample_sub_table'):
            if key in ('a', 'b', 'r'):
                contexts[key] = '0.0123'
            elif key in ('t', 'rh'):
                contexts[key] = '25 / 60%'
            else:
                contexts[key] = '正常' if key == 'sample_status' else '演示数据'

    # 表格
    handler = private_mod.TableDataHandler() if hasattr(private_mod, 'TableDataHandler') else None
    if handler:
        table_map = getattr(handler, 'TABLE_HEADER_MAP', {}) or {}
        for key, name in table_map.items():
            contexts[key] = name
        headers = [table_map.get(f't{i}_h', f't{i}') for i in range(1, 7)]
        contexts['table_1_rows'] = [
            {'t1': 'S-001', 't2': '50', 't3': '0.001', 't4': '0.321', 't5': '0.045', 't6': '0.045'},
            {'t1': 'S-002', 't2': '50', 't3': '0.001', 't4': '0.318', 't5': '0.044', 't6': '0.044'},
            {'t1': 'S-003', 't2': '50', 't3': '0.002', 't4': '0.312', 't5': '0.043', 't6': '0.043'},
        ]
        # 已知样品子表格
        stand = getattr(handler, 'STAND', []) or []
        if stand:
            head = [f'已知样-{i}' for i in range(len(stand))]
            rows = []
            for h in head:
                rows.append([h] + [f'样品{n}' for n in range(1, 6)])
            td_style = 'border:1px solid #000;padding:1px 3px;text-align:center;'
            cells = ''.join(
                '<tr>' + ''.join(f'<td style="{td_style}">{c}</td>' for c in r) + '</tr>'
                for r in rows
            )
            contexts['known_sample_sub_table'] = f'<table style="width:100%;border-collapse:collapse;">{cells}</table>'

    contexts['__title_list__'] = [
        {'name': '报告名称', 'value': '紫外/可见分光光度法测定原始记录', 'font': '黑体', 'font_size': 15},
        {'name': '报告名称', 'value': '紫外/可见分光光度法测定原始记录--附页', 'font': '黑体', 'font_size': 15},
    ]
    return contexts


async def main():
    private_mod = load_template_module(TEMPLATE_NAME)
    contexts = build_fake_contexts(private_mod)

    html_path = os.path.join(HTML_DIR, f'{TEMPLATE_NAME}.html')
    with open(html_path, encoding='utf-8') as f:
        html_tpl = f.read()

    env = Environment()
    rendered = env.from_string(html_tpl).render(**contexts)
    print(f'HTML 渲染完成，长度: {len(rendered)}')

    from utils.classic_html_builder import _html_to_pdf
    pdf_bytes = _html_to_pdf(rendered)
    os.makedirs(os.path.dirname(OUT_PDF), exist_ok=True)
    with open(OUT_PDF, 'wb') as f:
        f.write(pdf_bytes)
    print(f'PDF 已生成: {OUT_PDF} ({len(pdf_bytes)} bytes)')


if __name__ == '__main__':
    asyncio.run(main())

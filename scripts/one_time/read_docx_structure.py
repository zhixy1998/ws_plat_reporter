"""一次性脚本：解析 DOCX 的段落与表格结构，用于向导模板 HTML 化。"""
import sys
from docx import Document
from docx.table import Table
from docx.text.paragraph import Paragraph


def iter_block_items(parent):
    for child in parent.element.body.iterchildren():
        if child.tag.endswith('}p'):
            yield Paragraph(child, parent)
        elif child.tag.endswith('}tbl'):
            yield Table(child, parent)


def main(path):
    doc = Document(path)
    for block in iter_block_items(doc):
        if isinstance(block, Paragraph):
            txt = block.text
            style = block.style.name if block.style else ''
            align = block.alignment
            print(f"[P|{style}|{align}] {txt!r}")
        else:
            print(f"[TABLE rows={len(block.rows)} cols={len(block.columns)}]")
            for ri, row in enumerate(block.rows):
                cells = [c.text for c in row.cells]
                print(f"  row{ri}: {cells}")
            # 合并单元格信息
            print(f"  merged:")
            seen = set()
            for ri, row in enumerate(block.rows):
                for ci, cell in enumerate(row.cells):
                    tc = cell._tc
                    grid_span = tc.find('.//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}gridSpan')
                    vmerge = tc.find('.//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}vMerge')
                    if grid_span is not None or vmerge is not None:
                        gs = grid_span.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val') if grid_span is not None else '-'
                        vm = vmerge.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val') if vmerge is not None else 'continue'
                        print(f"    r{ri}c{ci}: gridSpan={gs} vMerge={vm} text={cell.text[:30]!r}")


if __name__ == '__main__':
    main(sys.argv[1])

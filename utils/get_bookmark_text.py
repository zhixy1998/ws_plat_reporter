from docx import Document

def get_bookmark_text(doc: Document, bookmark_name: str) -> str:
    ns_uri = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
    bookmark_starts = doc.part._element.xpath('.//*[local-name()="bookmarkStart"]')
    start_bm = None
    bm_id = None
    for bm in bookmark_starts:
        if bm.get(f"{{{ns_uri}}}name") == bookmark_name:
            start_bm = bm
            bm_id = bm.get(f"{{{ns_uri}}}id")
            break
    if not bm_id:
        print(f"❌ 没找到书签 {bookmark_name}")
        return ""

    bookmark_ends = doc.part._element.xpath('.//*[local-name()="bookmarkEnd"]')
    end_bm = None
    for bm in bookmark_ends:
        if bm.get(f"{{{ns_uri}}}id") == bm_id:
            end_bm = bm
            break
    else:
        print(f"❌ 没找到书签 {bookmark_name} 的结束标签")
        return ""

    texts = []
    elem = start_bm.getnext()  # 这里用 start_bm，不是 bm
    while elem is not None and elem != end_bm:
        if elem.tag.endswith("r"):  # run 标签
            text_elems = elem.findall(".//w:t", namespaces={"w": ns_uri})
            for t in text_elems:
                if t.text:
                    texts.append(t.text)
        elem = elem.getnext()

    return "".join(texts)

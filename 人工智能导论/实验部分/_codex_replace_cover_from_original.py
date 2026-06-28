from copy import deepcopy
from pathlib import Path

from docx import Document
from docx.oxml.ns import qn


ROOT = Path(__file__).resolve().parent
DST = ROOT / "人工智能导论实验报告_任务2任务3_统一字体.docx"
SRC = ROOT / "人工智能导论实验报告_任务2任务3.docx"


def paragraph_text(element):
    texts = []
    for node in element.iter():
        if node.tag == qn("w:t") and node.text:
            texts.append(node.text)
    return "".join(texts)


def is_toc_heading(element):
    text = paragraph_text(element).replace(" ", "")
    return text == "目录"


def body_children(doc):
    return list(doc._element.body)


src_doc = Document(str(SRC))
dst_doc = Document(str(DST))

src_cover_elements = []
for element in body_children(src_doc):
    if element.tag == qn("w:sectPr"):
        continue
    if is_toc_heading(element):
        break
    src_cover_elements.append(deepcopy(element))

dst_body = dst_doc._element.body
dst_children = body_children(dst_doc)
dst_toc = None
for element in dst_children:
    if is_toc_heading(element):
        dst_toc = element
        break

if dst_toc is None:
    raise RuntimeError("Could not locate current table-of-contents heading.")

for element in list(dst_body):
    if element is dst_toc:
        break
    if element.tag != qn("w:sectPr"):
        dst_body.remove(element)

for element in reversed(src_cover_elements):
    dst_toc.addprevious(element)

dst_doc.save(str(DST))
print(DST)

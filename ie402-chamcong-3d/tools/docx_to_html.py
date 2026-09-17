# -*- coding: utf-8 -*-
"""
Chuyển CHECKPOINT1-*.docx sang HTML để dán vào Google Docs (giữ heading, bảng, ảnh).

    python tools/docx_to_html.py
"""
import base64
import html
import os

import docx
from docx.oxml.ns import qn
from docx.table import Table
from docx.text.paragraph import Paragraph

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "CHECKPOINT1-Cham-cong-dinh-vi-3D.docx")
OUT = os.path.join(ROOT, "scratch", "checkpoint1.html")

FONT = "font-family:Times New Roman,serif"   # khong dat nhay: Google Docs bo qua khi co nhay

d = docx.Document(SRC)


def runs_html(p):
    out = []
    for r in p.runs:
        t = html.escape(r.text)
        if not t:
            continue
        if r.bold:
            t = "<b>%s</b>" % t
        if r.italic:
            t = "<i>%s</i>" % t
        out.append(t)
    return "".join(out)


def images_in(p):
    """Trả về các thẻ <img> base64 cho ảnh nhúng trong đoạn."""
    tags = []
    for blip in p._p.findall(".//" + qn("a:blip")):
        rid = blip.get(qn("r:embed"))
        if not rid:
            continue
        part = d.part.related_parts.get(rid)
        if part is None:
            continue
        b64 = base64.b64encode(part.blob).decode("ascii")
        ctype = part.content_type or "image/png"
        tags.append('<img src="data:%s;base64,%s" style="max-width:640px"/>' % (ctype, b64))
    return tags


def para_html(p):
    imgs = images_in(p)
    if imgs:
        return '<p style="text-align:center">%s</p>' % "".join(imgs)

    txt = runs_html(p).replace("	", "&nbsp;&nbsp;&nbsp;")
    style = (p.style.name or "").lower()

    if not txt.strip():
        return "<p><br/></p>"
    if style.startswith("heading 1"):
        return '<h1 style="%s;font-size:14pt">%s</h1>' % (FONT, txt)
    if style.startswith("heading 2"):
        return '<h2 style="%s;font-size:13pt">%s</h2>' % (FONT, txt)
    if style.startswith("heading 3"):
        return '<h3 style="%s;font-size:13pt">%s</h3>' % (FONT, txt)
    if style.startswith("list bullet") or style.startswith("list paragraph"):
        return '<ul><li style="%s;font-size:13pt">%s</li></ul>' % (FONT, txt)

    css = [FONT, "font-size:13pt"]
    if p.alignment is not None and "CENTER" in str(p.alignment):
        css.append("text-align:center")
    elif p.alignment is not None and "JUSTIFY" in str(p.alignment):
        css.append("text-align:justify")
    fi = p.paragraph_format.first_line_indent
    if fi is not None and fi.inches > 0:
        css.append("text-indent:%.2fin" % fi.inches)
    mono = any(r.font.name == "Consolas" for r in p.runs if r.text.strip())
    if mono:
        return ('<p style="font-family:Courier New,monospace;font-size:10pt;margin:0">'
                "%s</p>" % txt.replace(" ", "&nbsp;"))
    return '<p style="%s">%s</p>' % (";".join(css), txt)


def table_html(t):
    rows = []
    for ri, row in enumerate(t.rows):
        cells = []
        for cell in row.cells:
            inner = "".join(para_html(p) for p in cell.paragraphs)
            tag = "th" if ri == 0 else "td"
            cells.append('<%s style="border:1px solid #999;padding:4px;'
                         'vertical-align:top;%s;font-size:11pt">%s</%s>'
                         % (tag, FONT, inner, tag))
        rows.append("<tr>%s</tr>" % "".join(cells))
    return ('<table style="border-collapse:collapse;width:100%%">%s</table>'
            % "".join(rows))


parts = []
bodies = d.element.body
for child in bodies:
    if child.tag == qn("w:p"):
        parts.append(para_html(Paragraph(child, d)))
    elif child.tag == qn("w:tbl"):
        parts.append(table_html(Table(child, d)))

doc_html = (
    '<!DOCTYPE html><html><head><meta charset="utf-8"><title>Checkpoint 1</title>'
    '<style>body{font-family:"Times New Roman",serif;font-size:13pt;line-height:1.4;'
    'max-width:800px;margin:20px auto}h1{font-size:16pt}h2{font-size:14pt}h3{font-size:13pt}'
    'td,th{font-size:11pt}</style></head><body>'
    + "".join(parts) +
    "</body></html>")

os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w", encoding="utf-8") as f:
    f.write(doc_html)

print("DONE ->", OUT)
print("size KB:", round(os.path.getsize(OUT) / 1024))

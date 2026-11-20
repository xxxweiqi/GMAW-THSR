#!/usr/bin/env python3
"""Build the Chinese experiment plan as a styled, editable Word document.

Run from the package root after installing requirements-docs.txt.
PDF rendering is a separate operation, so the DOCX remains portable.
"""
from pathlib import Path
import argparse
import re
from docx import Document
from docx.shared import Cm, Pt, RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH


def cjk_font(obj, name="Noto Sans CJK SC", size=None, bold=None):
    obj.font.name = "Calibri"
    if size is not None:
        obj.font.size = Pt(size)
    if bold is not None:
        obj.font.bold = bold
    obj.font.color.rgb = RGBColor(0, 0, 0)
    element = obj.element
    rpr = element.get_or_add_rPr()
    fonts = rpr.find(qn("w:rFonts"))
    if fonts is None:
        fonts = OxmlElement("w:rFonts")
        rpr.insert(0, fonts)
    fonts.set(qn("w:eastAsia"), name)


def text_runs(paragraph, text, size=None):
    # Preserve literal code and emphasis without displaying Markdown markup.
    for fragment in re.split(r"(`[^`]+`|\*\*[^*]+\*\*)", text):
        if not fragment:
            continue
        code = fragment.startswith("`") and fragment.endswith("`")
        bold = fragment.startswith("**") and fragment.endswith("**")
        value = fragment[1:-1] if code else fragment[2:-2] if bold else fragment
        run = paragraph.add_run(value)
        cjk_font(run, size=size, bold=True if bold else None)
        if code:
            run.font.name = "DejaVu Sans Mono"
            if size is None:
                run.font.size = Pt(9)


def shade(cell, fill="F2F2F2"):
    tcpr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), fill)
    tcpr.append(shd)


def add_table(document, rows):
    cols = len(rows[0])
    table = document.add_table(rows=1, cols=cols)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    widths = {3: [3.9, 5.2, 7.5], 6: [2.5, 3.3, 1.3, 1.6, 1.6, 6.3]}.get(cols, [16.6 / cols] * cols)
    for i, width in enumerate(widths):
        table.columns[i].width = Cm(width)
    for r_index, row in enumerate(rows):
        cells = table.rows[0].cells if r_index == 0 else table.add_row().cells
        trpr = table.rows[r_index]._tr.get_or_add_trPr()
        no_split = OxmlElement("w:cantSplit")
        trpr.append(no_split)
        if r_index == 0:
            repeat = OxmlElement("w:tblHeader")
            trpr.append(repeat)
        for i, value in enumerate(row):
            cells[i].width = Cm(widths[i])
            cells[i].vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            tcpr = cells[i]._tc.get_or_add_tcPr()
            margin = OxmlElement("w:tcMar")
            for side in ("top", "left", "bottom", "right"):
                el = OxmlElement("w:" + side)
                el.set(qn("w:w"), "80")
                el.set(qn("w:type"), "dxa")
                margin.append(el)
            tcpr.append(margin)
            p = cells[i].paragraphs[0]
            p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.line_spacing = 1.08
            text_runs(p, value, size=9.5)
            if r_index == 0:
                shade(cells[i])
                for run in p.runs:
                    run.bold = True
    borders = OxmlElement("w:tblBorders")
    for name in ("top", "left", "bottom", "right", "insideH", "insideV"):
        e = OxmlElement("w:" + name)
        e.set(qn("w:val"), "single")
        e.set(qn("w:sz"), "4")
        e.set(qn("w:color"), "C8CDD2")
        borders.append(e)
    table._tbl.tblPr.append(borders)
    document.add_paragraph().paragraph_format.space_after = Pt(0)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", default="docs/experiment_plan_zh.md")
    parser.add_argument("--output", default="docs/GMAW_Experiment_Plan_v1.docx")
    args = parser.parse_args()
    doc = Document()
    section = doc.sections[0]
    section.page_width, section.page_height = Cm(21), Cm(29.7)
    section.top_margin, section.bottom_margin = Cm(1.8), Cm(1.8)
    section.left_margin, section.right_margin = Cm(2.2), Cm(2.2)
    section.footer_distance = Cm(.9)
    normal = doc.styles["Normal"]
    cjk_font(normal, size=10.5)
    normal.paragraph_format.space_after = Pt(6)
    normal.paragraph_format.line_spacing = 1.17
    normal.paragraph_format.widow_control = True
    for name, size in (("Title", 24), ("Subtitle", 12), ("Heading 1", 15), ("Heading 2", 12)):
        style = doc.styles[name]
        cjk_font(style, size=size, bold=name.startswith("Heading"))
        style.paragraph_format.space_before = Pt(13 if name.startswith("Heading") else 0)
        style.paragraph_format.space_after = Pt(7)
        style.paragraph_format.keep_with_next = True
        pr = style.element.find(qn("w:pPr"))
        if pr is not None:
            for e in list(pr.findall(qn("w:pBdr"))):
                pr.remove(e)
    doc.core_properties.title = "热历史与时空配准约束的GMAW多模态缺陷事件识别实验方案"
    doc.core_properties.subject = "可执行实验协议与研究参考实现"
    doc.core_properties.author = ""
    doc.core_properties.keywords = "GMAW, thermal history, alignment, defect event"
    p = doc.add_paragraph(style="Title")
    text_runs(p, "热历史与时空配准约束的\nGMAW多模态缺陷事件识别")
    p = doc.add_paragraph(style="Subtitle")
    text_runs(p, "详细实验方案与代码实施说明")
    p = doc.add_paragraph()
    text_runs(p, "版本 1.0    2026年11月18日    当前主任务 Normal 与 Undercut 二分类", size=9.5)
    p = doc.add_paragraph()
    text_runs(p, "本方案以独立焊缝上的缺陷事件为评价单位，把过程历史、可观察的熔池响应与焊后缺陷区间连接起来。优先完成时间空间校准与事件台账，再比较普通历史、热记忆、物理对齐及几何辅助监督，最后执行冻结测试和补充验证。")
    lines = Path(args.source).read_text(encoding="utf-8").splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line or line.startswith("# "):
            i += 1
            continue
        if line.startswith("## "):
            title = re.sub(r"^(\d+)\.\s*", r"\1 ", line[3:])
            title = title.replace("、", " ").replace("，", " ")
            p = doc.add_paragraph(style="Heading 1")
            text_runs(p, title)
        elif line.startswith("### "):
            p = doc.add_paragraph(style="Heading 2")
            text_runs(p, line[4:])
        elif line.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                items = [x.strip() for x in lines[i].strip().strip("|").split("|")]
                if not all(re.fullmatch(r":?-+:?", x.replace(" ", "")) for x in items):
                    rows.append(items)
                i += 1
            add_table(doc, rows)
            continue
        else:
            p = doc.add_paragraph()
            if re.match(r"\[\d+\]", line):
                p.paragraph_format.space_after = Pt(8)
                text_runs(p, line, size=9)
            else:
                text_runs(p, line)
        i += 1
    footer = section.footer.paragraphs[0]
    footer.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    run = footer.add_run("GMAW 实验方案  |  ")
    cjk_font(run, size=8)
    field = OxmlElement("w:fldSimple")
    field.set(qn("w:instr"), "PAGE")
    footer._p.append(field)
    target = Path(args.output)
    target.parent.mkdir(parents=True, exist_ok=True)
    doc.save(target)
    print(target)


if __name__ == "__main__":
    main()

from __future__ import annotations

import re
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Image,
    KeepTogether,
    ListFlowable,
    ListItem,
    PageBreak,
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs" / "relatorio_final.md"
OUTPUT = ROOT / "output" / "pdf" / "relatorio_final_revisao.pdf"


def register_fonts() -> tuple[str, str, str]:
    candidates = [
        (
            Path("C:/Windows/Fonts/arial.ttf"),
            Path("C:/Windows/Fonts/arialbd.ttf"),
            Path("C:/Windows/Fonts/consola.ttf"),
        ),
        (
            Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
            Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
            Path("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"),
        ),
    ]
    for regular, bold, mono in candidates:
        if regular.is_file() and bold.is_file() and mono.is_file():
            pdfmetrics.registerFont(TTFont("ReportRegular", str(regular)))
            pdfmetrics.registerFont(TTFont("ReportBold", str(bold)))
            pdfmetrics.registerFont(TTFont("ReportMono", str(mono)))
            return "ReportRegular", "ReportBold", "ReportMono"
    return "Helvetica", "Helvetica-Bold", "Courier"


REGULAR, BOLD, MONO = register_fonts()


def inline_markup(text: str) -> str:
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    text = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"`([^`]+)`", r'<font name="ReportMono">\1</font>', text)
    text = re.sub(r"\[([^]]+)\]\((https?://[^)]+)\)", r'<link href="\2" color="#1F4E79">\1</link>', text)
    text = re.sub(r"&lt;(https?://[^&]+)&gt;", r'<link href="\1" color="#1F4E79">\1</link>', text)
    text = text.replace("  ", "<br/>")
    return text


def make_styles():
    base = getSampleStyleSheet()
    return {
        "body": ParagraphStyle(
            "Body",
            parent=base["BodyText"],
            fontName=REGULAR,
            fontSize=9.4,
            leading=13.2,
            alignment=TA_JUSTIFY,
            spaceAfter=6,
            textColor=colors.HexColor("#202020"),
        ),
        "h1": ParagraphStyle(
            "H1",
            parent=base["Heading1"],
            fontName=BOLD,
            fontSize=17,
            leading=21,
            textColor=colors.HexColor("#163A5F"),
            spaceBefore=13,
            spaceAfter=8,
        ),
        "h2": ParagraphStyle(
            "H2",
            parent=base["Heading2"],
            fontName=BOLD,
            fontSize=13,
            leading=16,
            textColor=colors.HexColor("#1F4E79"),
            spaceBefore=11,
            spaceAfter=6,
        ),
        "h3": ParagraphStyle(
            "H3",
            parent=base["Heading3"],
            fontName=BOLD,
            fontSize=10.5,
            leading=13,
            textColor=colors.HexColor("#2F5D7C"),
            spaceBefore=8,
            spaceAfter=4,
        ),
        "caption": ParagraphStyle(
            "Caption",
            parent=base["BodyText"],
            fontName=REGULAR,
            fontSize=8,
            leading=10,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#555555"),
            spaceAfter=8,
        ),
        "note": ParagraphStyle(
            "Note",
            parent=base["BodyText"],
            fontName=REGULAR,
            fontSize=9,
            leading=12,
            leftIndent=10,
            rightIndent=10,
            borderColor=colors.HexColor("#D9E6F2"),
            borderWidth=0.8,
            borderPadding=7,
            backColor=colors.HexColor("#F5F9FC"),
            spaceAfter=8,
        ),
        "code": ParagraphStyle(
            "Code",
            fontName=MONO,
            fontSize=7.2,
            leading=9.2,
            leftIndent=8,
            rightIndent=8,
            borderColor=colors.HexColor("#D0D0D0"),
            borderWidth=0.5,
            borderPadding=6,
            backColor=colors.HexColor("#F7F7F7"),
            spaceAfter=8,
        ),
    }


STYLES = make_styles()


def page_chrome(canvas, document):
    canvas.saveState()
    width, height = A4
    if document.page > 1:
        canvas.setStrokeColor(colors.HexColor("#D8E0E8"))
        canvas.line(2 * cm, height - 1.45 * cm, width - 2 * cm, height - 1.45 * cm)
        canvas.setFont(REGULAR, 7.5)
        canvas.setFillColor(colors.HexColor("#52606D"))
        canvas.drawString(2 * cm, height - 1.15 * cm, "ISI — Trabalho Prático 1")
        canvas.drawRightString(width - 2 * cm, 1.15 * cm, f"Página {document.page}")
    canvas.restoreState()


def cover_story():
    return [
        Spacer(1, 2.1 * cm),
        Paragraph("INSTITUTO POLITÉCNICO DO CÁVADO E DO AVE", ParagraphStyle("CoverTop", fontName=BOLD, fontSize=13, leading=17, alignment=TA_CENTER, textColor=colors.HexColor("#1F4E79"))),
        Spacer(1, 0.3 * cm),
        Paragraph("Escola Superior de Tecnologia", ParagraphStyle("CoverSub", fontName=REGULAR, fontSize=11, leading=14, alignment=TA_CENTER)),
        Paragraph("Licenciatura em Engenharia de Sistemas Informáticos", ParagraphStyle("CoverSub2", fontName=REGULAR, fontSize=11, leading=14, alignment=TA_CENTER)),
        Spacer(1, 2.6 * cm),
        Paragraph("TRABALHO PRÁTICO 1", ParagraphStyle("CoverKicker", fontName=BOLD, fontSize=14, leading=18, alignment=TA_CENTER, textColor=colors.HexColor("#56748C"))),
        Spacer(1, 0.5 * cm),
        Paragraph("Pipeline ETL para análise de performance e campanhas de segurança da gama BMW M", ParagraphStyle("CoverTitle", fontName=BOLD, fontSize=23, leading=29, alignment=TA_CENTER, textColor=colors.HexColor("#163A5F"))),
        Spacer(1, 2.2 * cm),
        Table(
            [
                ["Autor", "Gonçalo Correia — n.º 22840"],
                ["Unidade curricular", "Integração de Sistemas de Informação"],
                ["Ano letivo", "2026/2027"],
                ["Data", "Outubro de 2026"],
            ],
            colWidths=[4.2 * cm, 9.5 * cm],
            style=TableStyle([
                ("FONTNAME", (0, 0), (0, -1), BOLD),
                ("FONTNAME", (1, 0), (1, -1), REGULAR),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#1F4E79")),
                ("LINEBELOW", (0, 0), (-1, -1), 0.35, colors.HexColor("#D8E0E8")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ]),
        ),
        Spacer(1, 2.5 * cm),
        Paragraph("Relatório técnico revisto", ParagraphStyle("CoverFoot", fontName=REGULAR, fontSize=10, alignment=TA_CENTER, textColor=colors.HexColor("#52606D"))),
        PageBreak(),
    ]


def add_table(story, rows):
    if not rows:
        return
    parsed = [[cell.strip() for cell in row.strip().strip("|").split("|")] for row in rows if not re.match(r"^\s*\|?\s*:?-+", row)]
    if not parsed:
        return
    columns = max(len(row) for row in parsed)
    for row in parsed:
        row.extend([""] * (columns - len(row)))
    data = [[Paragraph(inline_markup(cell), STYLES["body"]) for cell in row] for row in parsed]
    usable = A4[0] - 4 * cm
    table = Table(data, colWidths=[usable / columns] * columns, repeatRows=1, hAlign="LEFT")
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#DCEAF4")),
        ("FONTNAME", (0, 0), (-1, 0), BOLD),
        ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#AAB8C2")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    story.extend([table, Spacer(1, 7)])


def markdown_story():
    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    start = next(i for i, line in enumerate(lines) if line.startswith("## Resumo"))
    lines = lines[start:]
    story = cover_story()
    paragraph = []
    bullets = []
    table_rows = []
    code_lines = []
    in_code = False

    def flush_paragraph():
        nonlocal paragraph
        if paragraph:
            story.append(Paragraph(inline_markup(" ".join(part.strip() for part in paragraph)), STYLES["body"]))
            paragraph = []

    def flush_bullets():
        nonlocal bullets
        if bullets:
            items = [ListItem(Paragraph(inline_markup(item), STYLES["body"]), leftIndent=11) for item in bullets]
            story.append(ListFlowable(items, bulletType="bullet", start="circle", leftIndent=19, bulletFontName=REGULAR, bulletFontSize=6))
            story.append(Spacer(1, 4))
            bullets = []

    def flush_table():
        nonlocal table_rows
        if table_rows:
            add_table(story, table_rows)
            table_rows = []

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("```"):
            flush_paragraph(); flush_bullets(); flush_table()
            if in_code:
                story.append(Preformatted("\n".join(code_lines), STYLES["code"]))
                code_lines = []
                in_code = False
            else:
                in_code = True
            continue
        if in_code:
            code_lines.append(line)
            continue
        if stripped.startswith("| ") or (stripped.startswith("|") and stripped.endswith("|")):
            flush_paragraph(); flush_bullets(); table_rows.append(stripped); continue
        flush_table()
        image_match = re.match(r"!\[([^]]*)\]\(([^)]+)\)", stripped)
        if image_match:
            flush_paragraph(); flush_bullets()
            path = (SOURCE.parent / image_match.group(2)).resolve()
            if path.is_file():
                img = Image(str(path))
                max_width, max_height = A4[0] - 4.2 * cm, 11.5 * cm
                scale = min(max_width / img.imageWidth, max_height / img.imageHeight, 1)
                img.drawWidth = img.imageWidth * scale
                img.drawHeight = img.imageHeight * scale
                img.hAlign = "CENTER"
                story.append(img)
                story.append(Spacer(1, 4))
            continue
        if stripped.startswith("*") and stripped.endswith("*") and not stripped.startswith("**"):
            flush_paragraph(); flush_bullets()
            story.append(Paragraph(inline_markup(stripped.strip("*")), STYLES["caption"]))
            continue
        if stripped.startswith("### "):
            flush_paragraph(); flush_bullets()
            story.append(Paragraph(inline_markup(stripped[4:]), STYLES["h3"]))
            continue
        if stripped.startswith("## "):
            flush_paragraph(); flush_bullets()
            story.append(Paragraph(inline_markup(stripped[3:]), STYLES["h1"]))
            continue
        if stripped.startswith("# "):
            flush_paragraph(); flush_bullets()
            story.append(Paragraph(inline_markup(stripped[2:]), STYLES["h1"]))
            continue
        if stripped.startswith("> "):
            flush_paragraph(); flush_bullets()
            story.append(Paragraph(inline_markup(stripped[2:]), STYLES["note"]))
            continue
        if re.match(r"^-\s+", stripped):
            flush_paragraph(); bullets.append(re.sub(r"^-\s+", "", stripped)); continue
        numbered = re.match(r"^\d+\.\s+(.*)", stripped)
        if numbered:
            flush_paragraph(); bullets.append(numbered.group(1)); continue
        if stripped in {"", "---"}:
            flush_paragraph(); flush_bullets(); continue
        paragraph.append(stripped)

    flush_paragraph(); flush_bullets(); flush_table()
    return story


def main():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    document = SimpleDocTemplate(
        str(OUTPUT),
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=1.8 * cm,
        bottomMargin=1.7 * cm,
        title="Pipeline ETL para análise de performance e campanhas de segurança da gama BMW M",
        author="Gonçalo Correia",
        subject="Trabalho Prático 1 — Integração de Sistemas de Informação",
    )
    document.build(markdown_story(), onFirstPage=page_chrome, onLaterPages=page_chrome)
    print(OUTPUT)


if __name__ == "__main__":
    main()

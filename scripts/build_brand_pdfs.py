#!/usr/bin/env python3
"""Build the Sosa Tech brand manual and quick-reference PDFs."""

from __future__ import annotations

import html
import re
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import LETTER, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    HRFlowable,
    Image,
    KeepTogether,
    ListFlowable,
    ListItem,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "brand" / "BRAND_GUIDELINES.md"
OUTPUT = ROOT / "output" / "pdf"
LOGO = ROOT / "assets" / "logo-dark.png"

TEAL = colors.HexColor("#00E5C8")
CARBON = colors.HexColor("#080A0F")
SURFACE = colors.HexColor("#0D1117")
CARD = colors.HexColor("#131820")
BORDER = colors.HexColor("#1E2731")
WHITE = colors.HexColor("#F0F4F8")
CLEAR_STEEL = colors.HexColor("#91A1B2")
DEEP_TEAL = colors.HexColor("#00796B")


def register_fonts() -> tuple[str, str, str]:
    regular = Path("/System/Library/Fonts/Supplemental/Arial Unicode.ttf")
    bold = Path("/System/Library/Fonts/Supplemental/Arial Bold.ttf")
    display = Path("/System/Library/Fonts/Supplemental/Arial Black.ttf")
    if regular.exists() and bold.exists() and display.exists():
        pdfmetrics.registerFont(TTFont("SosaBody", regular))
        pdfmetrics.registerFont(TTFont("SosaBold", bold))
        pdfmetrics.registerFont(TTFont("SosaDisplay", display))
        pdfmetrics.registerFontFamily("SosaBody", normal="SosaBody", bold="SosaBold")
        return "SosaBody", "SosaBold", "SosaDisplay"
    return "Helvetica", "Helvetica-Bold", "Helvetica-Bold"


BODY_FONT, BOLD_FONT, DISPLAY_FONT = register_fonts()


def normalize(text: str) -> str:
    table = str.maketrans({
        "\u2013": "-", "\u2014": "-", "\u2011": "-", "\u2212": "-",
        "\u2018": "'", "\u2019": "'", "\u201c": '"', "\u201d": '"',
        "\u2192": "->", "\u00d7": "x", "\u00b7": " / ", "\u2026": "...",
    })
    return text.translate(table)


def inline(text: str) -> str:
    value = html.escape(normalize(text.strip()))
    value = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", value)
    value = re.sub(r"`(.+?)`", rf'<font name="{BOLD_FONT}" color="#00796B">\1</font>', value)
    value = re.sub(r"\[(.+?)\]\((.+?)\)", r'<link href="\2" color="#00796B">\1</link>', value)
    return value


def styles():
    base = getSampleStyleSheet()
    return {
        "h1": ParagraphStyle("H1", parent=base["Title"], fontName=DISPLAY_FONT, fontSize=29, leading=30, textColor=CARBON, spaceAfter=14),
        "h2": ParagraphStyle("H2", parent=base["Heading2"], fontName=DISPLAY_FONT, fontSize=21, leading=23, textColor=CARBON, spaceBefore=6, spaceAfter=12),
        "h3": ParagraphStyle("H3", parent=base["Heading3"], fontName=BOLD_FONT, fontSize=13, leading=16, textColor=DEEP_TEAL, spaceBefore=8, spaceAfter=5),
        "body": ParagraphStyle("Body", parent=base["BodyText"], fontName=BODY_FONT, fontSize=9.3, leading=13.4, textColor=colors.HexColor("#263440"), spaceAfter=7),
        "bullet": ParagraphStyle("Bullet", parent=base["BodyText"], fontName=BODY_FONT, fontSize=9.1, leading=12.8, textColor=colors.HexColor("#263440"), leftIndent=2),
        "quote": ParagraphStyle("Quote", parent=base["BodyText"], fontName=BODY_FONT, fontSize=9.4, leading=13.5, textColor=CARBON, leftIndent=13, rightIndent=8, borderColor=TEAL, borderWidth=2, borderPadding=8, backColor=colors.HexColor("#EAFBF8"), spaceAfter=8),
        "code": ParagraphStyle("Code", parent=base["Code"], fontName="Courier", fontSize=7.7, leading=10.5, textColor=WHITE, backColor=CARD, borderPadding=8, spaceAfter=8),
        "small": ParagraphStyle("Small", parent=base["BodyText"], fontName=BODY_FONT, fontSize=7.5, leading=9.5, textColor=CLEAR_STEEL),
    }


STYLES = styles()


class NumberedDoc(BaseDocTemplate):
    def __init__(self, filename: Path):
        super().__init__(
            str(filename), pagesize=LETTER, rightMargin=0.68 * inch,
            leftMargin=0.68 * inch, topMargin=0.72 * inch, bottomMargin=0.62 * inch,
            title="Sosa Tech Solutions Brand Guidelines v1.0",
            author="Sosa Tech Solutions",
            subject="Brand identity, voice, visual system, and production standards",
        )
        frame = Frame(self.leftMargin, self.bottomMargin, self.width, self.height, id="body")
        self.addPageTemplates(PageTemplate(id="manual", frames=[frame], onPage=self._decorate))

    @staticmethod
    def _decorate(canvas, doc):
        canvas.saveState()
        if doc.page > 1:
            canvas.setStrokeColor(BORDER)
            canvas.line(doc.leftMargin, LETTER[1] - 0.43 * inch, LETTER[0] - doc.rightMargin, LETTER[1] - 0.43 * inch)
            canvas.setFont(BOLD_FONT, 7.2)
            canvas.setFillColor(DEEP_TEAL)
            canvas.drawString(doc.leftMargin, LETTER[1] - 0.34 * inch, "SOSA TECH SOLUTIONS / BRAND GUIDELINES")
            canvas.setFont(BODY_FONT, 7.2)
            canvas.setFillColor(colors.HexColor("#5A6A7A"))
            canvas.drawRightString(LETTER[0] - doc.rightMargin, 0.34 * inch, f"VERSION 1.0 / {doc.page}")
        canvas.restoreState()


def table_from(lines: list[str], width: float):
    rows = []
    for line in lines:
        cells = [inline(cell) for cell in line.strip().strip("|").split("|")]
        if all(re.fullmatch(r":?-{3,}:?", html.unescape(cell).strip()) for cell in cells):
            continue
        rows.append([Paragraph(cell, STYLES["small"]) for cell in cells])
    if not rows:
        return Spacer(1, 1)
    col_count = len(rows[0])
    widths = [width / col_count] * col_count
    table = Table(rows, colWidths=widths, repeatRows=1, hAlign="LEFT")
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), CARBON),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("FONTNAME", (0, 0), (-1, 0), BOLD_FONT),
        ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#F5F8FA")),
        ("GRID", (0, 0), (-1, -1), 0.45, colors.HexColor("#CBD5DF")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    return table


def markdown_story(text: str, width: float):
    lines = text.splitlines()
    story = []
    index = 0
    first_h2 = True
    while index < len(lines):
        raw = lines[index]
        stripped = raw.strip()
        if not stripped or stripped == "---":
            index += 1
            continue
        if stripped.startswith("# "):
            index += 1
            continue
        if stripped.startswith("## "):
            if not first_h2:
                story.append(PageBreak())
            first_h2 = False
            story.extend([Paragraph(inline(stripped[3:]), STYLES["h2"]), HRFlowable(width="100%", thickness=1.5, color=TEAL, spaceAfter=10)])
            index += 1
            continue
        if stripped.startswith("### "):
            story.append(Paragraph(inline(stripped[4:]), STYLES["h3"]))
            index += 1
            continue
        if stripped.startswith("```"):
            code_lines = []
            index += 1
            while index < len(lines) and not lines[index].strip().startswith("```"):
                code_lines.append(lines[index])
                index += 1
            index += 1
            story.append(Paragraph(html.escape(normalize("\n".join(code_lines))).replace("\n", "<br/>"), STYLES["code"]))
            continue
        if stripped.startswith("|"):
            table_lines = []
            while index < len(lines) and lines[index].strip().startswith("|"):
                table_lines.append(lines[index])
                index += 1
            story.extend([table_from(table_lines, width), Spacer(1, 8)])
            continue
        if re.match(r"^(?:[-*]|\d+\.)\s+", stripped):
            entries = []
            while index < len(lines) and re.match(r"^(?:[-*]|\d+\.)\s+", lines[index].strip()):
                item = re.sub(r"^(?:[-*]|\d+\.)\s+", "", lines[index].strip())
                entries.append(ListItem(Paragraph(inline(item), STYLES["bullet"]), leftIndent=10))
                index += 1
            story.append(ListFlowable(entries, bulletType="bullet", start="circle", leftIndent=15, bulletColor=TEAL, spaceAfter=7))
            continue
        if stripped.startswith(">"):
            quote = []
            while index < len(lines) and lines[index].strip().startswith(">"):
                quote.append(lines[index].strip().lstrip(">").strip())
                index += 1
            story.append(Paragraph(inline(" ".join(quote)), STYLES["quote"]))
            continue
        paragraph = [stripped]
        index += 1
        while index < len(lines):
            probe = lines[index].strip()
            if not probe or probe.startswith(("#", "```", "|", ">")) or re.match(r"^(?:[-*]|\d+\.)\s+", probe):
                break
            paragraph.append(probe)
            index += 1
        story.append(Paragraph(inline(" ".join(paragraph)), STYLES["body"]))
    return story


def build_manual():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    destination = OUTPUT / "SOSA_TECH_BRAND_GUIDELINES_V1.pdf"
    doc = NumberedDoc(destination)
    story = [Spacer(1, 0.45 * inch)]
    if LOGO.exists():
        logo = Image(str(LOGO), width=3.8 * inch, height=1.35 * inch)
        logo.hAlign = "LEFT"
        story.append(logo)
    story.extend([
        Spacer(1, 0.45 * inch),
        Paragraph("BRAND<br/>GUIDELINES", ParagraphStyle("Cover", fontName=DISPLAY_FONT, fontSize=38, leading=37, textColor=CARBON)),
        Spacer(1, 0.25 * inch),
        HRFlowable(width=1.25 * inch, thickness=7, color=TEAL, hAlign="LEFT"),
        Spacer(1, 0.28 * inch),
        Paragraph("A practical identity, voice, and production system for Sosa Tech Solutions.", ParagraphStyle("CoverSub", fontName=BODY_FONT, fontSize=14, leading=20, textColor=colors.HexColor("#40505F"), rightIndent=1.4 * inch)),
        Spacer(1, 1.35 * inch),
        Paragraph("VERSION 1.0 / MIAMI / ENGLISH + ESPANOL", ParagraphStyle("CoverMeta", fontName=BOLD_FONT, fontSize=8, leading=11, textColor=DEEP_TEAL, tracking=1.3)),
        Paragraph("BRAND GUARDIAN: VICTOR SOSA", ParagraphStyle("CoverMeta2", fontName=BODY_FONT, fontSize=8, leading=11, textColor=colors.HexColor("#5A6A7A"))),
        PageBreak(),
    ])
    source = SOURCE.read_text(encoding="utf-8")
    story.extend(markdown_story(source, doc.width))
    doc.build(story)
    return destination


def label(canvas, text, x, y, width=None):
    canvas.setFillColor(DEEP_TEAL)
    canvas.setFont(BOLD_FONT, 7.2)
    canvas.drawString(x, y, normalize(text).upper())
    if width:
        canvas.setStrokeColor(TEAL)
        canvas.setLineWidth(2)
        canvas.line(x, y - 6, x + width, y - 6)


def wrapped(canvas, text, x, y, width, style, max_height=150):
    paragraph = Paragraph(inline(text), style)
    _, height = paragraph.wrap(width, max_height)
    paragraph.drawOn(canvas, x, y - height)
    return y - height


def build_quick_reference():
    from reportlab.pdfgen import canvas

    destination = OUTPUT / "SOSA_TECH_BRAND_QUICK_REFERENCE_V1.pdf"
    page = landscape(LETTER)
    c = canvas.Canvas(str(destination), pagesize=page)
    c.setTitle("Sosa Tech Solutions Brand Quick Reference v1.0")
    w, h = page
    margin = 0.42 * inch

    c.setFillColor(CARBON)
    c.rect(0, 0, w, h, stroke=0, fill=1)
    if LOGO.exists():
        c.drawImage(str(LOGO), margin, h - 1.07 * inch, width=2.42 * inch, height=0.86 * inch, preserveAspectRatio=True, mask="auto")
    c.setFillColor(TEAL)
    c.setFont(BOLD_FONT, 8)
    c.drawRightString(w - margin, h - 0.38 * inch, "BRAND QUICK REFERENCE / V1.0")
    c.setFillColor(WHITE)
    c.setFont(DISPLAY_FONT, 18)
    c.drawRightString(w - margin, h - 0.72 * inch, "WE BUILD. YOU GROW.")

    col_gap = 0.22 * inch
    col_w = (w - 2 * margin - 2 * col_gap) / 3
    top = h - 1.35 * inch
    card_h = 5.72 * inch
    for idx in range(3):
        x = margin + idx * (col_w + col_gap)
        c.setFillColor(CARD)
        c.roundRect(x, top - card_h, col_w, card_h, 4, stroke=0, fill=1)

    body = ParagraphStyle("QuickBody", fontName=BODY_FONT, fontSize=7.9, leading=11.2, textColor=WHITE)
    small = ParagraphStyle("QuickSmall", fontName=BODY_FONT, fontSize=7.1, leading=9.6, textColor=CLEAR_STEEL)
    head = ParagraphStyle("QuickHead", fontName=DISPLAY_FONT, fontSize=14.2, leading=15.4, textColor=WHITE)
    x1 = margin + 0.2 * inch
    y = top - 0.24 * inch
    label(c, "Brand foundation", x1, y, col_w - 0.4 * inch)
    y -= 0.28 * inch
    y = wrapped(c, "Practical systems that capture opportunities, remove repetitive work, and help small businesses operate with confidence.", x1, y, col_w - 0.4 * inch, head)
    y -= 0.17 * inch
    y = wrapped(c, "Capable / Direct / Resourceful / Modern / Approachable", x1, y, col_w - 0.4 * inch, body)
    y -= 0.23 * inch
    label(c, "Offer architecture", x1, y)
    y -= 0.22 * inch
    offers = ["01  Launch & Convert", "02  Automate & Respond", "03  Reach & Grow", "04  Run Reliably", "05  Stream & Broadcast"]
    for offer in offers:
        c.setFillColor(TEAL if offer.startswith(("01", "02", "03")) else CLEAR_STEEL)
        c.setFont(BOLD_FONT, 8.1)
        c.drawString(x1, y, offer)
        y -= 0.2 * inch
    y -= 0.05 * inch
    label(c, "Messaging", x1, y)
    y -= 0.22 * inch
    y = wrapped(c, "Core: Technology that captures leads, saves time, and keeps your business moving.", x1, y, col_w - 0.4 * inch, body)
    y -= 0.08 * inch
    wrapped(c, "Primary CTA: Book a free systems review. Secondary CTA: Message us on WhatsApp.", x1, y, col_w - 0.4 * inch, small)

    x2 = margin + col_w + col_gap + 0.2 * inch
    y = top - 0.24 * inch
    label(c, "Color system", x2, y, col_w - 0.4 * inch)
    y -= 0.32 * inch
    swatches = [("Electric Teal", "#00E5C8", TEAL), ("Carbon", "#080A0F", CARBON), ("Deep Surface", "#0D1117", SURFACE), ("Graphite", "#131820", CARD), ("Signal White", "#F0F4F8", WHITE), ("Clear Steel", "#91A1B2", CLEAR_STEEL)]
    for name, code, color in swatches:
        c.setFillColor(color)
        c.rect(x2, y - 8, 24, 15, stroke=1, fill=1)
        c.setFillColor(WHITE)
        c.setFont(BOLD_FONT, 7.4)
        c.drawString(x2 + 32, y + 1, name)
        c.setFillColor(CLEAR_STEEL)
        c.setFont(BODY_FONT, 7.1)
        c.drawRightString(x2 + col_w - 0.4 * inch, y + 1, code)
        y -= 0.27 * inch
    y -= 0.08 * inch
    label(c, "Typography", x2, y)
    y -= 0.25 * inch
    c.setFillColor(WHITE); c.setFont(DISPLAY_FONT, 12); c.drawString(x2, y, "SYNE / DISPLAY")
    y -= 0.24 * inch
    c.setFont(BOLD_FONT, 9); c.drawString(x2, y, "DM Sans / Body & UI")
    y -= 0.21 * inch
    c.setFillColor(TEAL); c.setFont("Courier-Bold", 8); c.drawString(x2, y, "DM MONO / LABELS")
    y -= 0.3 * inch
    label(c, "Composition", x2, y)
    y -= 0.22 * inch
    wrapped(c, "70% dark surface / 20% light neutral / 10% teal signal. Use one focal point, one message, and no more than two graphic devices.", x2, y, col_w - 0.4 * inch, small)

    x3 = margin + 2 * (col_w + col_gap) + 0.2 * inch
    y = top - 0.24 * inch
    label(c, "Voice & production", x3, y, col_w - 0.4 * inch)
    y -= 0.28 * inch
    c.setFillColor(WHITE); c.setFont(DISPLAY_FONT, 13); c.drawString(x3, y, "CLEAR. USEFUL. SPECIFIC.")
    y -= 0.28 * inch
    y = wrapped(c, "Lead with the business problem. Explain the technology second. Use short sentences, active verbs, and one useful next action.", x3, y, col_w - 0.4 * inch, body)
    y -= 0.17 * inch
    label(c, "Say", x3, y)
    y -= 0.2 * inch
    y = wrapped(c, "Practical systems / Clear next step / Faster follow-up / Direct support / Built to be maintained", x3, y, col_w - 0.4 * inch, small)
    y -= 0.15 * inch
    label(c, "Avoid", x3, y)
    y -= 0.2 * inch
    y = wrapped(c, "Revolutionary / Guaranteed growth / Magic / AI-powered everything / Invented results / Fake dashboards", x3, y, col_w - 0.4 * inch, small)
    y -= 0.16 * inch
    label(c, "Export specs", x3, y)
    y -= 0.2 * inch
    y = wrapped(c, "Feed 1080x1350 / Square 1080x1080 / Reel + Story 1080x1920 / Link preview 1200x630 / Feed safe margin 72 px", x3, y, col_w - 0.4 * inch, small)
    y -= 0.15 * inch
    label(c, "Approval", x3, y)
    y -= 0.2 * inch
    wrapped(c, "Victor approval: logo or palette changes, pricing, client names/results, testimonials, paid campaigns, or automatic publishing.", x3, y, col_w - 0.4 * inch, small)

    c.setFillColor(CLEAR_STEEL)
    c.setFont(BODY_FONT, 6.8)
    c.drawString(margin, 0.22 * inch, "SOURCE OF TRUTH: brand/BRAND_GUIDELINES.md")
    c.drawRightString(w - margin, 0.22 * inch, "SOSA TECH SOLUTIONS / MIAMI / ENGLISH + ESPANOL")
    c.save()
    return destination


if __name__ == "__main__":
    manual = build_manual()
    quick = build_quick_reference()
    print(manual)
    print(quick)

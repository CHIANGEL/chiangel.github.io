#!/usr/bin/env python3
"""Build the 42 x 36 inch KDD 2026 poster for PerFusion.

Usage:
  python scripts/build_perfusion_poster.py \
    --paper /path/to/perfusion.pdf \
    --output output/pdf/perfusion-kdd2026-poster.pdf
"""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

from PIL import Image
from reportlab.graphics import renderPDF
from reportlab.graphics.barcode.qr import QrCodeWidget
from reportlab.graphics.shapes import Drawing
from reportlab.lib.colors import HexColor, white
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import landscape
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph


ROOT = Path(__file__).resolve().parents[1]
FIG_DIR = ROOT / "figures" / "perfusion_poster"
SOURCE_DIR = FIG_DIR / "source"

PAGE_W = 42 * inch
PAGE_H = 36 * inch

NAVY = HexColor("#17233C")
BLUE = HexColor("#3E5F8A")
TEAL = HexColor("#2A9D8F")
CORAL = HexColor("#E76F51")
GOLD = HexColor("#E9C46A")
INK = HexColor("#25324A")
MUTED = HexColor("#667085")
PALE = HexColor("#F4F6FA")
LINE = HexColor("#DCE2EC")
MINT_BG = HexColor("#EAF7F4")
BLUE_BG = HexColor("#EDF2F8")
CORAL_BG = HexColor("#FFF0EC")
GOLD_BG = HexColor("#FFF8E4")

FONT = "/System/Library/Fonts/Supplemental/Arial.ttf"
FONT_BOLD = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
FONT_ITALIC = "/System/Library/Fonts/Supplemental/Arial Italic.ttf"

PAPER_URL = "https://arxiv.org/abs/2503.22182"
DOI_URL = "https://doi.org/10.1145/3770854.3783918"


def register_fonts() -> None:
    pdfmetrics.registerFont(TTFont("Arial", FONT))
    pdfmetrics.registerFont(TTFont("Arial-Bold", FONT_BOLD))
    pdfmetrics.registerFont(TTFont("Arial-Italic", FONT_ITALIC))


def render_page(pdf: Path, page: int, dpi: int = 600) -> Path:
    SOURCE_DIR.mkdir(parents=True, exist_ok=True)
    output_prefix = SOURCE_DIR / f"page-{page:02d}-{dpi}dpi"
    output = output_prefix.with_suffix(".png")
    if not output.exists():
        subprocess.run(
            [
                "pdftoppm",
                "-f",
                str(page),
                "-l",
                str(page),
                "-singlefile",
                "-png",
                "-r",
                str(dpi),
                str(pdf),
                str(output_prefix),
            ],
            check=True,
        )
    return output


def crop_figure(
    pdf: Path,
    name: str,
    page: int,
    crop_points: tuple[float, float, float, float],
    dpi: int = 600,
) -> Path:
    """Crop a source figure using top-origin PDF point coordinates."""
    output = SOURCE_DIR / f"{name}.png"
    source = render_page(pdf, page, dpi)
    scale = dpi / 72.0
    box = tuple(round(value * scale) for value in crop_points)
    with Image.open(source) as image:
        cropped = image.crop(box)
        cropped.save(output, optimize=True)
    return output


def prepare_source_figures(pdf: Path) -> dict[str, Path]:
    return {
        "paradigm": crop_figure(pdf, "fig1_paradigm", 2, (52, 78, 304, 211)),
        "challenges": crop_figure(pdf, "fig2_challenges", 2, (316, 80, 571, 178)),
        "reward": crop_figure(pdf, "fig3_perfusion_rm", 4, (52, 73, 302, 287)),
        "architecture": crop_figure(pdf, "fig4_perfusion", 5, (316, 82, 575, 378)),
        "case": crop_figure(pdf, "fig7_case_study", 9, (82, 70, 528, 267)),
    }


def paragraph(
    c: canvas.Canvas,
    text: str,
    x: float,
    top: float,
    width: float,
    *,
    size: float = 23,
    leading: float | None = None,
    color=INK,
    font: str = "Arial",
    align: int = TA_LEFT,
    space_after: float = 0,
) -> float:
    leading = leading or size * 1.28
    style = ParagraphStyle(
        name="poster",
        fontName=font,
        fontSize=size,
        leading=leading,
        textColor=color,
        alignment=align,
        spaceAfter=space_after,
    )
    flowable = Paragraph(text, style)
    _, height = flowable.wrap(width, PAGE_H)
    flowable.drawOn(c, x, top - height)
    return top - height - space_after


def section_title(c: canvas.Canvas, title: str, x: float, top: float, width: float) -> float:
    c.setFillColor(NAVY)
    c.roundRect(x, top - 40, 13, 40, 6, stroke=0, fill=1)
    c.setFont("Arial-Bold", 31)
    c.drawString(x + 27, top - 31, title.upper())
    c.setStrokeColor(LINE)
    c.setLineWidth(1.5)
    c.line(x, top - 51, x + width, top - 51)
    return top - 69


def draw_card(
    c: canvas.Canvas,
    x: float,
    y: float,
    width: float,
    height: float,
    fill,
    *,
    radius: float = 18,
    stroke=LINE,
    line_width: float = 1.2,
) -> None:
    c.setFillColor(fill)
    c.setStrokeColor(stroke)
    c.setLineWidth(line_width)
    c.roundRect(x, y, width, height, radius, stroke=1, fill=1)


def draw_image_contain(
    c: canvas.Canvas,
    path: Path,
    x: float,
    y: float,
    width: float,
    height: float,
    *,
    pad: float = 0,
) -> None:
    with Image.open(path) as image:
        iw, ih = image.size
    scale = min((width - 2 * pad) / iw, (height - 2 * pad) / ih)
    draw_w, draw_h = iw * scale, ih * scale
    draw_x = x + (width - draw_w) / 2
    draw_y = y + (height - draw_h) / 2
    c.drawImage(str(path), draw_x, draw_y, draw_w, draw_h, mask="auto")


def draw_metric(
    c: canvas.Canvas,
    x: float,
    y: float,
    width: float,
    height: float,
    value: str,
    label: str,
    fill,
    accent,
) -> None:
    draw_card(c, x, y, width, height, fill, stroke=fill)
    c.setFillColor(accent)
    c.roundRect(x, y, 12, height, 6, stroke=0, fill=1)
    c.setFillColor(NAVY)
    c.setFont("Arial-Bold", 39)
    c.drawString(x + 28, y + height - 54, value)
    paragraph(c, label, x + 28, y + height - 70, width - 46, size=19, leading=23, color=MUTED)


def draw_step(c: canvas.Canvas, x: float, y: float, width: float, number: str, title: str, body: str, color) -> None:
    c.setFillColor(color)
    c.circle(x + 26, y + 88, 24, stroke=0, fill=1)
    c.setFillColor(white)
    c.setFont("Arial-Bold", 20)
    c.drawCentredString(x + 26, y + 81, number)
    c.setFillColor(NAVY)
    c.setFont("Arial-Bold", 22)
    c.drawString(x + 62, y + 105, title)
    paragraph(c, body, x + 62, y + 90, width - 70, size=18, leading=22, color=MUTED)


def draw_qr(c: canvas.Canvas, url: str, x: float, y: float, size: float) -> None:
    c.setFillColor(white)
    c.roundRect(x - 7, y - 7, size + 14, size + 14, 8, stroke=0, fill=1)
    qr = QrCodeWidget(url)
    x1, y1, x2, y2 = qr.getBounds()
    width, height = x2 - x1, y2 - y1
    drawing = Drawing(size, size, transform=[size / width, 0, 0, size / height, 0, 0])
    drawing.add(qr)
    renderPDF.draw(drawing, c, x, y)
    c.linkURL(url, (x, y, x + size, y + size), relative=0)


def build_poster(paper: Path, output: Path) -> None:
    register_fonts()
    figs = prepare_source_figures(paper)
    online_chart = FIG_DIR / "fig_online_impact.png"
    reward_chart = FIG_DIR / "fig_reward_model_gauc.png"
    for chart in (online_chart, reward_chart):
        if not chart.exists():
            raise FileNotFoundError(f"Missing chart: {chart}. Run gen_fig_perfusion_poster_results.py first.")

    output.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(output), pagesize=(PAGE_W, PAGE_H), pageCompression=1)
    c.setTitle("PerFusion - KDD 2026 Poster")
    c.setAuthor("Jianghao Lin, Peng Du, Jiaqi Liu, Weite Li, Yong Yu, Weinan Zhang, Yang Cao")
    c.setSubject("Sell It Before You Make It: Personalized AI-Generated Items")

    # Background and header.
    c.setFillColor(PALE)
    c.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)
    header_h = 348
    c.setFillColor(NAVY)
    c.rect(0, PAGE_H - header_h, PAGE_W, header_h, stroke=0, fill=1)
    c.setFillColor(CORAL)
    c.setFillAlpha(0.92)
    c.circle(PAGE_W - 100, PAGE_H + 35, 275, stroke=0, fill=1)
    c.setFillColor(TEAL)
    c.setFillAlpha(0.55)
    c.circle(PAGE_W - 310, PAGE_H - 5, 185, stroke=0, fill=1)
    c.setFillAlpha(1)

    c.setFillColor(CORAL)
    c.roundRect(48, PAGE_H - 74, 174, 38, 10, stroke=0, fill=1)
    c.setFillColor(white)
    c.setFont("Arial-Bold", 18)
    c.drawCentredString(135, PAGE_H - 61, "KDD 2026 | JEJU")

    c.setFillColor(white)
    c.setFont("Arial-Bold", 63)
    c.drawString(48, PAGE_H - 146, "Sell It Before You Make It")
    c.setFont("Arial-Bold", 47)
    c.drawString(48, PAGE_H - 207, "Revolutionizing E-Commerce with Personalized AI-Generated Items")

    c.setFillColor(HexColor("#E8ECF4"))
    c.setFont("Arial", 23)
    c.drawString(
        50,
        PAGE_H - 259,
        "Jianghao Lin | Peng Du | Jiaqi Liu | Weite Li | Yong Yu | Weinan Zhang | Yang Cao",
    )
    c.setFont("Arial", 18)
    c.drawString(
        50,
        PAGE_H - 294,
        "Shanghai Jiao Tong University | Alibaba Group    |    KDD '26, August 9-13, 2026",
    )
    c.setFont("Arial-Italic", 17)
    c.drawString(50, PAGE_H - 326, "PerFusion aligns diffusion models with merchants' group-level personalized preferences.")

    # Column cards.
    margin = 45
    gap = 34
    body_bottom = 86
    body_top = PAGE_H - header_h - 28
    col_w = (PAGE_W - 2 * margin - 2 * gap) / 3
    xs = [margin, margin + col_w + gap, margin + 2 * (col_w + gap)]
    for x in xs:
        draw_card(c, x, body_bottom, col_w, body_top - body_bottom, white, radius=20, stroke=LINE)

    pad = 27

    # ------------------------------------------------------------------ LEFT
    x = xs[0] + pad
    width = col_w - 2 * pad
    top = body_top - 28
    top = section_title(c, "A paradigm shift", x, top, width)

    draw_card(c, x, top - 128, width, 128, BLUE_BG, stroke=BLUE_BG)
    c.setFillColor(BLUE)
    c.setFont("Arial-Bold", 35)
    c.drawString(x + 25, top - 48, "Generate -> sell -> manufacture on demand")
    paragraph(
        c,
        "AIGI removes the physical prototype from the critical path and lets merchants test demand before committing inventory.",
        x + 25,
        top - 65,
        width - 50,
        size=20,
        leading=25,
        color=INK,
    )
    top -= 153

    draw_card(c, x, top - 494, width, 494, white, stroke=LINE)
    draw_image_contain(c, figs["paradigm"], x + 10, top - 478, width - 20, 462)
    top -= 515
    top = paragraph(
        c,
        "<b>Business mode.</b> Merchants generate photorealistic designs first. Production starts only after customer orders reach a threshold - reducing inventory risk and shrinking launch cycles from months to days.",
        x,
        top,
        width,
        size=21,
        leading=27,
    ) - 20

    top = section_title(c, "The scientific gap", x, top, width)
    draw_card(c, x, top - 325, width, 325, PALE, stroke=PALE)
    draw_image_contain(c, figs["challenges"], x + 12, top - 305, width - 24, 285)
    top -= 347

    half = (width - 16) / 2
    draw_card(c, x, top - 190, half, 190, MINT_BG, stroke=MINT_BG)
    c.setFillColor(TEAL)
    c.setFont("Arial-Bold", 26)
    c.drawString(x + 20, top - 38, "01 | GROUP-LEVEL")
    paragraph(
        c,
        "Selections are made by comparing an entire candidate set - not isolated positives or pairs.",
        x + 20,
        top - 56,
        half - 40,
        size=20,
        leading=25,
        color=INK,
    )
    draw_card(c, x + half + 16, top - 190, half, 190, CORAL_BG, stroke=CORAL_BG)
    c.setFillColor(CORAL)
    c.setFont("Arial-Bold", 26)
    c.drawString(x + half + 36, top - 38, "02 | PERSONALIZED")
    paragraph(
        c,
        "The same prompt and image set can trigger sharply different choices across merchants.",
        x + half + 36,
        top - 56,
        half - 40,
        size=20,
        leading=25,
        color=INK,
    )
    top -= 214

    draw_card(c, x, top - 230, width, 230, GOLD_BG, stroke=GOLD_BG)
    c.setFillColor(GOLD)
    c.roundRect(x, top - 230, 13, 230, 6, stroke=0, fill=1)
    c.setFillColor(NAVY)
    c.setFont("Arial-Bold", 28)
    c.drawString(x + 30, top - 45, "OUR ANSWER: PERFUSION")
    paragraph(
        c,
        "A personalized reward model plus a personalized adaptive diffusion network, trained with a group-level preference objective. The result is the first industrial-scale deployment of personalized text-to-image generation for item design.",
        x + 30,
        top - 65,
        width - 55,
        size=20,
        leading=25,
        color=INK,
    )

    # ---------------------------------------------------------------- CENTER
    x = xs[1] + pad
    width = col_w - 2 * pad
    top = body_top - 28
    top = section_title(c, "PerFusion", x, top, width)
    top = paragraph(
        c,
        "Two components learn <b>who the merchant is</b>, <b>which candidates they prefer</b>, and <b>how to steer generation accordingly</b>.",
        x,
        top,
        width,
        size=22,
        leading=28,
    ) - 12

    row_h = 705
    arch_w = 520
    draw_card(c, x, top - row_h, arch_w, row_h, PALE, stroke=PALE)
    draw_image_contain(c, figs["architecture"], x + 10, top - row_h + 14, arch_w - 20, row_h - 28)

    side_x = x + arch_w + 18
    side_w = width - arch_w - 18
    draw_card(c, side_x, top - 335, side_w, 335, BLUE_BG, stroke=BLUE_BG)
    c.setFillColor(BLUE)
    c.setFont("Arial-Bold", 24)
    c.drawString(side_x + 20, top - 38, "PERFUSIONRM")
    paragraph(
        c,
        "Feature-crossing personalized plug-ins inject merchant representations into both CLIP towers. A group-wise ranking loss learns preference over all candidates.",
        side_x + 20,
        top - 58,
        side_w - 40,
        size=19,
        leading=24,
        color=INK,
    )
    c.setFillColor(BLUE)
    c.setFont("Arial-Bold", 20)
    c.drawString(side_x + 20, top - 302, "Output: personalized reward")

    draw_card(c, side_x, top - row_h, side_w, 350, CORAL_BG, stroke=CORAL_BG)
    c.setFillColor(CORAL)
    c.setFont("Arial-Bold", 24)
    c.drawString(side_x + 20, top - 390, "PERSONALIZED GENERATOR")
    paragraph(
        c,
        "A ControlNet-style adaptive network conditions Stable Diffusion on user features. The original U-Net stays frozen; trainable copies and zero convolutions add personalized signals safely.",
        side_x + 20,
        top - 412,
        side_w - 40,
        size=19,
        leading=24,
        color=INK,
    )
    c.setFillColor(CORAL)
    c.setFont("Arial-Bold", 20)
    c.drawString(side_x + 20, top - 672, "Output: preference-aligned images")
    top -= row_h + 20

    draw_card(c, x, top - 235, width, 235, MINT_BG, stroke=MINT_BG)
    c.setFillColor(TEAL)
    c.setFont("Arial-Bold", 25)
    c.drawString(x + 24, top - 42, "GROUP-LEVEL PREFERENCE OPTIMIZATION")
    paragraph(
        c,
        "Replace pairwise Bradley-Terry comparisons with a Plackett-Luce view over positive set <i>P</i> and negative set <i>N</i>. The objective preserves the global candidate context while conditioning on merchant representation <i>u</i>.",
        x + 24,
        top - 66,
        width - 48,
        size=20,
        leading=26,
        color=INK,
    )
    top -= 260

    top = section_title(c, "Offline evidence", x, top, width)
    draw_card(c, x, top - 472, width, 472, white, stroke=LINE)
    draw_image_contain(c, reward_chart, x + 8, top - 462, width - 16, 452)
    top -= 496

    third = (width - 24) / 3
    draw_metric(c, x, top - 170, third, 170, "0.9220", "Industrial MAP", BLUE_BG, BLUE)
    draw_metric(c, x + third + 12, top - 170, third, 170, "0.9564", "Industrial GAUC", CORAL_BG, CORAL)
    draw_metric(c, x + 2 * (third + 12), top - 170, third, 170, "26.44", "Industrial reward", MINT_BG, TEAL)
    top -= 192

    draw_card(c, x, top - 168, width, 168, GOLD_BG, stroke=GOLD_BG)
    paragraph(
        c,
        "<b>Ablations confirm both pieces matter:</b> removing the personalized adaptive network or the group-level objective degrades personalized generation on PickaPic and Alibaba's industrial dataset.",
        x + 24,
        top - 28,
        width - 48,
        size=20,
        leading=26,
        color=INK,
    )

    # ---------------------------------------------------------------- RIGHT
    x = xs[2] + pad
    width = col_w - 2 * pad
    top = body_top - 28
    top = section_title(c, "Works in production", x, top, width)

    half = (width - 14) / 2
    metric_h = 150
    draw_metric(c, x, top - metric_h, half, metric_h, "+17.81%", "Search CTR", MINT_BG, TEAL)
    draw_metric(c, x + half + 14, top - metric_h, half, metric_h, "+13.35%", "Recommendation CTR", BLUE_BG, BLUE)
    draw_metric(c, x, top - 2 * metric_h - 14, half, metric_h, "+17.27%", "Conversion rate", CORAL_BG, CORAL)
    draw_metric(c, x + half + 14, top - 2 * metric_h - 14, half, metric_h, "-7.9%", "Return rate", GOLD_BG, GOLD)
    top -= 338

    draw_card(c, x, top - 390, width, 390, white, stroke=LINE)
    draw_image_contain(c, online_chart, x + 10, top - 378, width - 20, 366)
    top -= 414

    top = section_title(c, "Product lifecycle", x, top, width)
    step_w = width / 3
    draw_step(c, x, top - 176, step_w, "1", "AI-assisted design", "Generate and select photorealistic items.", TEAL)
    draw_step(c, x + step_w, top - 176, step_w, "2", "Demand aggregation", "List designs and collect customer orders.", BLUE)
    draw_step(c, x + 2 * step_w, top - 176, step_w, "3", "Manufacture", "Trigger bulk production at a set threshold.", CORAL)
    c.setStrokeColor(LINE)
    c.setLineWidth(2)
    c.line(x + step_w - 10, top - 88, x + step_w + 10, top - 88)
    c.line(x + 2 * step_w - 10, top - 88, x + 2 * step_w + 10, top - 88)
    top -= 205

    top = section_title(c, "Same prompt, different taste", x, top, width)
    draw_card(c, x, top - 410, width, 410, white, stroke=LINE)
    draw_image_contain(c, figs["case"], x + 10, top - 400, width - 20, 390)
    top -= 434

    top = section_title(c, "Six-month deployment", x, top, width)
    third = (width - 24) / 3
    draw_metric(c, x, top - 156, third, 156, "2.5x", "Stores using AIGI", BLUE_BG, BLUE)
    draw_metric(c, x + third + 12, top - 156, third, 156, "2.81x", "Monthly GMV / store", MINT_BG, TEAL)
    draw_metric(c, x + 2 * (third + 12), top - 156, third, 156, "2.71x", "New products / month", CORAL_BG, CORAL)
    top -= 178

    draw_card(c, x, top - 222, width, 222, NAVY, stroke=NAVY)
    c.setFillColor(GOLD)
    c.setFont("Arial-Bold", 24)
    c.drawString(x + 25, top - 40, "TAKEAWAY")
    paragraph(
        c,
        "PerFusion turns personalized generation into a viable commerce loop: design digitally, validate demand in-market, then manufacture what customers already chose.",
        x + 25,
        top - 61,
        width - 190,
        size=21,
        leading=27,
        color=white,
    )
    draw_qr(c, PAPER_URL, x + width - 145, top - 182, 112)
    c.setFillColor(HexColor("#D5DCEA"))
    c.setFont("Arial", 15)
    c.drawCentredString(x + width - 89, top - 205, "SCAN FOR PAPER")

    # Global footer.
    c.setFillColor(NAVY)
    c.setFont("Arial-Bold", 17)
    c.drawString(52, 45, "PerFusion | KDD 2026")
    c.setFont("Arial", 16)
    c.drawString(270, 45, "doi.org/10.1145/3770854.3783918")
    c.linkURL(DOI_URL, (270, 30, 575, 65), relative=0)
    c.drawRightString(PAGE_W - 52, 45, "linjianghao.com  |  linjianghao@sjtu.edu.cn")

    c.showPage()
    c.save()
    print(f"Built poster: {output}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--paper", type=Path, required=True)
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "output" / "pdf" / "perfusion-kdd2026-poster.pdf",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    build_poster(args.paper.resolve(), args.output.resolve())


if __name__ == "__main__":
    main()

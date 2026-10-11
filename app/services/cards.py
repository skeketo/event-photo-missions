import os
from datetime import datetime
from pathlib import Path

from reportlab.lib.pagesizes import A6, A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

from database import get_conn
from services.config import get_setting, get_config
from services.front_cover import generate_front_cover, THEMES

CARDS_DIR = Path("/app/cards")
FRONT_TEMPLATE = Path("/app/assets/front_template.png")

WHITE = colors.white


def _theme_colors():
    config = get_config()
    event_type = config.get("EVENT_TYPE", "custom")
    theme = THEMES.get(event_type, THEMES["custom"])

    return {
        "bg": colors.HexColor(theme["bg"]),
        "accent": colors.HexColor(theme["accent"]),
        "accent2": colors.HexColor(theme["accent2"]),
        "text": colors.HexColor(theme["text"]),
        "soft": colors.HexColor(theme["soft"]),
    }


def _wrap_text(text, max_chars=54):
    words = text.split()
    lines = []
    current = ""

    for word in words:
        candidate = (current + " " + word).strip()
        if len(candidate) <= max_chars:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word

    if current:
        lines.append(current)

    return lines


def _draw_card_front(c):
    width, height = A6

    if FRONT_TEMPLATE.exists():
        bg = ImageReader(str(FRONT_TEMPLATE))
        c.drawImage(
            bg,
            0,
            0,
            width=width,
            height=height,
            preserveAspectRatio=False,
            mask="auto"
        )
        return

    c.setFillColor(colors.HexColor("#fbf6f0"))
    c.rect(0, 0, width, height, fill=1, stroke=0)

    c.setFillColor(colors.HexColor("#4f372c"))
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(width / 2, height - 45 * mm, "Falta portada")

    c.setFont("Helvetica", 9)
    c.drawCentredString(width / 2, height - 55 * mm, "/app/assets/front_template.png")


def _draw_card_back(c, guest, missions):
    width, height = A6
    theme = _theme_colors()

    BG_BACK = theme["bg"]
    BROWN = theme["text"]
    ACCENT = theme["accent"]
    ACCENT_DARK = theme["accent"]
    TEXT_SOFT = theme["soft"]
    LIGHT_LINE = theme["accent2"]

    config = get_config()
    event_label = config.get("EVENT_LABEL", "evento")
    prize_text = get_setting("PRIZE_TEXT", "el premio indicado por los organizadores")

    display_name = guest["alias"] or guest["name"]

    c.setFillColor(BG_BACK)
    c.rect(0, 0, width, height, fill=1, stroke=0)

    c.setFillColor(BROWN)
    c.setFont("Helvetica-Bold", 17)
    c.drawCentredString(width / 2, height - 16 * mm, "Misión fotográfica")

    c.setFillColor(TEXT_SOFT)
    c.setFont("Helvetica", 8.5)
    c.drawCentredString(width / 2, height - 23 * mm, f"Forma parte del equipo oficial de recuerdos del {event_label}")

    c.setStrokeColor(LIGHT_LINE)
    c.setLineWidth(0.8)
    c.line(22 * mm, height - 27.5 * mm, width - 22 * mm, height - 27.5 * mm)

    c.setFillColor(ACCENT)
    c.roundRect(13 * mm, height - 40 * mm, width - 26 * mm, 10 * mm, 5 * mm, fill=1, stroke=0)

    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", 10.5)
    c.drawCentredString(width / 2, height - 36.5 * mm, f"Participante: {display_name}")

    c.setFillColor(BROWN)
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString(width / 2, height - 50 * mm, "Tus 8 misiones")

    c.setFillColor(TEXT_SOFT)
    c.setFont("Helvetica", 7.8)
    c.drawCentredString(width / 2, height - 56 * mm, "Completa las que puedas y sube tus fotos con el QR")

    y = height - 68 * mm
    left_margin = 16 * mm
    text_x = 25 * mm

    missions = list(missions)[:8]

    for idx in range(8):
        if idx < len(missions):
            title = missions[idx]["title"]
        else:
            title = "Misión pendiente"

        c.setFillColor(ACCENT)
        c.circle(left_margin + 3 * mm, y + 1.2 * mm, 3.8 * mm, fill=1, stroke=0)

        c.setFillColor(WHITE)
        c.setFont("Helvetica-Bold", 7.5)
        c.drawCentredString(left_margin + 3 * mm, y - 1.2 * mm, str(idx + 1))

        c.setFillColor(BROWN)
        c.setFont("Helvetica-Bold", 8.2)

        lines = _wrap_text(title, 48)[:2]
        for line in lines:
            c.drawString(text_x, y, line)
            y -= 4.1 * mm

        y -= 4.2 * mm

    c.setStrokeColor(LIGHT_LINE)
    c.line(28 * mm, 18 * mm, width - 28 * mm, 18 * mm)

    c.setFont("Helvetica-Bold", 7.8)
    c.setFillColor(ACCENT_DARK)
    c.drawCentredString(width / 2, 14.0 * mm, "Premio al fotógrafo estrella")

    c.setFont("Helvetica", 6.3)
    c.setFillColor(BROWN)
    c.drawCentredString(width / 2, 10.8 * mm, "Quien lidere el ranking se llevará:")

    prize_lines = _wrap_text(prize_text, 42)[:2]
    y_prize = 7.8 * mm
    for line in prize_lines:
        c.drawCentredString(width / 2, y_prize, line)
        y_prize -= 3.0 * mm


def get_guest_cards_data():
    with get_conn() as conn:
        guests = conn.execute("""
            SELECT *
            FROM guests
            ORDER BY table_name, group_name, name, surname
        """).fetchall()

        data = []

        for guest in guests:
            missions = conn.execute("""
                SELECT m.*
                FROM guest_missions gm
                JOIN missions m ON m.id = gm.mission_id
                WHERE gm.guest_id = ?
                ORDER BY gm.id
            """, (guest["id"],)).fetchall()

            data.append((guest, missions))

        return data


def generate_cards_pdf():
    generate_front_cover()
    CARDS_DIR.mkdir(parents=True, exist_ok=True)

    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    output = CARDS_DIR / f"cards-a6-{stamp}.pdf"

    c = canvas.Canvas(str(output), pagesize=A6)

    for guest, missions in get_guest_cards_data():
        _draw_card_front(c)
        c.showPage()

        _draw_card_back(c, guest, missions)
        c.showPage()

    c.save()
    return output


def generate_cards_pdf_a4():
    generate_front_cover()
    CARDS_DIR.mkdir(parents=True, exist_ok=True)

    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    output = CARDS_DIR / f"cards-a4-4perpage-{stamp}.pdf"

    a4w, a4h = A4
    cardw, cardh = A6

    positions = [
        (0, a4h - cardh),
        (cardw, a4h - cardh),
        (0, a4h - cardh * 2),
        (cardw, a4h - cardh * 2),
    ]

    c = canvas.Canvas(str(output), pagesize=A4)
    data = get_guest_cards_data()

    for i in range(0, len(data), 4):
        chunk = data[i:i+4]

        for idx, (guest, missions) in enumerate(chunk):
            x, y = positions[idx]
            c.saveState()
            c.translate(x, y)
            _draw_card_front(c)
            c.restoreState()

        c.showPage()

        for idx, (guest, missions) in enumerate(chunk):
            x, y = positions[idx]
            c.saveState()
            c.translate(x, y)
            _draw_card_back(c, guest, missions)
            c.restoreState()

        c.showPage()

    c.save()
    return output

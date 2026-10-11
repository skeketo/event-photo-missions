from pathlib import Path
import textwrap

from PIL import Image, ImageDraw, ImageFont
import qrcode

from services.config import get_config

ASSETS_DIR = Path("/app/assets")
OUTPUT = ASSETS_DIR / "front_template.png"

W, H = 1055, 1491


THEMES = {
    "wedding": {
        "bg": "#fbf4ee",
        "accent": "#b98972",
        "accent2": "#e7c7b8",
        "text": "#4f372c",
        "soft": "#8a6f62",
        "label": "Wedding Photo Missions",
        "phrase": "Captura los recuerdos más bonitos del día",
        "decor": "floral",
    },
    "birthday": {
        "bg": "#fff7e8",
        "accent": "#e09a3e",
        "accent2": "#ffd28a",
        "text": "#4a3322",
        "soft": "#8a6a42",
        "label": "Birthday Photo Missions",
        "phrase": "Haz que cada momento cuente",
        "decor": "confetti",
    },
    "company": {
        "bg": "#f4f7fb",
        "accent": "#315f8f",
        "accent2": "#b9d3ea",
        "text": "#203040",
        "soft": "#5d7185",
        "label": "Event Photo Missions",
        "phrase": "Comparte los mejores momentos del evento",
        "decor": "corporate",
    },
    "party": {
        "bg": "#fbf0ff",
        "accent": "#9b4dca",
        "accent2": "#e2b8ff",
        "text": "#3c2452",
        "soft": "#735987",
        "label": "Party Photo Missions",
        "phrase": "Captura la energía de la fiesta",
        "decor": "confetti",
    },
    "communion": {
        "bg": "#f8f4ec",
        "accent": "#b59a62",
        "accent2": "#e8dcc0",
        "text": "#4a3b26",
        "soft": "#7d705a",
        "label": "Celebration Photo Missions",
        "phrase": "Guarda los recuerdos de un día especial",
        "decor": "classic",
    },
    "custom": {
        "bg": "#f8f3ed",
        "accent": "#9f735f",
        "accent2": "#d8c1b3",
        "text": "#4f372c",
        "soft": "#7e685e",
        "label": "Event Photo Missions",
        "phrase": "Completa misiones y comparte recuerdos",
        "decor": "classic",
    },
}


def _font(size, bold=False, italic=False):
    candidates = []

    if bold:
        candidates.extend([
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf",
        ])
    elif italic:
        candidates.extend([
            "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Italic.ttf",
            "/usr/share/fonts/truetype/liberation2/LiberationSerif-Italic.ttf",
        ])
    else:
        candidates.extend([
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
        ])

    for path in candidates:
        if Path(path).exists():
            return ImageFont.truetype(path, size)

    return ImageFont.load_default()


def _center(draw, y, text, font, fill, max_width=None, line_gap=12):
    if not text:
        return y

    lines = [text]

    if max_width:
        chars = max(12, int(max_width / (font.size * 0.55)))
        lines = textwrap.wrap(text, width=chars) or [text]

    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        tw = bbox[2] - bbox[0]
        draw.text(((W - tw) / 2, y), line, font=font, fill=fill)
        y += (bbox[3] - bbox[1]) + line_gap

    return y


def _draw_confetti(draw, theme):
    accent = theme["accent"]
    accent2 = theme["accent2"]
    for x, y, r, color in [
        (90, 130, 18, accent), (170, 230, 10, accent2), (900, 140, 16, accent),
        (840, 260, 9, accent2), (120, 1190, 13, accent), (920, 1230, 16, accent2),
        (210, 1320, 8, accent2), (800, 1360, 10, accent),
    ]:
        draw.ellipse((x-r, y-r, x+r, y+r), fill=color)

    for x, y, color in [
        (260, 120, accent), (770, 200, accent2), (125, 330, accent),
        (920, 410, accent), (160, 1030, accent2), (860, 1120, accent),
    ]:
        draw.rounded_rectangle((x, y, x+44, y+12), radius=6, fill=color)


def _draw_floral(draw, theme):
    accent = theme["accent"]
    accent2 = theme["accent2"]

    for cx, cy, scale in [(100, 135, 1.0), (930, 132, 0.9), (110, 1320, 0.8), (920, 1310, 1.0)]:
        for dx, dy in [(-22, 0), (22, 0), (0, -22), (0, 22)]:
            r = int(18 * scale)
            draw.ellipse((cx+dx-r, cy+dy-r, cx+dx+r, cy+dy+r), fill=accent2)
        r = int(18 * scale)
        draw.ellipse((cx-r, cy-r, cx+r, cy+r), fill=accent)
        draw.line((cx, cy+35, cx+45, cy+70), fill=accent, width=4)
        draw.ellipse((cx+30, cy+54, cx+70, cy+78), outline=accent, width=4)


def _draw_corporate(draw, theme):
    accent = theme["accent"]
    accent2 = theme["accent2"]

    draw.rectangle((0, 0, W, 22), fill=accent)
    draw.rectangle((0, H-22, W, H), fill=accent)

    draw.rounded_rectangle((70, 105, 245, 135), radius=15, fill=accent2)
    draw.rounded_rectangle((810, 105, 985, 135), radius=15, fill=accent2)
    draw.rounded_rectangle((70, 1340, 245, 1370), radius=15, fill=accent2)
    draw.rounded_rectangle((810, 1340, 985, 1370), radius=15, fill=accent2)


def _draw_classic(draw, theme):
    accent = theme["accent"]
    accent2 = theme["accent2"]

    draw.rounded_rectangle((62, 62, W-62, H-62), radius=38, outline=accent2, width=5)
    draw.rounded_rectangle((82, 82, W-82, H-82), radius=30, outline=accent, width=2)


def _draw_decor(draw, theme):
    decor = theme.get("decor", "classic")
    if decor == "floral":
        _draw_floral(draw, theme)
        _draw_classic(draw, theme)
    elif decor == "confetti":
        _draw_confetti(draw, theme)
    elif decor == "corporate":
        _draw_corporate(draw, theme)
    else:
        _draw_classic(draw, theme)


def _qr_image(url):
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=2,
    )
    qr.add_data(url or "http://localhost:8093")
    qr.make(fit=True)
    return qr.make_image(fill_color="black", back_color="white").convert("RGB")


def generate_front_cover():
    config = get_config()

    event_type = config.get("EVENT_TYPE", "custom")
    theme = THEMES.get(event_type, THEMES["custom"])

    app_name = config.get("APP_NAME", "Event Photo Missions")
    event_date = config.get("EVENT_DATE", "Event date")
    public_url = config.get("PUBLIC_BASE_URL", "http://localhost:8093")
    event_label = config.get("EVENT_LABEL", "evento")

    img = Image.new("RGB", (W, H), theme["bg"])
    draw = ImageDraw.Draw(img)

    _draw_decor(draw, theme)

    draw.rounded_rectangle((135, 160, W-135, 1270), radius=46, fill="#ffffff")

    y = 220
    y = _center(draw, y, theme["label"], _font(36, bold=True), theme["accent"], max_width=760, line_gap=18)

    y += 42
    y = _center(draw, y, app_name, _font(74, bold=True), theme["text"], max_width=760, line_gap=18)

    y += 8
    y = _center(draw, y, event_date, _font(34), theme["soft"], max_width=760, line_gap=20)

    y += 44
    draw.line((260, y, W-260, y), fill=theme["accent2"], width=4)

    y += 52
    y = _center(draw, y, theme["phrase"], _font(34, italic=True), theme["soft"], max_width=720, line_gap=14)

    y += 50
    qr = _qr_image(public_url)
    qr = qr.resize((350, 350))
    qr_x = (W - 350) // 2
    draw.rounded_rectangle((qr_x-26, y-26, qr_x+376, y+376), radius=28, fill="#ffffff", outline=theme["accent2"], width=5)
    img.paste(qr, (qr_x, y))

    y += 400
    y = _center(draw, y, "Escanea el QR", _font(34, bold=True), theme["text"], max_width=700, line_gap=10)
    y = _center(draw, y, f"y participa en las misiones del {event_label}", _font(28), theme["soft"], max_width=760, line_gap=10)

    draw.rounded_rectangle((180, 1320, W-180, 1382), radius=31, fill=theme["accent"])
    _center(draw, 1332, "Ver misiones · Subir fotos · Ranking", _font(27, bold=True), "#ffffff", max_width=700)

    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    img.save(OUTPUT, quality=95)

    return OUTPUT

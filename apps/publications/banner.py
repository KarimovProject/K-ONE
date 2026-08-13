import io
import textwrap

from django.core.files.base import ContentFile
from PIL import Image, ImageDraw, ImageFont

from apps.events.services.qr import generate_qr_code_png
from apps.publications.models import Publication
from apps.publications.rendering import public_event_url

SIZES = {
    "telegram": (1280, 720),
    "instagram_portrait": (1080, 1350),
    "instagram_square": (1080, 1080),
    "instagram_story": (1080, 1920),
}


def _font(size: int, bold: bool = False):
    names = ("segoeuib.ttf", "arialbd.ttf") if bold else ("segoeui.ttf", "arial.ttf")
    for name in names:
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def generate_banner(publication: Publication, variant: str | None = None) -> bytes:
    variant = variant or (
        "telegram"
        if publication.platform == Publication.Platform.TELEGRAM_CHANNEL
        else "instagram_portrait"
    )
    width, height = SIZES[variant]
    image = Image.new("RGB", (width, height), "#07172f")
    draw = ImageDraw.Draw(image)
    for y in range(height):
        ratio = y / max(height - 1, 1)
        draw.line((0, y, width, y), fill=(7, int(23 + 34 * ratio), int(47 + 55 * ratio)))
    accent = "#22d3ee" if publication.banner_template != "emergency" else "#f97360"
    draw.ellipse((width * 0.68, -height * 0.18, width * 1.1, height * 0.5), outline=accent, width=4)
    draw.ellipse((width * 0.73, -height * 0.1, width, height * 0.35), outline="#2563eb", width=2)
    margin = int(width * 0.075)
    draw.text(
        (margin, margin), "IEMS  •  INTERNATIONAL EVENTS", font=_font(23, True), fill="#67e8f9"
    )
    max_chars = 25 if width <= 1080 else 34
    title = textwrap.wrap(publication.headline, width=max_chars)[:4]
    title_font = _font(62 if height <= 1080 else 68, True)
    y = int(height * 0.23)
    for line in title:
        draw.text((margin, y), line, font=title_font, fill="#f8fafc")
        y += int(title_font.size * 1.14)
    event = publication.event
    detail_font = _font(28, True)
    y = max(y + 24, int(height * 0.62))
    draw.text(
        (margin, y),
        f"{event.planned_date:%d.%m.%Y}  •  {event.start_time:%H:%M}",
        font=detail_font,
        fill="#f8fafc",
    )
    draw.text((margin, y + 46), event.venue.localized_name[:58], font=_font(25), fill="#cbd5e1")
    if publication.include_qr:
        qr = Image.open(io.BytesIO(generate_qr_code_png(public_event_url(publication)))).convert(
            "RGB"
        )
        qr_size = int(min(width, height) * 0.18)
        qr.thumbnail((qr_size, qr_size))
        x, qy = width - margin - qr.width, height - margin - qr.height
        image.paste(qr, (x, qy))
        label = {"uz": "Dastur uchun QR", "ru": "QR программы", "en": "Scan for program"}
        draw.text(
            (x, qy - 34),
            label.get(publication.language, label["uz"]),
            font=_font(20, True),
            fill="#f8fafc",
        )
    if publication.include_sponsors:
        logo_x = margin
        logo_y = height - margin - 56
        for sponsor in publication.event.sponsors.exclude(logo="")[:4]:
            try:
                with sponsor.logo.open("rb") as source:
                    logo = Image.open(source).convert("RGBA")
                    logo.thumbnail((110, 48))
                    image.paste(logo, (logo_x, logo_y), logo)
                    logo_x += logo.width + 20
            except (OSError, ValueError):
                continue
    buffer = io.BytesIO()
    image.save(buffer, "PNG", optimize=True)
    return buffer.getvalue()


def save_banner(publication: Publication, variant: str | None = None) -> None:
    content = generate_banner(publication, variant)
    publication.banner.save(f"{publication.id}.png", ContentFile(content), save=False)
    publication.save(update_fields=("banner", "updated_at"))

import io

import qrcode
import qrcode.image.svg


def generate_qr_code_png(data: str) -> bytes:
    """Generate QR code as PNG image bytes."""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=3,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="#07172f", back_color="#ffffff")
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return buffer.getvalue()


def generate_qr_code_svg(data: str) -> str:
    """Generate QR code as SVG XML string."""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=3,
        image_factory=qrcode.image.svg.SvgPathImage,
    )
    qr.add_data(data)
    qr.make(fit=True)

    buffer = io.BytesIO()
    img = qr.make_image()
    img.save(buffer)
    return buffer.getvalue().decode("utf-8")

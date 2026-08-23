from PIL import Image

def clean_pure_3d_emblem():
    src = Image.open('static/img/k-one/k-one-3d-pure.png').convert('RGBA')
    w, h = src.size
    pixels = src.load()

    out = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    out_pixels = out.load()

    for y in range(h):
        for x in range(w):
            r, g, b, _ = pixels[x, y]

            # Letters K-ONE: y >= 270, x from 55 to 520
            if y >= 270:
                if (50 <= x <= 525):
                    delta_b = b - 52
                    delta_g = g - 24
                    delta_r = r - 3
                    strength = max(0, delta_b * 3.5, delta_g * 5.0, delta_r * 6.0)
                    if b > 48:
                        strength = max(strength, (b - 45) * 5.0)
                    if strength > 5:
                        alpha = int(min(255, strength * 1.8))
                        out_pixels[x, y] = (r, g, b, alpha)
            else:
                # Calendar Emblem: y < 270, x from 145 to 445, y from 35 to 265
                # Rings at x ~190..215 and x ~345..370, y from 35 to 80
                in_rings = ((185 <= x <= 220 or 340 <= x <= 375) and (35 <= y <= 80))
                in_calendar_body = (145 <= x <= 445 and 55 <= y <= 265)

                if in_rings or in_calendar_body:
                    delta_b = b - 52
                    delta_g = g - 24
                    delta_r = r - 3
                    strength = max(0, delta_b * 3.5, delta_g * 5.0, delta_r * 6.0)
                    if b > 50:
                        strength = max(strength, (b - 48) * 4.5)
                    if strength > 5:
                        alpha = int(min(255, strength * 1.8))
                        out_pixels[x, y] = (r, g, b, alpha)

    bbox = out.getbbox()
    cropped = out.crop(bbox)
    cropped.save('static/img/k-one/k-one-3d-pure-trans.png', 'PNG', optimize=True)
    print("Saved clean k-one-3d-pure-trans.png with size:", cropped.size)

    # Test composite over dark navy background #071A33
    test_bg = Image.new('RGBA', (700, 500), (7, 26, 51, 255))
    pos = ((700 - cropped.width) // 2, (500 - cropped.height) // 2)
    test_bg.alpha_composite(cropped, pos)
    test_bg.save('static/img/k-one/test_pure_trans_composite.png')
    print("Saved test_pure_trans_composite.png")

if __name__ == '__main__':
    clean_pure_3d_emblem()

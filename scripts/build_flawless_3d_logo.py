from PIL import Image

def build_flawless_3d_logo():
    src = Image.open('static/img/k-one/k-one-3d-pure.png').convert('RGBA')
    w, h = src.size
    pixels = src.load()

    out = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    out_pixels = out.load()

    for y in range(h):
        for x in range(w):
            r, g, b, _ = pixels[x, y]

            # Key feature metrics
            max_c = max(r, g, b)
            min_c = min(r, g, b)
            cyan_score = max(0, g - r) + max(0, b - r)

            # The artwork consists of:
            # 1. Glowing cyan lines / -ONE / diagonal K: max_c > 120, cyan_score > 60
            # 2. Medium blue glossy highlights: max_c > 75, b > 70
            # 3. Traditional pattern: white/cyan/blue details
            # 4. Vertical stem of K / K- letter: subtle navy 3D shape

            # Background is very dark navy (r <= 5, g <= 28, b <= 65) with low variance
            is_bg = (r <= 6 and g <= 30 and b <= 68 and max_c <= 68 and cyan_score <= 45)

            if is_bg:
                out_pixels[x, y] = (0, 0, 0, 0)
            else:
                # Calculate alpha based on how far it is from background
                if max_c > 110 or cyan_score > 70:
                    # Solid bright foreground
                    out_pixels[x, y] = (r, g, b, 255)
                elif max_c > 70 or cyan_score > 48:
                    # Antialiased edge or subtle blue 3D body
                    alpha_ratio = min(1.0, (max_c - 50) / 50.0)
                    alpha = int(255 * alpha_ratio)
                    out_pixels[x, y] = (r, g, b, max(120, alpha))
                else:
                    alpha = int(255 * min(1.0, (max_c - 30) / 40.0))
                    if alpha > 20:
                        out_pixels[x, y] = (r, g, b, alpha)
                    else:
                        out_pixels[x, y] = (0, 0, 0, 0)

    # Soft feather outer 8px boundary
    for y in range(h):
        for x in range(w):
            r, g, b, a = out_pixels[x, y]
            if a > 0:
                dx = min(x, w - 1 - x)
                dy = min(y, h - 1 - y)
                min_d = min(dx, dy)
                if min_d < 8:
                    out_pixels[x, y] = (r, g, b, int(a * (min_d / 8.0)))

    out.save('static/img/k-one/k-one-3d-flawless.png', 'PNG', optimize=True)
    print("Saved k-one-3d-flawless.png")

    # Test composite over dark navy background #071A33
    test_bg = Image.new('RGBA', (800, 600), (7, 26, 51, 255))
    pos = ((800 - w) // 2, (600 - h) // 2)
    test_bg.alpha_composite(out, pos)
    test_bg.save('static/img/k-one/test_flawless_composite.png')
    print("Saved test_flawless_composite.png")

if __name__ == '__main__':
    build_flawless_3d_logo()

from PIL import Image

def create_pure_transparent_3d_logo():
    src = Image.open('static/img/k-one/k-one-3d-pure.png').convert('RGBA')
    w, h = src.size
    pixels = src.load()

    out = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    out_pixels = out.load()

    # Background color reference
    bg_r, bg_g, bg_b = 0, 18, 48

    for y in range(h):
        for x in range(w):
            r, g, b, _ = pixels[x, y]

            # Brightness and color distance from background
            brightness = max(r, g, b)
            dist = ((r - bg_r)**2 + (g - bg_g)**2 + (b - bg_b)**2)**0.5

            # Cyan / Blue intensity
            cyan_intensity = max(0, g - r) + max(0, b - r)

            if dist < 10 and cyan_intensity < 25:
                # Pure background
                out_pixels[x, y] = (0, 0, 0, 0)
            elif dist < 35 and cyan_intensity < 40:
                # Soft transition from background
                alpha_factor = (dist - 10) / 25.0
                alpha = int(255 * (alpha_factor ** 1.5))
                out_pixels[x, y] = (r, g, b, alpha)
            else:
                # Strong foreground / glow / letters
                if brightness > 120 or cyan_intensity > 70:
                    out_pixels[x, y] = (r, g, b, 255)
                else:
                    alpha = min(255, int(150 + dist * 2.5))
                    out_pixels[x, y] = (r, g, b, alpha)

    # Feather outer 20px
    feather = 20.0
    for y in range(h):
        for x in range(w):
            r, g, b, a = out_pixels[x, y]
            if a > 0:
                dx = min(x, w - 1 - x)
                dy = min(y, h - 1 - y)
                min_d = min(dx, dy)
                if min_d < feather:
                    edge_f = (min_d / feather) ** 1.5
                    out_pixels[x, y] = (r, g, b, int(a * edge_f))

    out.save('static/img/k-one/k-one-3d-transparent.png', 'PNG', optimize=True)
    print("Saved static/img/k-one/k-one-3d-transparent.png with size:", out.size)

    # Test composite over dark navy background #071A33
    test_bg = Image.new('RGBA', (800, 700), (7, 26, 51, 255))
    pos = ((800 - w) // 2, (700 - h) // 2)
    test_bg.alpha_composite(out, pos)
    test_bg.save('static/img/k-one/test_composite_3d_navy.png')
    print("Saved test_composite_3d_navy.png")

if __name__ == '__main__':
    create_pure_transparent_3d_logo()

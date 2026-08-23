from PIL import Image

def build_compact_hero_art():
    src_path = r'C:\Users\User\.gemini\antigravity-ide\brain\9eec15eb-0f56-460c-8293-57d12a473cb6\.user_uploaded\media_1786969906369.png'
    img = Image.open(src_path).convert('RGBA')
    w, h = img.size
    pixels = img.load()

    # 1. Inpaint the small duplicate text at y=602..636
    y_start = 602
    y_end = 636
    for y in range(y_start, y_end + 1):
        t = (y - y_start) / float(y_end - y_start)
        for x in range(w):
            top_p = pixels[x, y_start]
            bot_p = pixels[x, y_end]
            new_r = int(top_p[0] * (1 - t) + bot_p[0] * t)
            new_g = int(top_p[1] * (1 - t) + bot_p[1] * t)
            new_b = int(top_p[2] * (1 - t) + bot_p[2] * t)
            pixels[x, y] = (new_r, new_g, new_b, 255)

    # 2. Smoothly fade the outer 60px edges into #01112D (1, 17, 45)
    target_r, target_g, target_b = 1, 17, 45
    feather = 60.0
    for y in range(h):
        for x in range(w):
            r, g, b, a = pixels[x, y]
            dx = min(x, w - 1 - x)
            dy = min(y, h - 1 - y)
            min_d = min(dx, dy)
            if min_d < feather:
                t = (min_d / feather) ** 1.3
                new_r = int(r * t + target_r * (1 - t))
                new_g = int(g * t + target_g * (1 - t))
                new_b = int(b * t + target_b * (1 - t))
                pixels[x, y] = (new_r, new_g, new_b, 255)

    dst_path = 'static/img/k-one/k-one-login-hero-art.png'
    img.save(dst_path, 'PNG', optimize=True)
    print(f"Saved compact feathered hero art to {dst_path}")

    # Test composite on 960x1080 canvas (desktop left panel)
    panel = Image.new('RGBA', (960, 1080), (1, 17, 45, 255))
    # Resize artwork to compact size (width=460px, height=690px)
    compact_size = (460, int(460 * h / w))
    resized_art = img.resize(compact_size, Image.Resampling.LANCZOS)
    pos = ((960 - compact_size[0]) // 2, (1080 - compact_size[1]) // 2)
    panel.alpha_composite(resized_art, pos)
    panel.save('static/img/k-one/test_panel_compact.png')
    print("Saved test_panel_compact.png")

if __name__ == '__main__':
    build_compact_hero_art()

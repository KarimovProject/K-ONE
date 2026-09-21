from PIL import Image

def create_feathered_transparent_hero():
    src_path = r'C:\Users\User\.gemini\antigravity-ide\brain\9eec15eb-0f56-460c-8293-57d12a473cb6\.user_uploaded\media_1786969906369.png'
    img = Image.open(src_path).convert('RGBA')
    w, h = img.size
    pixels = img.load()

    # 1. Inpaint duplicate text at y=602..636
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

    # 2. Feather the alpha to 0 for the outer 80px
    feather = 80.0
    for y in range(h):
        for x in range(w):
            r, g, b, _ = pixels[x, y]
            dx = min(x, w - 1 - x)
            dy = min(y, h - 1 - y)
            min_d = min(dx, dy)
            if min_d < feather:
                edge_factor = (min_d / feather) ** 1.6
                pixels[x, y] = (r, g, b, int(255 * edge_factor))
            else:
                pixels[x, y] = (r, g, b, 255)

    dst_path = 'static/img/k-one/k-one-login-hero-art.png'
    img.save(dst_path, 'PNG', optimize=True)
    print(f"Saved feathered transparent hero to {dst_path}")

    # Test composite on 960x1080 panel with matching gradient
    panel = Image.new('RGBA', (960, 1080), (1, 14, 38, 255))
    compact_size = (440, int(440 * h / w))
    resized_art = img.resize(compact_size, Image.Resampling.LANCZOS)
    pos = ((960 - compact_size[0]) // 2, (1080 - compact_size[1]) // 2)
    panel.alpha_composite(resized_art, pos)
    panel.save('static/img/k-one/test_panel_gradient.png')
    print("Saved test_panel_gradient.png")

if __name__ == '__main__':
    create_feathered_transparent_hero()

from PIL import Image

def prepare_perfect_hero_art():
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

    # 2. Feather the outer 40px edges to transparent alpha (0) so it blends 100% with any background
    feather = 40.0
    for y in range(h):
        for x in range(w):
            r, g, b, a = pixels[x, y]
            dx = min(x, w - 1 - x)
            dy = min(y, h - 1 - y)
            min_d = min(dx, dy)
            if min_d < feather:
                edge_factor = (min_d / feather) ** 1.5
                new_a = int(255 * edge_factor)
                pixels[x, y] = (r, g, b, new_a)

    dst_path = 'static/img/k-one/k-one-login-hero-art.png'
    img.save(dst_path, 'PNG', optimize=True)
    print(f"Saved feathered seamless hero art to {dst_path}")

    # Also test composite over dark background
    test_bg = Image.new('RGBA', (900, 1100), (0, 14, 39, 255))
    pos = ((900 - w) // 2, (1100 - h) // 2)
    test_bg.alpha_composite(img, pos)
    test_bg.save('static/img/k-one/test_hero_art_full.png')
    print("Saved test_hero_art_full.png")

if __name__ == '__main__':
    prepare_perfect_hero_art()

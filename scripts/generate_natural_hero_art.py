from PIL import Image

def generate_natural_hero_art():
    src_path = r'C:\Users\User\.gemini\antigravity-ide\brain\9eec15eb-0f56-460c-8293-57d12a473cb6\.user_uploaded\media_1786969906369.png'
    img = Image.open(src_path).convert('RGB')
    w, h = img.size
    pixels = img.load()

    # Inpaint the small duplicate text at y=602..636
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
            pixels[x, y] = (new_r, new_g, new_b)

    dst_path = 'static/img/k-one/k-one-login-hero-art.png'
    img.save(dst_path, 'PNG', optimize=True)
    print(f"Saved natural seamless hero art to {dst_path}")

if __name__ == '__main__':
    generate_natural_hero_art()

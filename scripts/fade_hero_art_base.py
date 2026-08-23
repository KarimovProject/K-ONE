import os
from PIL import Image

# 1. Ensure k-one-login-hero-art.png has smooth feathered edges all around
src_path = r'C:\Users\User\.gemini\antigravity-ide\brain\9eec15eb-0f56-460c-8293-57d12a473cb6\.user_uploaded\media_1786969906369.png'
img = Image.open(src_path).convert('RGBA')
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
        pixels[x, y] = (new_r, new_g, new_b, 255)

# Smoothly fade all outer 50px of the image to the exact base color (0, 14, 39)
base_r, base_g, base_b = 0, 14, 39
feather = 50.0

for y in range(h):
    for x in range(w):
        r, g, b, a = pixels[x, y]
        dx = min(x, w - 1 - x)
        dy = min(y, h - 1 - y)
        min_d = min(dx, dy)
        if min_d < feather:
            t = (min_d / feather) ** 1.3
            new_r = int(r * t + base_r * (1 - t))
            new_g = int(g * t + base_g * (1 - t))
            new_b = int(b * t + base_b * (1 - t))
            pixels[x, y] = (new_r, new_g, new_b, 255)

dst_path = 'static/img/k-one/k-one-login-hero-art.png'
img.save(dst_path, 'PNG', optimize=True)
print("Updated k-one-login-hero-art.png with seamless base color fading.")

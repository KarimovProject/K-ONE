from PIL import Image

def extract_compact_3d_emblem():
    # Source is owner uploaded illuminated art
    src_path = r'C:\Users\User\.gemini\antigravity-ide\brain\9eec15eb-0f56-460c-8293-57d12a473cb6\.user_uploaded\media_1786969906369.png'
    src = Image.open(src_path).convert('RGBA')

    # Crop just the calendar + K-ONE letters
    # Calendar top: y=175, K-ONE bottom: y=595, x: 55..625
    cropped = src.crop((55, 175, 625, 595))
    w, h = cropped.size
    pixels = cropped.load()

    out = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    out_pixels = out.load()

    for y in range(h):
        for x in range(w):
            r, g, b, a = pixels[x, y]
            brightness = max(r, g, b)
            cyan_diff = (g - r) + (b - r)

            # Letters K-ONE region
            if y >= 270:
                if 50 <= x <= 520:
                    delta = max(0, (b - 50) * 3.5, (g - 24) * 5.0, (r - 4) * 6.0)
                    if b > 48:
                        delta = max(delta, (b - 45) * 5.0)
                    if delta > 4:
                        alpha = int(min(255, delta * 1.8))
                        out_pixels[x, y] = (r, g, b, alpha)
            else:
                # Calendar emblem: rings & frame
                in_rings = ((185 <= x <= 220 or 340 <= x <= 375) and (35 <= y <= 80))
                in_calendar = (145 <= x <= 445 and 55 <= y <= 265)
                if in_rings or in_calendar:
                    delta = max(0, (b - 50) * 3.5, (g - 24) * 5.0, (r - 4) * 6.0)
                    if b > 48:
                        delta = max(delta, (b - 46) * 4.5)
                    if delta > 4:
                        alpha = int(min(255, delta * 1.8))
                        out_pixels[x, y] = (r, g, b, alpha)

    # Trim empty bounds
    bbox = out.getbbox()
    trimmed = out.crop(bbox)

    # Save compact transparent 3D emblem
    dst_path = 'static/img/k-one/k-one-3d-compact.png'
    trimmed.save(dst_path, 'PNG', optimize=True)
    print(f"Saved {dst_path} with size {trimmed.size}")

    # Test composite over dark navy
    test_bg = Image.new('RGBA', (600, 500), (1, 17, 45, 255))
    pos = ((600 - trimmed.width) // 2, (500 - trimmed.height) // 2)
    test_bg.alpha_composite(trimmed, pos)
    test_bg.save('static/img/k-one/test_compact_composite.png')
    print("Saved test_compact_composite.png")

if __name__ == '__main__':
    extract_compact_3d_emblem()

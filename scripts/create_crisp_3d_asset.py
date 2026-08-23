from PIL import Image, ImageFilter

def create_crisp_3d_asset():
    src = Image.open('static/img/k-one/k-one-3d-pure.png').convert('RGBA')
    w, h = src.size
    pixels = src.load()

    # We want:
    # 1. Letters 'K-ONE' (y > 280)
    # 2. Calendar emblem (y <= 290)

    out = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    out_pixels = out.load()

    for y in range(h):
        for x in range(w):
            r, g, b, _ = pixels[x, y]
            brightness = max(r, g, b)
            cyan_diff = (g - r) + (b - r)

            # Letters K-ONE region (y >= 270)
            if y >= 270:
                if brightness > 55 or cyan_diff > 40:
                    out_pixels[x, y] = (r, g, b, 255)
                elif brightness > 35 or cyan_diff > 25:
                    alpha = int(255 * (brightness - 35) / 20.0)
                    out_pixels[x, y] = (r, g, b, max(0, min(255, alpha)))
                else:
                    out_pixels[x, y] = (0, 0, 0, 0)
            else:
                # Calendar emblem region (y < 270)
                # Calendar outline coordinates are approx:
                # x between 110 and 460, y between 25 and 265
                is_calendar_area = (105 <= x <= 465 and 20 <= y <= 270)

                if is_calendar_area:
                    if brightness > 50 or cyan_diff > 35:
                        out_pixels[x, y] = (r, g, b, 255)
                    elif brightness > 30 or cyan_diff > 20:
                        alpha = int(255 * (brightness - 30) / 20.0)
                        out_pixels[x, y] = (r, g, b, max(0, min(255, alpha)))
                    else:
                        out_pixels[x, y] = (0, 0, 0, 0)
                else:
                    out_pixels[x, y] = (0, 0, 0, 0)

    # Crop to content bounding box
    bbox = out.getbbox()
    print('Artwork bbox:', bbox)
    cropped = out.crop(bbox)

    cropped.save('static/img/k-one/k-one-3d-clean.png', 'PNG', optimize=True)
    print(f"Saved static/img/k-one/k-one-3d-clean.png with size {cropped.size}")

    # Test composite over dark navy background #071A33
    test_bg = Image.new('RGBA', (700, 550), (7, 26, 51, 255))
    pos = ((700 - cropped.width) // 2, (550 - cropped.height) // 2)
    test_bg.alpha_composite(cropped, pos)
    test_bg.save('static/img/k-one/test_clean_3d_composite.png')
    print("Saved test_clean_3d_composite.png")

if __name__ == '__main__':
    create_crisp_3d_asset()

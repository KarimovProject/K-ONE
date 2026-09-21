from PIL import Image

def generate_perfect_transparent_logo():
    src_path = 'static/img/k-one/k-one-official.png'
    dst_path = 'static/img/k-one/k-one-official-transparent.png'

    orig = Image.open(src_path).convert('RGBA')
    width, height = orig.size
    orig_pixels = orig.load()

    out_img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    out_pixels = out_img.load()

    for y in range(height):
        for x in range(width):
            r, g, b, _ = orig_pixels[x, y]

            # Check for pure white/near-white background
            min_c = min(r, g, b)
            max_c = max(r, g, b)
            avg_c = (r + g + b) / 3.0

            # Color difference (saturation)
            diff = max_c - min_c

            if min_c >= 244 and diff <= 6:
                # Pure background canvas / white open area
                out_pixels[x, y] = (0, 0, 0, 0)
            elif min_c >= 190 and diff <= 25:
                # Neutral anti-aliased edge fading to white
                # Compute alpha from distance from pure white (255)
                # At min_c = 244, alpha = 0; at min_c = 190, alpha = 255
                alpha_ratio = max(0.0, min(1.0, (244.0 - avg_c) / (244.0 - 190.0)))
                alpha = int(alpha_ratio * 255)

                if alpha > 0:
                    # Unmultiply white to recover true foreground color
                    fg_r = max(0, min(255, int((r - 255 * (1 - alpha_ratio)) / alpha_ratio)))
                    fg_g = max(0, min(255, int((g - 255 * (1 - alpha_ratio)) / alpha_ratio)))
                    fg_b = max(0, min(255, int((b - 255 * (1 - alpha_ratio)) / alpha_ratio)))
                    out_pixels[x, y] = (fg_r, fg_g, fg_b, alpha)
                else:
                    out_pixels[x, y] = (0, 0, 0, 0)
            elif min_c >= 210 and diff > 25:
                # Colored anti-aliased edge (e.g. cyan/blue fading to white)
                # Compute alpha based on brightness
                alpha_ratio = max(0.0, min(1.0, (250.0 - min_c) / (250.0 - 160.0)))
                alpha = int(alpha_ratio * 255)
                if alpha > 0:
                    fg_r = max(0, min(255, int((r - 255 * (1 - alpha_ratio)) / alpha_ratio)))
                    fg_g = max(0, min(255, int((g - 255 * (1 - alpha_ratio)) / alpha_ratio)))
                    fg_b = max(0, min(255, int((b - 255 * (1 - alpha_ratio)) / alpha_ratio)))
                    out_pixels[x, y] = (fg_r, fg_g, fg_b, alpha)
                else:
                    out_pixels[x, y] = (0, 0, 0, 0)
            else:
                # Solid artwork pixel
                out_pixels[x, y] = (r, g, b, 255)

    out_img.save(dst_path, 'PNG', optimize=True)
    print(f"Successfully generated {dst_path} with size {out_img.size}")

    # Test composite over dark navy #071A33
    navy_bg = Image.new('RGBA', (width, height), (7, 26, 51, 255))
    composite = Image.alpha_composite(navy_bg, out_img)
    composite.save('static/img/k-one/test_composite_navy.png', 'PNG')
    print("Generated test_composite_navy.png for visual verification.")

if __name__ == '__main__':
    generate_perfect_transparent_logo()

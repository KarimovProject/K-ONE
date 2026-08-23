from PIL import Image

def generate_cropped_transparent_logo():
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

            min_c = min(r, g, b)
            max_c = max(r, g, b)
            avg_c = (r + g + b) / 3.0
            diff = max_c - min_c

            if min_c >= 244 and diff <= 6:
                out_pixels[x, y] = (0, 0, 0, 0)
            elif min_c >= 190 and diff <= 25:
                alpha_ratio = max(0.0, min(1.0, (244.0 - avg_c) / (244.0 - 190.0)))
                alpha = int(alpha_ratio * 255)
                if alpha > 0:
                    fg_r = max(0, min(255, int((r - 255 * (1 - alpha_ratio)) / alpha_ratio)))
                    fg_g = max(0, min(255, int((g - 255 * (1 - alpha_ratio)) / alpha_ratio)))
                    fg_b = max(0, min(255, int((b - 255 * (1 - alpha_ratio)) / alpha_ratio)))
                    out_pixels[x, y] = (fg_r, fg_g, fg_b, alpha)
                else:
                    out_pixels[x, y] = (0, 0, 0, 0)
            elif min_c >= 210 and diff > 25:
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
                out_pixels[x, y] = (r, g, b, 255)

    # Get bounding box of content
    bbox = out_img.getbbox()
    print('Content bbox:', bbox)
    # Add a small padding (12px)
    pad = 12
    crop_box = (
        max(0, bbox[0] - pad),
        max(0, bbox[1] - pad),
        min(width, bbox[2] + pad),
        min(height, bbox[3] + pad)
    )
    print('Cropped box:', crop_box)
    cropped_img = out_img.crop(crop_box)
    print('Cropped size:', cropped_img.size)
    cropped_img.save(dst_path, 'PNG', optimize=True)
    print(f"Saved cropped transparent logo to {dst_path}")

if __name__ == '__main__':
    generate_cropped_transparent_logo()

from PIL import Image
from collections import deque
import math

def create_transparent_logo():
    src_path = 'static/img/k-one/k-one-official.png'
    dst_path = 'static/img/k-one/k-one-official-transparent.png'

    img = Image.open(src_path).convert('RGBA')
    width, height = img.size
    pixels = img.load()

    # 1. Connected component BFS from borders for background
    visited = bytearray(width * height)
    queue = deque()

    def is_bg(r, g, b):
        return r >= 240 and g >= 240 and b >= 240

    for x in range(width):
        for y in [0, height - 1]:
            r, g, b, _ = pixels[x, y]
            if is_bg(r, g, b):
                idx = y * width + x
                if not visited[idx]:
                    visited[idx] = 1
                    queue.append((x, y))

    for y in range(height):
        for x in [0, width - 1]:
            idx = y * width + x
            if not visited[idx]:
                r, g, b, _ = pixels[x, y]
                if is_bg(r, g, b):
                    visited[idx] = 1
                    queue.append((x, y))

    while queue:
        cx, cy = queue.popleft()
        for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
            nx, ny = cx + dx, cy + dy
            if 0 <= nx < width and 0 <= ny < height:
                nidx = ny * width + nx
                if not visited[nidx]:
                    r, g, b, _ = pixels[nx, ny]
                    if is_bg(r, g, b):
                        visited[nidx] = 1
                        queue.append((nx, ny))

    # 2. Defringe and apply alpha
    out_img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    out_pixels = out_img.load()

    for y in range(height):
        for x in range(width):
            idx = y * width + x
            r, g, b, a = pixels[x, y]
            if visited[idx]:
                # Pure outer background
                out_pixels[x, y] = (0, 0, 0, 0)
            else:
                # Check if it borders a background pixel
                has_bg_neighbor = False
                for dx, dy in [(-1,0), (1,0), (0,-1), (0,1), (-1,-1), (1,1), (-1,1), (1,-1)]:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < width and 0 <= ny < height:
                        if visited[ny * width + nx]:
                            has_bg_neighbor = True
                            break

                if has_bg_neighbor and (r > 220 and g > 220 and b > 220):
                    # Soft edge anti-aliasing pixel: recover alpha from brightness
                    # Distance from white (255,255,255)
                    brightness = (r + g + b) / 3.0
                    alpha = max(0, min(255, int((255 - brightness) * (255 / (255 - 220)))))
                    # Defringe color towards the non-white part
                    out_pixels[x, y] = (r, g, b, alpha)
                else:
                    out_pixels[x, y] = (r, g, b, 255)

    out_img.save(dst_path, 'PNG', optimize=True)
    print(f"Created {dst_path} with size {out_img.size} and mode {out_img.mode}")

if __name__ == '__main__':
    create_transparent_logo()

from PIL import Image

def feather_illuminated_logo():
    img = Image.open('static/img/k-one/k-one-login-illuminated.png').convert('RGBA')
    w, h = img.size
    pixels = img.load()

    feather_dist = 28.0

    for y in range(h):
        for x in range(w):
            r, g, b, a = pixels[x, y]

            # Distance from 4 edges
            dx = min(x, w - 1 - x)
            dy = min(y, h - 1 - y)
            min_d = min(dx, dy)

            if min_d < feather_dist:
                edge_factor = (min_d / feather_dist) ** 1.5
                new_a = int(a * edge_factor)
                pixels[x, y] = (r, g, b, new_a)

    img.save('static/img/k-one/k-one-login-illuminated.png', 'PNG', optimize=True)
    print("Feathered edges of k-one-login-illuminated.png successfully!")

if __name__ == '__main__':
    feather_illuminated_logo()

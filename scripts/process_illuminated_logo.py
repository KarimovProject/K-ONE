from PIL import Image
import math

def create_transparent_illuminated_logo():
    src_path = r'C:\Users\User\.gemini\antigravity-ide\brain\9eec15eb-0f56-460c-8293-57d12a473cb6\.user_uploaded\media_1786969906369.png'
    src = Image.open(src_path).convert('RGBA')

    # 1. Exact crop of the illuminated logo (including slogan)
    # The logo in the uploaded 682x1024 image:
    # Rings top: y=95, slogan bottom: y=616
    # Left edge of K: x=40, Right edge of E: x=640
    # Let's find tight bounding box
    logo_crop = src.crop((35, 90, 647, 625))
    logo_crop.save('static/img/k-one/k-one-login-illuminated.png', 'PNG', optimize=True)
    print('Saved static/img/k-one/k-one-login-illuminated.png with size:', logo_crop.size)

    # 2. Also create the full login hero background art from the uploaded image
    # If the user wants the exact look with background network + illuminated logo:
    # The uploaded image is 682x1024, which fits the login hero side!
    src.save('static/img/k-one/k-one-login-hero-art.png', 'PNG', optimize=True)
    print('Saved static/img/k-one/k-one-login-hero-art.png with size:', src.size)

if __name__ == '__main__':
    create_transparent_illuminated_logo()

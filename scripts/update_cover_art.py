import os

with open('static/css/app.css', 'r', encoding='utf-8') as f:
    app_css = f.read()

app_css = app_css.replace(""".auth-hero-art-img {
  width: 100%;
  height: 100%;
  max-width: 680px;
  max-height: 980px;
  object-fit: contain;
  display: block;
  animation: fadeInScale 0.4s var(--ease-out);
}""", """.auth-hero-art-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: center;
  display: block;
  animation: fadeInScale 0.4s var(--ease-out);
}""")

with open('static/css/app.css', 'w', encoding='utf-8') as f:
    f.write(app_css)

print("Updated auth-hero-art-img to object-fit: cover for full-bleed edge-to-edge rendering.")

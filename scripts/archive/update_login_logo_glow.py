import os

with open('static/css/app.css', 'r', encoding='utf-8') as f:
    app_css = f.read()

app_css = app_css.replace(""".brand-logo-large {
  position: relative;
  z-index: 1;
  width: 100%;
  max-width: 400px;
  height: auto;
  object-fit: contain;
  display: block;
  transform: scale(1.3);
  transform-origin: left center;
  margin-left: 10px;
  animation: fadeInScale 0.4s var(--ease-out);
}""", """.brand-logo-large {
  position: relative;
  z-index: 1;
  width: 100%;
  max-width: 380px;
  height: auto;
  object-fit: contain;
  display: block;
  transform: scale(1.25);
  transform-origin: left center;
  margin-left: 6px;
  filter: drop-shadow(0 0 1px rgba(255, 255, 255, 0.4)) drop-shadow(0 0 18px rgba(22, 188, 235, 0.2));
  animation: fadeInScale 0.4s var(--ease-out);
}""")

with open('static/css/app.css', 'w', encoding='utf-8') as f:
    f.write(app_css)

print("Updated brand-logo-large with subtle luminous definition.")

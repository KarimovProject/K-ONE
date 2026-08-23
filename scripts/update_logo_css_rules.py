import os

# 1. Update public.css
with open('static/css/public.css', 'r', encoding='utf-8') as f:
    pub_css = f.read()

pub_css = pub_css.replace("""/* --- Logo --- */
.brand-logo-public {
  height: 62px;
  width: auto;
  max-width: 140px;
  object-fit: contain;
  display: block;
  transform: scale(1.35);
  transform-origin: left center;
  margin-left: 6px;
  transition: transform var(--duration-micro) var(--ease-out);
}""", """/* --- Logo --- */
.brand-logo-public {
  height: 48px;
  width: auto;
  max-width: 130px;
  object-fit: contain;
  display: block;
  transition: transform var(--duration-micro) var(--ease-out);
}""")

pub_css = pub_css.replace("""  .brand-logo-public {
    height: 52px;
    max-width: 115px;
    transform: scale(1.3);
    margin-left: 4px;
  }""", """  .brand-logo-public {
    height: 44px;
    max-width: 110px;
  }""")

pub_css = pub_css.replace("""  .brand-logo-public {
    height: 40px;
    max-width: 86px;
    transform: scale(1.25);
    margin-left: 2px;
  }""", """  .brand-logo-public {
    height: 36px;
    max-width: 80px;
  }""")

with open('static/css/public.css', 'w', encoding='utf-8') as f:
    f.write(pub_css)

# 2. Update app.css
with open('static/css/app.css', 'r', encoding='utf-8') as f:
    app_css = f.read()

app_css = app_css.replace(""".sidebar-logo {
  height: 42px;
  width: auto;
  max-width: 130px;
  object-fit: contain;
  display: block;
  transform: scale(1.3);
  transform-origin: left center;
  margin-left: 4px;
  margin-bottom: 2px;
}""", """.sidebar-logo {
  height: 36px;
  width: auto;
  max-width: 120px;
  object-fit: contain;
  display: block;
}""")

app_css = app_css.replace(""".brand-logo-large {
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
}""", """.brand-logo-large {
  width: 100%;
  max-width: 350px;
  max-height: 290px;
  height: auto;
  object-fit: contain;
  display: block;
  filter: drop-shadow(0 8px 24px rgba(0, 174, 239, 0.12));
  animation: fadeInScale 0.4s var(--ease-out);
}""")

app_css = app_css.replace(""".brand-logo-mobile {
    height: 68px;
    width: auto;
    max-width: 150px;
    object-fit: contain;
    transform: scale(1.35);
  }""", """.brand-logo-mobile {
    height: 56px;
    width: auto;
    max-width: 130px;
    object-fit: contain;
  }""")

with open('static/css/app.css', 'w', encoding='utf-8') as f:
    f.write(app_css)

print("Updated public.css and app.css logo display rules.")

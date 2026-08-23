import os

# 1. Update public.css
with open('static/css/public.css', 'r', encoding='utf-8') as f:
    pub_css = f.read()

pub_css = pub_css.replace("""/* --- Logo --- */
.brand-logo-public {
  height: 60px;
  width: auto;
  min-width: 110px;
  max-width: 140px;
  object-fit: contain;
  display: block;
  transition: transform var(--duration-micro) var(--ease-out);
}""", """/* --- Logo --- */
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
}""")

pub_css = pub_css.replace("""  .brand-logo-public {
    min-width: 95px;
    max-width: 110px;
    height: 52px;
  }""", """  .brand-logo-public {
    height: 52px;
    max-width: 115px;
    transform: scale(1.3);
    margin-left: 4px;
  }""")

pub_css = pub_css.replace("""  .brand-logo-public {
    min-width: 70px;
    max-width: 82px;
    height: 42px;
  }""", """  .brand-logo-public {
    height: 40px;
    max-width: 86px;
    transform: scale(1.25);
    margin-left: 2px;
  }""")

with open('static/css/public.css', 'w', encoding='utf-8') as f:
    f.write(pub_css)

# 2. Update app.css
with open('static/css/app.css', 'r', encoding='utf-8') as f:
    app_css = f.read()

app_css = app_css.replace(""".brand-logo-large {
  position: relative;
  z-index: 1;
  width: 100%;
  max-width: 360px;
  height: auto;
  object-fit: contain;
  display: block;
  animation: fadeInScale 0.4s var(--ease-out);
}""", """.brand-logo-large {
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
}""")

app_css = app_css.replace(""".sidebar-logo {
  height: 38px;
  width: auto;
  max-width: 130px;
  object-fit: contain;
  display: block;
}""", """.sidebar-logo {
  height: 42px;
  width: auto;
  max-width: 130px;
  object-fit: contain;
  display: block;
  transform: scale(1.3);
  transform-origin: left center;
  margin-left: 4px;
  margin-bottom: 2px;
}""")

app_css = app_css.replace(""".brand-logo-mobile {
    height: 60px;
    width: auto;
    max-width: 140px;
    object-fit: contain;
  }""", """.brand-logo-mobile {
    height: 68px;
    width: auto;
    max-width: 150px;
    object-fit: contain;
    transform: scale(1.35);
  }""")

# Add sr-only and mobile topbar rules to app.css
if ".sr-only" not in app_css:
    app_css += """
.sr-only {
  position: absolute !important;
  width: 1px !important;
  height: 1px !important;
  padding: 0 !important;
  margin: -1px !important;
  overflow: hidden !important;
  clip: rect(0, 0, 0, 0) !important;
  white-space: nowrap !important;
  border: 0 !important;
}

@media (max-width: 640px) {
  .topbar {
    padding: 0 16px;
    height: 56px;
  }
  .topbar-context {
    display: none;
  }
  .user-block,
  .admin-link,
  .public-view-link {
    display: none;
  }
  .menu-button {
    font-size: 24px;
    color: var(--color-text-title);
    padding: 4px;
    display: flex;
    align-items: center;
    justify-content: center;
  }
}
"""

with open('static/css/app.css', 'w', encoding='utf-8') as f:
    f.write(app_css)

print("Applied CSS polish for logos, sr-only, and mobile topbar.")

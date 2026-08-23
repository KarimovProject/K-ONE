import os

with open('static/css/app.css', 'r', encoding='utf-8') as f:
    app_css = f.read()

app_css = app_css.replace(""".auth-brand-panel {
  flex: 0 0 50%;
  background-color: #000E27;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 32px;
  color: #FFFFFF;
  overflow: hidden;
  box-sizing: border-box;
}

.auth-brand-art-box {
  width: 100%;
  max-width: 540px;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.auth-hero-art-img {
  width: 100%;
  max-width: 520px;
  max-height: 90vh;
  height: auto;
  object-fit: contain;
  display: block;
  animation: fadeInScale 0.4s var(--ease-out);
}""", """.auth-brand-panel {
  flex: 0 0 50%;
  background: #000E27;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
  color: #FFFFFF;
  overflow: hidden;
  box-sizing: border-box;
}

.auth-brand-art-box {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #000E27;
}

.auth-hero-art-img {
  width: 100%;
  height: 100%;
  max-width: 680px;
  max-height: 980px;
  object-fit: contain;
  display: block;
  animation: fadeInScale 0.4s var(--ease-out);
}""")

with open('static/css/app.css', 'w', encoding='utf-8') as f:
    f.write(app_css)

print("Updated app.css with seamless matching background.")

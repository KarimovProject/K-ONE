import os

with open('templates/registration/login.html', 'r', encoding='utf-8') as f:
    login_html = f.read()

login_html = login_html.replace(
    '<img src="{% static \'img/k-one/k-one-login-illuminated.png\' %}" alt="K-ONE Logo" class="brand-logo-mobile">',
    '<img src="{% static \'img/k-one/k-one-official-transparent.png\' %}" alt="K-ONE Logo" class="brand-logo-mobile">'
)

with open('templates/registration/login.html', 'w', encoding='utf-8') as f:
    f.write(login_html)

print("Updated mobile logo to use clean transparent asset.")

import re

with open(r"C:\IEMS\templates\events\calendar.html", "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace(r"{% trans \'Zal bo‘yicha\' %}", "{% trans 'Zal bo‘yicha' %}")
content = content.replace(r"{% trans \'Tadbir turi bo‘yicha\' %}", "{% trans 'Tadbir turi bo‘yicha' %}")
content = content.replace(r"{% trans \'Holat bo‘yicha\' %}", "{% trans 'Holat bo‘yicha' %}")

with open(r"C:\IEMS\templates\events\calendar.html", "w", encoding="utf-8") as f:
    f.write(content)

print("Fixed trans quotes.")

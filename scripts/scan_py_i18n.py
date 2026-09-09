import glob
import json
import re

import polib

pat_dq = re.compile(r'_\(\s*"((?:[^"\\]|\\.)*)"\s*\)')
pat_sq = re.compile(r"_\(\s*'((?:[^'\\]|\\.)*)'\s*\)")

strings = set()
for path in glob.glob("apps/**/*.py", recursive=True):
    with open(path, encoding="utf-8") as f:
        content = f.read()
    strings.update(pat_dq.findall(content))
    strings.update(pat_sq.findall(content))

print("total python _() strings:", len(strings))

result = {}
for lang in ["uz", "en", "ru", "tr"]:
    po = polib.pofile(f"locale/{lang}/LC_MESSAGES/django.po")
    ids = {e.msgid for e in po}
    missing = sorted(s for s in strings if s and s not in ids)
    result[lang] = missing
    print(lang, "missing", len(missing))

with open("scratch_py_missing.json", "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=1)

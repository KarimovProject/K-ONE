import polib
import os

def compile_locale(lang):
    po_path = rf"D:\Projects\K ONE\K ONE\locale\{lang}\LC_MESSAGES\django.po"
    mo_path = rf"D:\Projects\K ONE\K ONE\locale\{lang}\LC_MESSAGES\django.mo"
    po = polib.pofile(po_path)
    po.save_as_mofile(mo_path)
    print(f"Compiled {lang}")

compile_locale("uz")
compile_locale("ru")
compile_locale("en")
compile_locale("tr")

import polib
import os

def compile_locale(lang):
    po_path = rf"C:\IEMS\locale\{lang}\LC_MESSAGES\django.po"
    mo_path = rf"C:\IEMS\locale\{lang}\LC_MESSAGES\django.mo"
    po = polib.pofile(po_path)
    po.save_as_mofile(mo_path)
    print(f"Compiled {lang}")

compile_locale("ru")
compile_locale("en")

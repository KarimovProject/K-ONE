import os
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
sys.path.insert(0, os.getcwd())

import django
django.setup()

from django.contrib.auth import get_user_model
from playwright.sync_api import sync_playwright

User = get_user_model()
PORT = 8012
BASE = f"http://127.0.0.1:{PORT}"

def wait_server():
    for _ in range(80):
        try:
            with urllib.request.urlopen(f"{BASE}/accounts/login/", timeout=1) as response:
                if response.status == 200:
                    return
        except Exception:
            time.sleep(0.25)
    raise RuntimeError("Server did not start")

def check_page(page, path, viewports):
    page.goto(f"{BASE}{path}")
    page.wait_for_load_state("networkidle")
    
    results = {}
    
    # Check for bad selectors
    bad_selects = page.evaluate('''() => {
        return Array.from(document.querySelectorAll('select')).filter(s => !s.classList.contains('command-select') && !s.classList.contains('filter-select') && !s.classList.contains('form-control')).length;
    }''')
    bad_filter_bar = page.evaluate('''() => document.querySelectorAll('.filter-bar').length''')
    
    has_defects = False
    defects = []
    if bad_selects > 0:
        has_defects = True
        defects.append(f"{bad_selects} raw selects")
    if bad_filter_bar > 0:
        has_defects = True
        defects.append("legacy .filter-bar used")
        
    for vp_name, w, h in viewports:
        page.set_viewport_size({"width": w, "height": h})
        page.wait_for_timeout(100)
        
        scroll_width = page.evaluate("document.documentElement.scrollWidth")
        client_width = page.evaluate("document.documentElement.clientWidth")
        
        if scroll_width > client_width:
            results[vp_name] = "FAIL (Overflow)"
            has_defects = True
            defects.append(f"overflow at {vp_name}")
        else:
            # specifically check profile layout stretching
            if "profile" in path and w == 1920:
                profile_width = page.evaluate('''() => {
                    let el = document.querySelector('.profile-layout');
                    return el ? el.getBoundingClientRect().width : 0;
                }''')
                if profile_width > 1400:
                    results[vp_name] = "FAIL (Stretched)"
                    has_defects = True
                    defects.append("Profile stretched on 1920")
                else:
                    results[vp_name] = "PASS"
            else:
                results[vp_name] = "PASS"
                
    overall = "FAIL" if has_defects else "PASS"
    defects_str = ", ".join(defects) if defects else "None"
    
    return overall, defects_str, results

def main():
    # Setup user
    if not User.objects.filter(username="audit_admin").exists():
        admin = User.objects.create_superuser("audit_admin", password="AuditPassword123!", role=User.Role.SUPER_ADMIN)
    else:
        admin = User.objects.get(username="audit_admin")
        admin.set_password("AuditPassword123!")
        admin.save()

    server = subprocess.Popen(
        [sys.executable, "manage.py", "runserver", f"127.0.0.1:{PORT}", "--noreload"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    try:
        wait_server()
        
        viewports = [
            ("1920", 1920, 1080),
            ("1366", 1366, 768),
            ("1024", 1024, 768),
            ("390", 390, 844),
        ]
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(f"{BASE}/accounts/login/")
            page.fill("input[name=username]", "audit_admin")
            page.fill("input[name=password]", "AuditPassword123!")
            page.click("button[type=submit]")
            page.wait_for_load_state("networkidle")
            
            routes = {
                "EVENTS": "/events/",
                "CALENDAR": "/calendar/",
                "PROFILE": "/profile/",
                "MASTER_DATA": "/master-data/venues/",
            }
            
            print(f"{'PAGE':<25} | {'1920':<15} | {'1366':<15} | {'1024':<15} | {'390':<15} | {'STATUS':<6} | DEFECTS")
            print("-" * 110)
            
            for name, path in routes.items():
                overall, defects, res = check_page(page, path, viewports)
                print(f"{name:<25} | {res.get('1920'):<15} | {res.get('1366'):<15} | {res.get('1024'):<15} | {res.get('390'):<15} | {overall:<6} | {defects}")
                
            browser.close()
    finally:
        server.terminate()
        server.wait(timeout=5)

if __name__ == "__main__":
    main()

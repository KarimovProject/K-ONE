import asyncio
import os
import sys
import django
import datetime
from django.conf import settings

# Setup Django ORM
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")
django.setup()

from django.contrib.auth import get_user_model
from apps.events.models import Event, EventType
from apps.venues.models import Venue

User = get_user_model()
from playwright.async_api import async_playwright

BASE_URL = "http://10.34.12.2:8012"
SCREENSHOT_DIR = r"C:\IEMS\qa_screenshots\phase28_2a"

os.makedirs(SCREENSHOT_DIR, exist_ok=True)

async def login(page, username, password):
    await page.goto(f"{BASE_URL}/accounts/login/")
    await page.wait_for_load_state("networkidle")
    await page.fill("input[name='username']", username)
    await page.fill("input[name='password']", password)
    await page.click(".auth-submit-btn")
    await page.wait_for_load_state("networkidle")

async def logout(page):
    await page.context.clear_cookies()
    await page.goto(f"{BASE_URL}/")
    await page.wait_for_load_state("networkidle")

from asgiref.sync import sync_to_async

@sync_to_async
def cleanup_and_setup_users():
    Event.objects.filter(title__startswith="QA28").delete()
    User.objects.filter(username__startswith="qa_").delete()
    
    Venue.objects.filter(code="QA28").delete()
    venue = Venue.objects.create(
        name_en="QA28 Venue",
        code="QA28",
        capacity=10,
        working_start=datetime.time(8, 0),
        working_end=datetime.time(20, 0),
        display_enabled=True,
    )
    etype = EventType.objects.first()
    
    user, _ = User.objects.get_or_create(username="qa_user", defaults={"is_staff": True})
    user.set_password("password")
    user.role = User.Role.RESPONSIBLE_EMPLOYEE
    user.save()
    
    approver, _ = User.objects.get_or_create(username="qa_approver", defaults={"is_staff": True})
    approver.set_password("password")
    approver.role = User.Role.MANAGEMENT_RESPONSIBLE
    approver.save()
    
    admin, _ = User.objects.get_or_create(username="qa_admin", defaults={"is_staff": True, "is_superuser": True})
    admin.set_password("password")
    admin.role = User.Role.INTERNATIONAL_ADMIN
    admin.save()
    return user, approver, admin, venue, etype

@sync_to_async
def create_event(title, status, user, approver, venue, etype, date_str, start_hour, end_hour, priority="normal"):
    return Event.objects.create(
        title=title,
        status=status,
        responsible_employee=user,
        management_responsible=approver,
        venue=venue,
        event_type=etype,
        planned_date=date_str,
        start_time=datetime.time(start_hour, 0),
        end_time=datetime.time(end_hour, 0),
        priority=priority
    )

async def run():
    print("Starting Playwright verification...")
    user, approver, admin, venue, etype = await cleanup_and_setup_users()
    
    date_str = (datetime.date.today() + datetime.timedelta(days=1)).strftime("%Y-%m-%d")

    async with async_playwright() as p:
        b = await p.chromium.launch(headless=True)
        c = await b.new_context(ignore_https_errors=True, viewport={'width': 1920, 'height': 1080})
        
        page = await c.new_page()
        
        # 1. Approval Flow
        e1 = await create_event(
            title="QA28 Event 1",
            status=Event.Status.PENDING_APPROVAL,
            user=user,
            approver=approver,
            venue=venue,
            etype=etype,
            date_str=date_str,
            start_hour=10,
            end_hour=11,
            priority="normal"
        )
        
        print("Login as QA Admin to approve...")
        await login(page, "qa_admin", "password")
        
        await page.goto(f"{BASE_URL}/events/approvals/")
        await page.wait_for_load_state("networkidle")
        await page.screenshot(path=os.path.join(SCREENSHOT_DIR, "01_approval_center_1920.png"))
        
        await page.set_viewport_size({'width': 390, 'height': 844})
        await page.screenshot(path=os.path.join(SCREENSHOT_DIR, "02_approval_center_390.png"))
        await page.set_viewport_size({'width': 1920, 'height': 1080})
        
        await page.goto(f"{BASE_URL}/events/{e1.pk}/")
        await page.wait_for_load_state("networkidle")
        await page.screenshot(path=os.path.join(SCREENSHOT_DIR, "03_pending_event.png"))
        
        try:
            await page.click("[data-testid='approve-event-btn']", timeout=5000)
        except Exception as e:
            await page.screenshot(path=os.path.join(SCREENSHOT_DIR, "ERROR_approve_btn_missing.png"))
            with open("C:/IEMS/debug_page.html", "w", encoding="utf-8") as f:
                f.write(await page.content())
            print(f"Failed to find approve button: {e}")
            raise
            
        await page.wait_for_load_state("networkidle")
        await page.screenshot(path=os.path.join(SCREENSHOT_DIR, "04_approved_event.png"))
        # await logout(page)
        
        # 2. Rejection Flow
        print("Rejection Flow...")
        e2 = await create_event(
            title="QA28 Event 2",
            status=Event.Status.PENDING_APPROVAL,
            user=user,
            approver=approver,
            venue=venue,
            etype=etype,
            date_str=date_str,
            start_hour=12,
            end_hour=13,
            priority="normal"
        )

        await page.goto(f"{BASE_URL}/events/{e2.pk}/")
        await page.click("[data-testid='reject-event-btn']")
        await page.wait_for_timeout(500)
        await page.click("button:has-text('Confirm Rejection')")
        await page.wait_for_load_state("networkidle")
        await page.screenshot(path=os.path.join(SCREENSHOT_DIR, "05_reject_empty_reason_blocked.png"))
        
        await page.fill("textarea[name='reason']", "No time")
        await page.click("button:has-text('Confirm Rejection')")
        await page.wait_for_load_state("networkidle")
        await page.screenshot(path=os.path.join(SCREENSHOT_DIR, "06_rejected_event.png"))
        
        e3 = await create_event(
            title="QA28 Event 3",
            status=Event.Status.PENDING_APPROVAL,
            user=user,
            approver=approver,
            venue=venue,
            etype=etype,
            date_str=date_str,
            start_hour=12,
            end_hour=13,
            priority="normal"
        )
        await page.goto(f"{BASE_URL}/events/{e3.pk}/")
        await page.click("[data-testid='approve-event-btn']")
        await page.wait_for_load_state("networkidle")
        await page.screenshot(path=os.path.join(SCREENSHOT_DIR, "07_released_room_reused.png"))
        # await logout(page)
        
        # 4. Priority Override
        print("Override Flow...")
        e4 = await create_event(
            title="QA28 Event 4",
            status=Event.Status.APPROVED,
            user=user,
            approver=approver,
            venue=venue,
            etype=etype,
            date_str=date_str,
            start_hour=14,
            end_hour=15,
            priority="normal"
        )
        e5 = await create_event(
            title="QA28 Event 5",
            status=Event.Status.PENDING_APPROVAL,
            user=user,
            approver=approver,
            venue=venue,
            etype=etype,
            date_str=date_str,
            start_hour=14,
            end_hour=15,
            priority="emergency"
        )
        
        await logout(page)
        await login(page, "qa_approver", "password")
        await page.goto(f"{BASE_URL}/events/{e5.pk}/")
        await page.screenshot(path=os.path.join(SCREENSHOT_DIR, "08_priority_conflict.png"))
        override_btn = await page.query_selector("text=Override Conflict")
        if not override_btn:
            print("Override button hidden for non-authorized.")
            await page.screenshot(path=os.path.join(SCREENSHOT_DIR, "09_override_denied.png"))
        
        res = await page.request.post(f"{BASE_URL}/events/{e5.pk}/override/", data={"reason": "test"})
        print(f"Direct POST override status: {res.status}")
        
        await logout(page)
        
        await login(page, "qa_admin", "password")
        await page.goto(f"{BASE_URL}/events/{e5.pk}/")
        
        await page.click("[data-testid='override-event-btn']")
        await page.wait_for_load_state("networkidle")
        await page.screenshot(path=os.path.join(SCREENSHOT_DIR, "11_override_confirmation.png"))
        
        await page.click("button:has-text('Confirm Override')")
        await page.wait_for_load_state("networkidle")
        await page.screenshot(path=os.path.join(SCREENSHOT_DIR, "10_override_empty_reason_blocked.png"))
        
        await page.fill("textarea[name='reason']", "VIP meeting")
        await page.click("button:has-text('Confirm Override')")
        await page.wait_for_load_state("networkidle")
        await page.screenshot(path=os.path.join(SCREENSHOT_DIR, "12_override_completed.png"))
        
        await page.goto(f"{BASE_URL}/events/{e4.pk}/")
        await page.screenshot(path=os.path.join(SCREENSHOT_DIR, "13_displaced_event.png"))
        
        await page.goto(f"{BASE_URL}/events/{e5.pk}/")
        await page.screenshot(path=os.path.join(SCREENSHOT_DIR, "14_override_audit_history.png"))
        
        await b.close()
        print("Done Playwright")

if __name__ == "__main__":
    asyncio.run(run())

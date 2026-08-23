import requests

s = requests.Session()
login_url = "http://10.34.12.2:8012/accounts/login/"
res = s.get(login_url)
print(f"Login GET: {res.status_code}")

csrf_token = res.cookies.get("csrftoken")
res2 = s.post(login_url, data={
    "username": "acceptance_admin",
    "password": "K-ONE-admin-2026!",
    "csrfmiddlewaretoken": csrf_token
}, headers={"Referer": login_url})
print(f"Login POST: {res2.status_code} (URL: {res2.url})")

routes = [
    "/workspace/",
    "/events/",
    "/calendar/",
    "/venues/",
    "/master-data/event-types/",
    "/master-data/organizations/",
    "/master-data/sponsors/",
    "/master-data/speakers/",
    "/publications/",
    "/leadership/",
    "/reporting/"
]

for r in routes:
    url = f"http://10.34.12.2:8012{r}"
    r_res = s.get(url)
    print(f"GET {r}: {r_res.status_code}")

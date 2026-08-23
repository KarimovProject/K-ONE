import urllib.request
import urllib.parse
from http.cookiejar import CookieJar

cj = CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

login_url = "http://10.34.12.2:8012/accounts/login/"
res = opener.open(login_url)
print(f"Login GET: {res.status}")

csrf = ""
for cookie in cj:
    if cookie.name == "csrftoken":
        csrf = cookie.value

data = urllib.parse.urlencode({
    "username": "acceptance_admin",
    "password": "K-ONE-admin-2026!",
    "csrfmiddlewaretoken": csrf
}).encode("utf-8")

req = urllib.request.Request(login_url, data=data)
req.add_header("Referer", login_url)
res2 = opener.open(req)
print(f"Login POST: {res2.status} (URL: {res2.url})")

routes = [
    "/workspace/",
    "/events/",
    "/dashboard/calendar/",
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
    r_res = opener.open(url)
    print(f"GET {r}: {r_res.status}")

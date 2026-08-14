from django.contrib.auth import views as auth_views
from django.http import HttpResponse
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _

from config.rate_limit import clear_rate_limit, is_rate_limited


class ThrottledLoginView(auth_views.LoginView):
    def post(self, request, *args, **kwargs):
        username = request.POST.get("username", "").strip().lower()[:150]
        if is_rate_limited(request, "login", 10, 300, username):
            return render(
                request,
                "errors/429.html",
                {"message": _("Too many login attempts. Please try again later.")},
                status=429,
            )
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        # Successful authentication rotates the session key in Django's login().
        username = self.request.POST.get("username", "").strip().lower()[:150]
        clear_rate_limit(self.request, "login", username)
        return super().form_valid(form)


def error_400(request, exception=None):
    return render(request, "errors/400.html", status=400)


def error_403(request, exception=None):
    return render(request, "errors/403.html", status=403)


def error_404(request, exception=None):
    return render(request, "errors/404.html", status=404)


def error_500(request):
    return render(request, "errors/500.html", status=500)


def rate_limited_response(request, message=None) -> HttpResponse:
    return render(
        request,
        "errors/429.html",
        {"message": message or _("Too many requests. Please try again later.")},
        status=429,
    )

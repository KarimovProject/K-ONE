from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from apps.reporting.selectors import get_dashboard_shell_data


@login_required
def dashboard(request: HttpRequest) -> HttpResponse:
    return render(request, "dashboard.html", get_dashboard_shell_data())


from django.core.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.models import User
from apps.reporting.reports import report_context
from apps.reporting.selectors import allowed_report_sections, reporting_user_allowed


class ReportAPIView(APIView):
    section = "summary"

    def get(self, request):
        if not reporting_user_allowed(request.user):
            raise PermissionDenied
        if self.section not in allowed_report_sections(request.user):
            raise PermissionDenied
        form, _, report = report_context(request.query_params, request.user)
        if not report:
            return Response({"errors": form.errors}, status=400)
        data = report[self.section]
        if self.section == "attendance" and request.user.role == User.Role.LEADERSHIP_VIEWER:
            data = {key: value for key, value in data.items() if key != "highest"}
        return Response(data)

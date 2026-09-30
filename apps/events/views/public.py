
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import (
    DetailView,
    TemplateView,
)

from apps.attendance.services import (
    CHECKIN_COOKIE_NAME,
    get_or_create_browser_checkin_token,
    is_already_checked_in,
)
from apps.audit.services import log_audit_event
from apps.events.models import Event

# --- Phase 4 Program & Public Page Views ---

class PublicKioskView(TemplateView):
    template_name = "events/public_kiosk.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = timezone.now()
        today = now.date()
        
        events_today = Event.objects.filter(
            is_public_enabled=True,
            planned_date=today,
            status=Event.Status.APPROVED
        ).order_by('start_time').select_related("event_type", "venue")
        
        # We can also filter out events that are not publicly accessible if
        # there are other conditions (like checkin_status). But for now,
        # is_public_enabled=True and status=APPROVED is sufficient for the kiosk.
        
        context["events_today"] = events_today
        context["now"] = now
        return context

class PublicEventPageView(DetailView):
    model = Event
    template_name = "events/public_event_detail.html"
    context_object_name = "event"
    slug_field = "public_token"
    slug_url_kwarg = "public_token"

    def dispatch(self, request, *args, **kwargs):
        from config.rate_limit import is_rate_limited
        from config.views import rate_limited_response

        token = kwargs.get("public_token", "")
        if is_rate_limited(request, "public-event", 600, 60, token):
            return rate_limited_response(request)
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        token = self.kwargs.get("public_token")
        event = get_object_or_404(
            Event.objects.select_related("event_type", "venue").prefetch_related(
                "organizing_organizations", "sponsors", "program_items__speaker"
            ),
            public_token=token,
        )
        if not event.is_publicly_accessible:
            raise Http404(_("This event page is not currently published or unavailable."))
        return event

    def render_to_response(self, context, **response_kwargs):
        response = super().render_to_response(context, **response_kwargs)
        if not self.request.COOKIES.get(CHECKIN_COOKIE_NAME):
            token, _ = get_or_create_browser_checkin_token(self.request)
            response.set_cookie(
                CHECKIN_COOKIE_NAME,
                token,
                max_age=365 * 24 * 3600,
                samesite="Lax",
                httponly=True,
                secure=settings.SESSION_COOKIE_SECURE,
            )
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        event = self.object
        context["countdown_info"] = event.public_countdown_info
        context["program_source"] = event.program_source

        if event.program_source == Event.ProgramSource.PDF and event.program_pdf:
            context["has_pdf"] = True
            context["pdf_url"] = event.program_pdf.url
        else:
            context["has_pdf"] = False

        agenda_items = list(event.program_items.all())
        context["agenda_items"] = agenda_items

        speakers = []
        seen_speaker_ids = set()
        for item in agenda_items:
            sp = item.speaker
            if sp and sp.public_profile_enabled and sp.pk not in seen_speaker_ids:
                seen_speaker_ids.add(sp.pk)
                speakers.append(sp)
        context["speakers"] = speakers

        scheme = self.request.scheme
        host = self.request.get_host()
        context["public_url"] = f"{scheme}://{host}/event/{event.public_token}/"

        # Phase 5 Attendance context
        status_info = event.checkin_status()
        checked_in, _ = is_already_checked_in(event, self.request)
        context["checkin_status"] = status_info
        context["attendance_count"] = event.attendances.count()
        context["user_checked_in"] = checked_in
        context["scanned"] = self.request.GET.get("scan") == "true"
        # Check-in opens an hour before the event, so someone can legitimately
        # check in while it still hasn't started — say so plainly instead of
        # letting the page imply the event is already under way.
        context["event_not_started"] = timezone.now() < event.start_datetime
        return context


class EventQrCodePngView(View):
    def get(self, request, pk):
        event = get_object_or_404(Event, pk=pk)
        public_url = f"{request.scheme}://{request.get_host()}/event/{event.public_token}/?scan=true"
        from apps.events.services.qr import generate_qr_code_png

        log_audit_event(
            "event.qr_generated",
            actor=request.user,
            target=event,
            payload={"format": "png"},
        )
        png_bytes = generate_qr_code_png(public_url)
        return HttpResponse(png_bytes, content_type="image/png")


class EventQrCodeSvgView(View):
    def get(self, request, pk):
        event = get_object_or_404(Event, pk=pk)
        public_url = f"{request.scheme}://{request.get_host()}/event/{event.public_token}/?scan=true"
        from apps.events.services.qr import generate_qr_code_svg

        log_audit_event(
            "event.qr_generated",
            actor=request.user,
            target=event,
            payload={"format": "svg"},
        )
        svg_xml = generate_qr_code_svg(public_url)
        return HttpResponse(svg_xml, content_type="image/svg+xml")


class EventPrintQrView(LoginRequiredMixin, DetailView):
    model = Event
    template_name = "events/event_print_qr.html"
    context_object_name = "event"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        event = self.object
        log_audit_event("event.qr_printed", actor=self.request.user, target=event)
        context["public_url"] = (
            f"{self.request.scheme}://{self.request.get_host()}/event/{event.public_token}/"
        )
        return context

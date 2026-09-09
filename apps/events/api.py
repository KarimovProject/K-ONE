from datetime import datetime

from django.shortcuts import get_object_or_404
from rest_framework import filters, generics, serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.api_permissions import CanViewMasterData
from apps.accounts.models import User
from apps.accounts.rbac import Capability, user_has_capability
from apps.events.models import Event, EventType
from apps.events.selectors import calendar_events
from apps.events.services.conflicts import check_venue_availability
from apps.venues.models import Venue
from config.rate_limit import is_rate_limited


class EventTypeSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="localized_name", read_only=True)

    class Meta:
        model = EventType
        fields = (
            "id",
            "code",
            "name",
            "name_uz",
            "name_ru",
            "name_en",
            "description",
            "color",
            "icon",
            "is_active",
            "requires_management_approval",
            "allows_emergency_override",
            "sort_order",
        )


class EventTypeListAPIView(generics.ListAPIView):
    serializer_class = EventTypeSerializer
    permission_classes = (CanViewMasterData,)
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    search_fields = ("code", "name_uz", "name_ru", "name_en")
    ordering_fields = ("code", "sort_order")
    ordering = ("sort_order", "code")

    def get_queryset(self):
        queryset = EventType.objects.all()
        if self.request.query_params.get("active") == "true":
            queryset = queryset.filter(is_active=True)
        return queryset


class EventTypeDetailAPIView(generics.RetrieveAPIView):
    queryset = EventType.objects.all()
    serializer_class = EventTypeSerializer
    permission_classes = (CanViewMasterData,)


# --- Event API Serializers & Views ---


class EventListSerializer(serializers.ModelSerializer):
    event_type_name = serializers.CharField(source="event_type.localized_name", read_only=True)
    event_type_color = serializers.CharField(source="event_type.color", read_only=True)
    venue_name = serializers.CharField(source="venue.localized_name", read_only=True)
    responsible_employee_name = serializers.CharField(
        source="responsible_employee.get_full_name", read_only=True
    )
    status_label = serializers.CharField(source="get_status_display", read_only=True)
    priority_label = serializers.CharField(source="get_priority_display", read_only=True)
    weekday_name = serializers.CharField(read_only=True)

    class Meta:
        model = Event
        fields = (
            "id",
            "title",
            "event_type",
            "event_type_name",
            "event_type_color",
            "venue",
            "venue_name",
            "planned_date",
            "start_time",
            "end_time",
            "responsible_employee",
            "responsible_employee_name",
            "status",
            "status_label",
            "priority",
            "priority_label",
            "expected_attendees",
            "weekday_name",
            "duration_minutes",
        )


class EventDetailSerializer(serializers.ModelSerializer):
    event_type_name = serializers.CharField(source="event_type.localized_name", read_only=True)
    event_type_color = serializers.CharField(source="event_type.color", read_only=True)
    venue_name = serializers.CharField(source="venue.localized_name", read_only=True)
    responsible_employee_name = serializers.CharField(
        source="responsible_employee.get_full_name", read_only=True
    )
    management_responsible_name = serializers.CharField(
        source="management_responsible.get_full_name", read_only=True
    )
    status_label = serializers.CharField(source="get_status_display", read_only=True)
    priority_label = serializers.CharField(source="get_priority_display", read_only=True)
    weekday_name = serializers.CharField(read_only=True)

    class Meta:
        model = Event
        fields = (
            "id",
            "title",
            "event_type",
            "event_type_name",
            "event_type_color",
            "description",
            "venue",
            "venue_name",
            "planned_date",
            "start_time",
            "end_time",
            "responsible_employee",
            "responsible_employee_name",
            "management_responsible",
            "management_responsible_name",
            "organizing_organizations",
            "sponsors",
            "zoom_url",
            "registration_url",
            "status",
            "status_label",
            "priority",
            "priority_label",
            "expected_attendees",
            "notes",
            "weekday_name",
            "duration_minutes",
            "is_over_capacity",
            "created_at",
            "updated_at",
        )


class EventListAPIView(generics.ListAPIView):
    serializer_class = EventListSerializer
    permission_classes = (CanViewMasterData,)
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    search_fields = ("title", "description")
    ordering_fields = ("planned_date", "start_time", "created_at")
    ordering = ("-planned_date", "start_time")

    def get_queryset(self):
        queryset = Event.objects.select_related("event_type", "venue", "responsible_employee")
        status_param = self.request.query_params.get("status")
        if status_param and status_param != "all":
            queryset = queryset.filter(status=status_param)
        return queryset


class EventDetailAPIView(generics.RetrieveAPIView):
    queryset = Event.objects.all()
    serializer_class = EventDetailSerializer
    permission_classes = (CanViewMasterData,)


class CalendarEventsAPIView(APIView):
    permission_classes = (CanViewMasterData,)

    def get(self, request):
        start_str = request.query_params.get("start")
        end_str = request.query_params.get("end")

        if not (start_str and end_str):
            return Response(
                {"error": "start and end query parameters are required (YYYY-MM-DD)"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            start_date = datetime.strptime(start_str[:10], "%Y-%m-%d").date()
            end_date = datetime.strptime(end_str[:10], "%Y-%m-%d").date()
        except ValueError:
            return Response(
                {"error": "Invalid date format. Use YYYY-MM-DD"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        events = calendar_events(
            start_date=start_date,
            end_date=end_date,
            venue_id=request.query_params.get("venue"),
            event_type_id=request.query_params.get("type"),
            status_filter=request.query_params.get("status"),
            responsible_id=request.query_params.get("responsible"),
            organization_id=request.query_params.get("organization"),
        )

        calendar_payload = []
        for e in events:
            start_iso = f"{e.planned_date.isoformat()}T{e.start_time.strftime('%H:%M:%S')}"
            end_iso = f"{e.planned_date.isoformat()}T{e.end_time.strftime('%H:%M:%S')}"
            resp_name = e.responsible_employee.get_full_name() or e.responsible_employee.username

            status_colors = {
                "draft": "#64748B",
                "pending_approval": "#F59E0B",
                "submitted": "#F59E0B",
                "under_review": "#F59E0B",
                "approved": "#0EA5E9",
                "rejected": "#E11D48",
                "planned": "#2563EB",
                "scheduled": "#2563EB",
                "ongoing": "#10B981",
                "completed": "#475569",
                "postponed": "#F59E0B",
                "displaced": "#E11D48",
                "cancelled": "#E11D48",
                "emergency": "#E11D48",
            }
            color = status_colors.get(e.status, "#2563EB")

            calendar_payload.append(
                {
                    "id": str(e.pk),
                    "title": e.title,
                    "start": start_iso,
                    "end": end_iso,
                    "backgroundColor": color,
                    "borderColor": color,
                    "textColor": "#ffffff",
                    "extendedProps": {
                        "venue_name": e.venue.localized_name,
                        "event_type_name": e.event_type.localized_name,
                        "status": e.status,
                        "status_label": e.get_status_display(),
                        "priority": e.priority,
                        "responsible_name": resp_name,
                        "detail_url": f"/events/{e.pk}/",
                        "banner_url": e.banner_image.url if e.banner_image else "",
                    },
                }
            )

        return Response(calendar_payload)


class VenueAvailabilityAPIView(APIView):
    permission_classes = (CanViewMasterData,)

    def get(self, request, pk: int):
        venue = get_object_or_404(Venue, pk=pk)

        date_str = request.query_params.get("date")
        start_str = request.query_params.get("start_time")
        end_str = request.query_params.get("end_time")
        attendees = int(request.query_params.get("expected_attendees", 1))
        exclude_id = request.query_params.get("exclude_event_id")

        if not (date_str and start_str and end_str):
            return Response(
                {"error": "date, start_time, and end_time parameters required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            planned_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            start_time = datetime.strptime(start_str, "%H:%M").time()
            end_time = datetime.strptime(end_str, "%H:%M").time()
        except ValueError:
            return Response(
                {"error": "Invalid date or time format"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        result = check_venue_availability(
            venue=venue,
            planned_date=planned_date,
            start_time=start_time,
            end_time=end_time,
            expected_attendees=attendees,
            exclude_event_id=exclude_id,
        )

        cap_warn = str(result.capacity_warning) if result.capacity_warning else None

        return Response(
            {
                "is_available": result.is_available,
                "status_label": result.status_label,
                "message": str(result.message),
                "conflicting_event": (
                    {
                        "id": str(result.conflicting_event.pk),
                        "title": result.conflicting_event.title,
                        "start_time": result.conflicting_event.start_time.strftime("%H:%M"),
                        "end_time": result.conflicting_event.end_time.strftime("%H:%M"),
                    }
                    if result.conflicting_event
                    else None
                ),
                "capacity_warning": cap_warn,
                "alternative_venues": result.alternative_venues,
            }
        )


class EventSubmitAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, pk):
        event = get_object_or_404(Event, pk=pk)
        is_owner = request.user == event.responsible_employee or request.user == event.created_by
        is_admin = (
            user_has_capability(request.user, Capability.MANAGE_EVENTS) or request.user.is_superuser
        )
        if not (is_owner or is_admin):
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

        try:
            from apps.events.services.workflow import submit_event_for_approval

            ev = submit_event_for_approval(event, request.user)
            return Response(EventDetailSerializer(ev).data, status=status.HTTP_200_OK)
        except Exception as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)


class EventApproveAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, pk):
        event = get_object_or_404(Event, pk=pk)
        is_mgmt = (
            request.user == event.management_responsible
            or user_has_capability(request.user, Capability.APPROVE_EVENTS)
            or request.user.is_superuser
        )
        if not is_mgmt:
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

        notes = request.data.get("notes", "")
        try:
            from apps.events.services.workflow import approve_event

            ev = approve_event(event, request.user, notes=notes)
            return Response(EventDetailSerializer(ev).data, status=status.HTTP_200_OK)
        except Exception as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)


class EventRejectAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, pk):
        event = get_object_or_404(Event, pk=pk)
        is_mgmt = (
            request.user == event.management_responsible
            or user_has_capability(request.user, Capability.APPROVE_EVENTS)
            or request.user.is_superuser
        )
        if not is_mgmt:
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

        reason = request.data.get("reason", "").strip()
        if not reason:
            return Response(
                {"error": "Rejection reason is mandatory."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            from apps.events.services.workflow import reject_event

            ev = reject_event(event, request.user, reason=reason)
            return Response(EventDetailSerializer(ev).data, status=status.HTTP_200_OK)
        except Exception as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)


class EventResubmitAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, pk):
        event = get_object_or_404(Event, pk=pk)
        is_owner = request.user == event.responsible_employee or request.user == event.created_by
        is_admin = (
            user_has_capability(request.user, Capability.MANAGE_EVENTS) or request.user.is_superuser
        )
        if not (is_owner or is_admin):
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

        try:
            from apps.events.services.workflow import resubmit_event

            ev = resubmit_event(event, request.user)
            return Response(EventDetailSerializer(ev).data, status=status.HTTP_200_OK)
        except Exception as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)


class EventPostponeAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, pk):
        event = get_object_or_404(Event, pk=pk)
        is_owner = request.user == event.responsible_employee or request.user == event.created_by
        is_admin = (
            user_has_capability(request.user, Capability.MANAGE_EVENTS) or request.user.is_superuser
        )
        if not (is_owner or is_admin):
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

        reason = request.data.get("reason", "")
        try:
            from apps.events.services.workflow import postpone_event

            ev = postpone_event(event, request.user, reason=reason)
            return Response(EventDetailSerializer(ev).data, status=status.HTTP_200_OK)
        except Exception as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)


class EventRescheduleAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, pk):
        event = get_object_or_404(Event, pk=pk)
        is_owner = request.user == event.responsible_employee or request.user == event.created_by
        is_admin = (
            user_has_capability(request.user, Capability.MANAGE_EVENTS) or request.user.is_superuser
        )
        if not (is_owner or is_admin):
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

        date_str = request.data.get("planned_date")
        start_str = request.data.get("start_time")
        end_str = request.data.get("end_time")
        venue_id = request.data.get("venue_id")

        if not (date_str and start_str and end_str):
            return Response(
                {"error": "planned_date, start_time, and end_time are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            planned_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            start_time = datetime.strptime(start_str, "%H:%M").time()
            end_time = datetime.strptime(end_str, "%H:%M").time()
        except ValueError:
            return Response(
                {"error": "Invalid date or time format."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        target_venue = None
        if venue_id:
            target_venue = get_object_or_404(Venue, pk=venue_id)

        try:
            from apps.events.services.workflow import reschedule_event

            ev = reschedule_event(
                event,
                request.user,
                planned_date=planned_date,
                start_time=start_time,
                end_time=end_time,
                venue=target_venue,
            )
            return Response(EventDetailSerializer(ev).data, status=status.HTTP_200_OK)
        except Exception as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)


class EventEmergencyOverrideAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, pk):
        event = get_object_or_404(Event, pk=pk)
        is_authorized = request.user.is_superuser or request.user.role in (
            User.Role.SUPER_ADMIN,
            User.Role.INTERNATIONAL_ADMIN,
        )
        if not is_authorized:
            return Response(
                {
                    "detail": (
                        "Only super admins and international admins can trigger "
                        "emergency overrides."
                    )
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        justification = request.data.get("justification", "").strip()
        if not justification:
            return Response(
                {"error": "Emergency justification is mandatory."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            from apps.events.services.emergency import execute_emergency_override

            ev, displaced = execute_emergency_override(
                event, request.user, justification=justification
            )
            return Response(
                {
                    "event": EventDetailSerializer(ev).data,
                    "displaced_count": len(displaced),
                    "displaced_event_ids": [str(d.pk) for d in displaced],
                },
                status=status.HTTP_200_OK,
            )
        except Exception as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)


# --- Phase 4 Public & Program API Views ---


class PublicEventAPIView(APIView):
    permission_classes = ()  # Public endpoint - no login required

    def get(self, request, token: str):
        if is_rate_limited(request, "public-event-api", 180, 60, token):
            return Response(
                {"error": "Too many requests"}, status=status.HTTP_429_TOO_MANY_REQUESTS
            )
        event = get_object_or_404(
            Event.objects.select_related("event_type", "venue").prefetch_related(
                "organizing_organizations", "sponsors", "program_items__speaker"
            ),
            public_token=token,
        )
        if not event.is_publicly_accessible:
            return Response(
                {"detail": "Event program is not published or unavailable."},
                status=status.HTTP_404_NOT_FOUND,
            )

        agenda_items = []
        for item in event.program_items.all():
            agenda_items.append(
                {
                    "id": item.pk,
                    "start_time": item.start_time.strftime("%H:%M"),
                    "end_time": item.end_time.strftime("%H:%M"),
                    "title": item.title,
                    "description": item.description,
                    "speaker": item.speaker_display_name,
                    "sort_order": item.sort_order,
                }
            )

        speakers = []
        seen_speaker_ids = set()
        for item in event.program_items.all():
            sp = item.speaker
            if sp and sp.public_profile_enabled and sp.pk not in seen_speaker_ids:
                seen_speaker_ids.add(sp.pk)
                speakers.append(
                    {
                        "id": sp.pk,
                        "full_name": sp.full_name,
                        "title": sp.title,
                        "organization": sp.organization,
                        "country": sp.country,
                        "bio": sp.bio,
                        "photo": sp.photo.url if sp.photo else None,
                    }
                )

        organizers = [
            {"id": org.pk, "name": org.localized_name, "logo": org.logo.url if org.logo else None}
            for org in event.organizing_organizations.all()
        ]
        sponsors = [
            {"id": sp.pk, "name": sp.localized_name, "logo": sp.logo.url if sp.logo else None}
            for sp in event.sponsors.all()
        ]

        payload = {
            "public_token": event.public_token,
            "title": event.title,
            "event_type": event.event_type.localized_name,
            "event_type_color": event.event_type.color,
            "venue_name": event.venue.localized_name,
            "planned_date": event.planned_date.isoformat(),
            "weekday_name": event.weekday_name,
            "start_time": event.start_time.strftime("%H:%M"),
            "end_time": event.end_time.strftime("%H:%M"),
            "status": event.status,
            "status_label": event.get_status_display(),
            "description": event.description,
            "zoom_url": event.zoom_url,
            "registration_url": event.registration_url,
            "program_source": event.program_source,
            "program_pdf_url": (
                event.program_pdf.url
                if (event.program_pdf and event.program_source == "pdf")
                else None
            ),
            "program_intro": event.program_intro,
            "program_notes": event.program_notes,
            "countdown_info": event.public_countdown_info,
            "agenda_items": agenda_items,
            "speakers": speakers,
            "organizing_organizations": organizers,
            "sponsors": sponsors,
        }
        return Response(payload, status=status.HTTP_200_OK)


class EventProgramAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk):
        event = get_object_or_404(Event, pk=pk)
        agenda_items = [
            {
                "id": item.pk,
                "start_time": item.start_time.strftime("%H:%M"),
                "end_time": item.end_time.strftime("%H:%M"),
                "title": item.title,
                "description": item.description,
                "speaker_id": item.speaker_id,
                "speaker_name": item.speaker_display_name,
                "sort_order": item.sort_order,
            }
            for item in event.program_items.all()
        ]
        return Response(
            {
                "id": str(event.pk),
                "title": event.title,
                "program_source": event.program_source,
                "program_pdf": event.program_pdf.url if event.program_pdf else None,
                "program_intro": event.program_intro,
                "program_notes": event.program_notes,
                "public_token": event.public_token,
                "is_public_enabled": event.is_public_enabled,
                "agenda_items": agenda_items,
            }
        )

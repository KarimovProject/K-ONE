from django.core.cache import cache
from django.core.exceptions import ValidationError as DjangoValidationError
from django.shortcuts import get_object_or_404
from rest_framework import serializers, status
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.generics import ListCreateAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.publications.adapters import PublicationAdapterError
from apps.publications.models import Publication
from apps.publications.policies import (
    can_approve,
    can_prepare,
    can_publish,
    ensure_event_publishable,
)
from apps.publications.services import (
    approve_publication,
    mark_publication_failed,
    publish_publication,
    schedule_publication,
)


class PublicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Publication
        fields = (
            "id",
            "event",
            "platform",
            "language",
            "status",
            "headline",
            "short_description",
            "caption",
            "rendered_caption",
            "banner",
            "scheduled_for",
            "published_at",
            "external_post_id",
            "external_url",
            "error_code",
            "error_message",
        )
        read_only_fields = (
            "status",
            "rendered_caption",
            "banner",
            "published_at",
            "external_post_id",
            "external_url",
            "error_code",
            "error_message",
        )

    def create(self, validated_data):
        event = validated_data["event"]
        user = self.context["request"].user
        if not can_prepare(user, event):
            raise PermissionDenied
        try:
            ensure_event_publishable(event)
        except DjangoValidationError as exc:
            raise serializers.ValidationError(str(exc)) from exc
        return Publication.objects.create(created_by=user, **validated_data)


class PublicationListCreateAPIView(ListCreateAPIView):
    queryset = Publication.objects.select_related("event")
    serializer_class = PublicationSerializer


class PublicationDetailAPIView(RetrieveAPIView):
    queryset = Publication.objects.select_related("event")
    serializer_class = PublicationSerializer


class PublicationActionAPIView(APIView):
    action = ""

    def post(self, request, pk):
        publication = get_object_or_404(Publication, pk=pk)
        try:
            if self.action == "approve":
                if not can_approve(request.user):
                    raise PermissionDenied
                approve_publication(publication, request.user)
            elif self.action == "schedule":
                if not can_publish(request.user):
                    raise PermissionDenied
                value = serializers.DateTimeField().to_internal_value(
                    request.data.get("scheduled_for")
                )
                schedule_publication(publication, request.user, value)
            else:
                if not can_publish(request.user):
                    raise PermissionDenied
                if not cache.add(f"publication-api:{publication.pk}", "1", 10):
                    raise ValidationError("Publication action is already in progress.")
                publish_publication(publication.pk)
        except PublicationAdapterError as exc:
            publication.refresh_from_db()
            mark_publication_failed(publication, exc)
            raise ValidationError("Platform publication failed.") from exc
        except (ValueError, serializers.ValidationError, DjangoValidationError) as exc:
            raise ValidationError(str(exc)) from exc
        publication.refresh_from_db()
        return Response(PublicationSerializer(publication).data, status=status.HTTP_200_OK)

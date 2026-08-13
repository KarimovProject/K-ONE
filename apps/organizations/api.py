from rest_framework import filters, generics, serializers

from apps.accounts.api_permissions import CanViewMasterData
from apps.organizations.models import Organization, Sponsor


class OrganizationSerializer(serializers.ModelSerializer):
    organization_type_label = serializers.CharField(
        source="get_organization_type_display",
        read_only=True,
    )

    class Meta:
        model = Organization
        fields = (
            "id",
            "name",
            "short_name",
            "organization_type",
            "organization_type_label",
            "country",
            "city",
            "address",
            "website",
            "email",
            "phone",
            "contact_person",
            "logo",
            "notes",
            "is_active",
        )


class SponsorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sponsor
        fields = (
            "id",
            "name",
            "description",
            "website",
            "contact_person",
            "phone",
            "email",
            "logo",
            "is_active",
            "notes",
        )


class ActiveFilterMixin:
    def filter_active(self, queryset):
        active = self.request.query_params.get("active")
        if active == "true":
            return queryset.filter(is_active=True)
        if active == "false":
            return queryset.filter(is_active=False)
        return queryset


class OrganizationListAPIView(ActiveFilterMixin, generics.ListAPIView):
    serializer_class = OrganizationSerializer
    permission_classes = (CanViewMasterData,)
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    search_fields = ("name", "short_name", "country", "city", "contact_person")
    ordering_fields = ("name", "country", "organization_type")
    ordering = ("name",)

    def get_queryset(self):
        queryset = self.filter_active(Organization.objects.all())
        organization_type = self.request.query_params.get("type")
        if organization_type in Organization.Type.values:
            queryset = queryset.filter(organization_type=organization_type)
        return queryset


class OrganizationDetailAPIView(generics.RetrieveAPIView):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    permission_classes = (CanViewMasterData,)


class SponsorListAPIView(ActiveFilterMixin, generics.ListAPIView):
    serializer_class = SponsorSerializer
    permission_classes = (CanViewMasterData,)
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    search_fields = ("name", "contact_person", "email", "phone")
    ordering_fields = ("name",)
    ordering = ("name",)

    def get_queryset(self):
        return self.filter_active(Sponsor.objects.all())


class SponsorDetailAPIView(generics.RetrieveAPIView):
    queryset = Sponsor.objects.all()
    serializer_class = SponsorSerializer
    permission_classes = (CanViewMasterData,)

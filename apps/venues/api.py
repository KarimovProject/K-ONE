from rest_framework import filters, generics, serializers

from apps.accounts.api_permissions import CanViewMasterData
from apps.venues.models import Venue


class VenueSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="localized_name", read_only=True)

    class Meta:
        model = Venue
        fields = (
            "id",
            "code",
            "name",
            "name_uz",
            "name_ru",
            "name_en",
            "description",
            "location",
            "capacity",
            "working_start",
            "working_end",
            "is_active",
            "display_enabled",
            "photo",
            "sort_order",
        )


class VenueListAPIView(generics.ListAPIView):
    serializer_class = VenueSerializer
    permission_classes = (CanViewMasterData,)
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    search_fields = ("code", "name_uz", "name_ru", "name_en", "location")
    ordering_fields = ("code", "capacity", "sort_order")
    ordering = ("sort_order", "code")

    def get_queryset(self):
        queryset = Venue.objects.all()
        if self.request.query_params.get("active") == "true":
            queryset = queryset.filter(is_active=True)
        return queryset


class VenueDetailAPIView(generics.RetrieveAPIView):
    queryset = Venue.objects.all()
    serializer_class = VenueSerializer
    permission_classes = (CanViewMasterData,)

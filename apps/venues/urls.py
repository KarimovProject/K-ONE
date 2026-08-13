from django.urls import path

from apps.venues import views

app_name = "venues"

urlpatterns = [
    path("", views.VenueListView.as_view(), name="list"),
    path("new/", views.VenueCreateView.as_view(), name="create"),
    path("<int:pk>/", views.VenueDetailView.as_view(), name="detail"),
    path("<int:pk>/edit/", views.VenueUpdateView.as_view(), name="edit"),
    path("<int:pk>/delete/", views.VenueDeleteView.as_view(), name="delete"),
]

from django.urls import path

from apps.organizations import views

organization_patterns = (
    [
        path("", views.OrganizationListView.as_view(), name="list"),
        path("new/", views.OrganizationCreateView.as_view(), name="create"),
        path("<int:pk>/", views.OrganizationDetailView.as_view(), name="detail"),
        path("<int:pk>/edit/", views.OrganizationUpdateView.as_view(), name="edit"),
        path("<int:pk>/delete/", views.OrganizationDeleteView.as_view(), name="delete"),
    ],
    "organizations",
)

sponsor_patterns = (
    [
        path("", views.SponsorListView.as_view(), name="list"),
        path("new/", views.SponsorCreateView.as_view(), name="create"),
        path("<int:pk>/", views.SponsorDetailView.as_view(), name="detail"),
        path("<int:pk>/edit/", views.SponsorUpdateView.as_view(), name="edit"),
        path("<int:pk>/delete/", views.SponsorDeleteView.as_view(), name="delete"),
    ],
    "sponsors",
)

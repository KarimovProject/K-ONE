from django.urls import path

from apps.publications import views

app_name = "publications"

urlpatterns = [
    path("", views.PublicationListView.as_view(), name="list"),
    path("events/<uuid:event_pk>/new/", views.PublicationCreateView.as_view(), name="create"),
    path("<uuid:pk>/", views.PublicationDetailView.as_view(), name="detail"),
    path("<uuid:pk>/edit/", views.PublicationUpdateView.as_view(), name="edit"),
]
for action in ("prepare", "approve", "schedule", "publish", "retry", "cancel"):
    urlpatterns.append(
        path(
            f"<uuid:pk>/{action}/",
            views.PublicationActionView.as_view(action=action),
            name=action,
        )
    )

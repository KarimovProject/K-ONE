from django.db.models import QuerySet

from apps.organizations.models import Organization, Sponsor


def active_organizations() -> QuerySet[Organization]:
    return Organization.objects.filter(is_active=True)


def organizations_by_type(organization_type: str) -> QuerySet[Organization]:
    return active_organizations().filter(organization_type=organization_type)


def active_sponsors() -> QuerySet[Sponsor]:
    return Sponsor.objects.filter(is_active=True)

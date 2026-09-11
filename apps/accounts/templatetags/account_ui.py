from django import template
from django.utils.translation import gettext as _

from apps.accounts.models import User

register = template.Library()


@register.filter
def localized_role(user: User) -> str:
    labels = {
        User.Role.SUPER_ADMIN: _("Super administrator"),
        User.Role.INTERNATIONAL_ADMIN: _("International department administrator"),
        User.Role.RESPONSIBLE_EMPLOYEE: _("Responsible employee"),
        User.Role.MANAGEMENT_RESPONSIBLE: _("Management responsible"),
        User.Role.LEADERSHIP_VIEWER: _("Leadership viewer"),
        User.Role.CONTENT_MANAGER: _("Content manager"),
        User.Role.RECEPTION_OPERATOR: _("Reception operator"),
        User.Role.DOCTOR: _("Doctor"),
    }
    return str(labels.get(user.role, user.get_role_display()))

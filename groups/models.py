from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db import models
from django.utils.translation import gettext_lazy as _

USER = get_user_model()


class GroupInfo(models.Model):
    """Extension of Django's built-in Group model"""

    group = models.OneToOneField(Group, on_delete=models.CASCADE)
    description = models.TextField(_('group description'), blank=True)
    organization = models.ForeignKey('organizations.Organization', on_delete=models.CASCADE)
    creator = models.ForeignKey(USER, on_delete=models.CASCADE, related_name='created_groups')

    def __str__(self):
        return self.group.name

from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.db import models

USER = get_user_model()


class Organization(models.Model):
    """Organization model"""

    name = models.CharField(_('organization name'), max_length=150, blank=False)
    description = models.TextField(_('organization description'), blank=True)
    owner = models.ForeignKey(USER, on_delete=models.CASCADE, related_name='owned_organizations')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Organization')
        verbose_name_plural = _('Organizations')

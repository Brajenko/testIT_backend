from django.contrib.auth.models import AbstractUser, Group
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _

from .managers import *


class User(AbstractUser):
    """Custom user model

    Uses email instead of username for authentication and adds some additional fields.
    """

    username = None
    email = models.EmailField(_('email address'), unique=True)
    first_name = models.CharField(_('first name'), max_length=150, blank=False)
    last_name = models.CharField(_('last name'), max_length=150, blank=False)
    is_teacher = models.BooleanField(_('is user teacher'), default=False)
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.SET_NULL,
        null=True,
    )
    photo = models.ImageField(_('user photo'), upload_to='users_photos', blank=True, null=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'is_teacher', 'password']

    def __str__(self) -> str:
        return self.email

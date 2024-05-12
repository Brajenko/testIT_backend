from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework.serializers import ValidationError

from organizations.models import Organization
from organizations.serializers import OrganizationSerializer

from .models import *

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())],
    )
    organization_id = serializers.PrimaryKeyRelatedField(queryset=Organization.objects.all(), required=False, write_only=True)
    organization = OrganizationSerializer(read_only=True)
    
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    if settings.DEBUG:
        password = serializers.CharField(write_only=True, required=True, validators=[])

    class Meta:
        model = User
        fields = (
            'id',
            'password',
            'email',
            'first_name',
            'last_name',
            'photo',
            'is_teacher',
            'organization',
            'organization_id',
        )

    def create(self, validated_data):
        user = User.objects.create(
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            is_teacher=validated_data['is_teacher'],
        )
        if org_id := validated_data.get('organization_id', None):
            org = Organization.objects.get(id=org_id)
            user.organization = org # type: ignore

        user.set_password(validated_data['password'])
        user.save()
        return user

    def update(self, instance, validated_data):
        if password := validated_data.pop('password', None):
            instance.set_password(password)
            
        if org_id := validated_data.pop('organization_id', None):
            org = Organization.objects.get(id=org_id)
            if instance.organization is not None and instance.organization != org:
                raise ValidationError('You can`t change your organization')
            else:
                instance.organization = org
        return super().update(instance, validated_data)

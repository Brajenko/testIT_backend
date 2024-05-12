from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.serializers import ValidationError

from organizations.serializers import OrganizationSerializer
from users.serializers import UserSerializer

from .models import *

USER = get_user_model()


class GroupSerializer(serializers.ModelSerializer):
    description = serializers.CharField(required=True, source='groupinfo.description')
    organization = OrganizationSerializer(source='groupinfo.organization', read_only=True)
    members = UserSerializer(many=True, source='user_set', read_only=True)

    class Meta:
        model = Group
        fields = ('id', 'name', 'description', 'organization', 'members')

    def validate(self, attrs):
        """Adds creator and organization to data"""
        creator = self.context['request'].user
        if not creator.organization:
            raise ValidationError('Creator must be in an organization')
        attrs['creator'] = creator
        attrs['organization'] = creator.organization
        return super().validate(attrs)

    def create(self, validated_data):
        """Creates group and group info objects and returns group object."""
        group = Group.objects.create(
            name=validated_data['name'],
        )
        group_info = GroupInfo.objects.create(
            group=group,
            description=validated_data['description'],
            organization=validated_data['organization'],
            creator=validated_data['creator'],
        )
        return group


class GroupAddUserSerializer(serializers.Serializer):
    user = serializers.PrimaryKeyRelatedField(queryset=USER.objects.all())

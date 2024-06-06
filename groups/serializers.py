from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.serializers import ValidationError

from organizations.serializers import OrganizationSerializer
from users.serializers import UserWithoutOrganizationSerializer

from .models import *

USER = get_user_model()


class GroupSerializer(serializers.ModelSerializer):
    description = serializers.CharField(required=True, source='groupinfo.description')
    members = UserWithoutOrganizationSerializer(many=True, source='user_set', read_only=True)

    class Meta:
        model = Group
        fields = ('id', 'name', 'description', 'members')

    def validate(self, attrs):
        """Adds creator and organization to data"""
        creator = self.context['request'].user
        if not creator.organization:
            raise ValidationError('Creator must be in an organization')
        print(attrs)
        attrs['groupinfo']['creator'] = creator
        attrs['groupinfo']['organization'] = creator.organization
        return super().validate(attrs)

    def create(self, validated_data):
        """Creates group and group info objects and returns group object."""
        groupinfo_data = validated_data.pop('groupinfo')
        group = Group.objects.create(
            **validated_data
        )
        GroupInfo.objects.create(
            group=group,
            **groupinfo_data
        )
        return group


class GroupAddUserSerializer(serializers.Serializer):
    user = serializers.PrimaryKeyRelatedField(queryset=USER.objects.all())


class GroupWithoutMembersSerializer(GroupSerializer):
    class Meta(GroupSerializer.Meta):
        fields = ('id', 'name', 'description')

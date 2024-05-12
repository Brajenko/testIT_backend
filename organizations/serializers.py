from rest_framework import serializers

from .models import *


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ('id', 'name', 'description', 'owner')
        read_only_fields = ('id', 'owner')

    def create(self, validated_data):
        org = super().create(validated_data)
        validated_data['owner'].organization = org
        validated_data['owner'].save()
        return org

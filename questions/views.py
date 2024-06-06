import datetime as dt

import tablib
from django.http.response import HttpResponse
from drf_spectacular.utils import (OpenApiResponse, extend_schema,
                                   extend_schema_view)
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from completions.serializers import (CompletionCreationSerializer,
                                     CompletionSerializer)
from organizations.permissions import HasOrg
from users.permissions import IsTeacher

from .models import Test
from .permissions import CanPassTest, IsTestCreator
from .serializers import (AllowToGroupSerializer, TestCreationSerializer,
                          TestSerializer)


class TestViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = [IsTestCreator]

    def get_queryset(self):  # type: ignore
        """Returns only test created by teachers from the same organization as user"""
        if self.action == 'export_completions':
            return Test.objects.all()
        if self.request.user.is_anonymous:
            return Test.objects.none()
        org = self.request.user.organization  # type: ignore
        return Test.objects.filter(creator__organization=org)

    def get_permissions(self):
        match self.action:
            case 'list' | 'create':
                return [(HasOrg & IsTeacher)()]
            case 'export_completions':
                return []
        return super().get_permissions()

    def get_serializer_class(self):  # type: ignore
        match self.action:
            case 'list':
                return TestSerializer
            case 'retrieve' | 'create':
                return TestCreationSerializer
            case 'allow_for_group' | 'disallow_for_group':
                return AllowToGroupSerializer
        return TestSerializer

    @extend_schema(request=TestSerializer, responses=TestSerializer)
    def list(self, request, *args, **kwargs):
        """List all tests created by current teacher."""
        return super().list(request, *args, **kwargs)

    @extend_schema(request=TestCreationSerializer, responses=TestCreationSerializer)
    def create(self, request, *args, **kwargs):
        """Create new test."""
        return super().create(request, *args, **kwargs)

    @extend_schema(request=TestCreationSerializer, responses=TestCreationSerializer)
    def retrieve(self, request, *args, **kwargs):
        """Return test (teachers only!)"""
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(request=AllowToGroupSerializer, responses=TestCreationSerializer)
    @action(detail=True, methods=['post'])
    def allow_for_group(self, request, pk=None):
        """Allow test completion for group."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        group = serializer.validated_data['group']
        instance = self.get_object()
        instance.available_for.add(group)
        return Response(TestCreationSerializer(instance).data)

    @extend_schema(request=AllowToGroupSerializer, responses=TestCreationSerializer)
    @action(detail=True, methods=['post'])
    def disallow_for_group(self, request, pk=None):
        """Disallow test completion for group."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        group = serializer.validated_data['group']
        instance = self.get_object()
        instance.available_for.remove(group)
        return Response(TestCreationSerializer(instance).data)

    @extend_schema(request=None, responses=TestCreationSerializer)
    @action(detail=True, methods=['post'])
    def regenerate_uuid(self, request, pk=None):
        """Regenerate uuid, that used in link for test completion."""
        instance = self.get_object()
        instance.regenerate_uuid()
        return Response(TestCreationSerializer(instance).data)

    @extend_schema(request=None, responses=CompletionSerializer(many=True))
    @action(detail=True, methods=['get'], url_path='completions')
    def get_completions(self, request, pk=None):
        """Get all completions of test."""
        instance = self.get_object()
        return Response(CompletionSerializer(instance.completion_set.all(), many=True).data)

    @extend_schema(request=None, responses={200: bytes})
    @action(detail=True, methods=['get'], url_path='completions/export')
    def export_completions(self, request, pk=None):
        """Get completions of test in xlsx format."""
        instance = self.get_object()
        completions = instance.completion_set.all()
        headers = ['Email', 'ФИ', 'Группа', 'Оценка', 'Дата и время']
        data = []
        data = tablib.Dataset(*data, headers=headers, title=instance.name)
        for c in completions:
            # remove timezone info so excel could properly write this
            created_at_without_tz = c.created_at.replace(tzinfo=None)
            # choose which group is display for user
            # option 1: group that user is in and that is allowed for test
            # option 2: first group of user
            # option 3: 'Не в группе'
            group = (c.user.groups.filter() & c.test.available_for.all()
                     ).first() or c.user.groups.first() or 'Не в группе'
            data.append([c.user.email, c.user.last_name + ' ' + c.user.first_name,
                        group, c.score, created_at_without_tz])
        response = HttpResponse(data.export('xlsx'),
                                content_type='application/vnd.ms-excel;charset=utf-8')
        response['Content-Disposition'] = f'attachment; filename=results.xlsx'
        return response


class PublicTestViewSet(
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    permission_classes = [IsAuthenticated & CanPassTest]
    queryset = Test.objects.all()
    serializer_class = TestSerializer
    lookup_field = 'public_uuid'

    @extend_schema(responses=CompletionCreationSerializer(many=True))
    @action(detail=True, methods=['get'], url_path='completions')
    def get_completions(self, request, public_uuid=None):
        """Get all completions of current student of current test."""
        instance = self.get_object()
        return Response(CompletionCreationSerializer(instance.completion_set.filter(user=self.request.user), many=True).data)

    def retrieve(self, request, *args, **kwargs):
        """Get test for completion (only students!)"""
        return super().retrieve(request, *args, **kwargs)

from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import generics, mixins, views, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from organizations.permissions import HasOrg
from users.permissions import IsTeacher
from questions.permissions import CanPassTest

from .models import Completion
from .serializers import CompletionCreationSerializer, CompletionSerializer


class CompletionViewSet(
    mixins.CreateModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):

    queryset = Completion.objects.all()
    serializer_class = CompletionCreationSerializer

    def get_permissions(self):
        if self.action == 'with_correctness':
            return [HasOrg(), IsTeacher()]
        return [HasOrg()]

    def get_serializer_class(self):   # type: ignore
        if self.action == 'with_correctness':   # type: ignore
            return CompletionSerializer
        return super().get_serializer_class()

    @extend_schema(request=CompletionCreationSerializer, responses=CompletionCreationSerializer)
    def create(self, request, *args, **kwargs):
        """Create new completion"""
        return super().create(request, *args, **kwargs)

    @extend_schema(responses={200: CompletionCreationSerializer})
    def retrieve(self, request, *args, **kwargs):
        """Return completion"""
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(responses={200: CompletionSerializer})
    @action(detail=True, methods=['GET'])
    def with_correctness(self, request, *args, **kwargs):
        """Return completion with is_correct in answers."""
        return super().retrieve(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

from rest_framework import mixins, viewsets, generics
from .models import Test, Completion
from .serializers import TestSerializer, NoAnswerTestSerializer, CompletionSerializer, NoAnswersCompletionSerializer
from rest_framework.exceptions import PermissionDenied
from rest_framework import permissions
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes


class IsTestCreator(permissions.BasePermission):
    """
    Permission checks if user created test obj
    """

    def has_object_permission(self, request, view, obj):
        if request.user.is_anonymous:
            return False
        return request.user == obj.creator


class CanPassTest(permissions.BasePermission):
    """
    Permission checks if user can pass this test
    """

    def has_object_permission(self, request, view, obj):
        print(request.user, obj)
        return True


class MyTestsViewSet(mixins.CreateModelMixin,
                     mixins.ListModelMixin,
                     mixins.RetrieveModelMixin,
                     mixins.DestroyModelMixin,
                     viewsets.GenericViewSet):

    """
    Manage tests, created by currently authenficated user.
    """
    model = Test
    serializer_class = TestSerializer

    def get_queryset(self):
        user = self.request.user
        return Test.objects.filter(creator=user)

    @extend_schema(
        parameters=[
            OpenApiParameter("id", OpenApiTypes.INT, OpenApiParameter.PATH)
        ]
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)


class TestView(generics.RetrieveAPIView):

    """
    Get test to pass 
    """
    model = Test
    serializer_class = NoAnswerTestSerializer
    permission_classes = [CanPassTest]
    lookup_field = 'public_uuid'
    queryset = Test.objects.all()


class CompletionViewSet(mixins.CreateModelMixin,
                        mixins.ListModelMixin,
                        mixins.RetrieveModelMixin,
                        mixins.DestroyModelMixin,
                        viewsets.GenericViewSet):
    model = Completion
    serializer_class = NoAnswersCompletionSerializer
    queryset = Completion.objects.all()
    
    @extend_schema(
        parameters=[
            OpenApiParameter("id", OpenApiTypes.INT, OpenApiParameter.PATH)
        ]
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

class MyTestCompletionsViewSet(mixins.ListModelMixin,
                        mixins.CreateModelMixin,
                        mixins.RetrieveModelMixin,
                        mixins.DestroyModelMixin, 
                        viewsets.GenericViewSet):
    model = Completion
    def get_queryset(self):
        return Completion.objects.filter(test=self.kwargs['public_uuid'], student=self.request.user)

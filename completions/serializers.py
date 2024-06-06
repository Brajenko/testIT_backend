from rest_framework import serializers
from drf_spectacular.utils import extend_schema_serializer

from questions.serializers import VariantSerializer, VariantIsCorrectSerializer
from questions.models import Test
from users.serializers import UserWithoutOrganizationSerializer

from .models import *

class AnswerBodySerializer(serializers.Serializer):
    picked_variant = VariantIsCorrectSerializer(required=False)
    picked_variants = VariantIsCorrectSerializer(many=True, required=False)
    code = serializers.CharField(required=False)
    is_correct = serializers.BooleanField(required=False)
    runtime_errors = serializers.CharField(required=False, source='errors')
    
    def to_representation(self, instance):
        match instance.answer.question.type:
            case 'text' | 'radio':
                return {
                    'picked_variant': VariantIsCorrectSerializer(instance.picked_variant).data,
                }
            case 'check':
                return {
                    'picked_variants': VariantIsCorrectSerializer(instance.picked_variants.all(), many=True).data,
                }
            case 'code':
                return {
                    'code': instance.code,
                    'is_correct': instance.is_correct,
                    'errors': instance.errors
                }
            case _:
                return {}


class AnswerSerializer(serializers.ModelSerializer):
    body = AnswerBodySerializer()
    points = serializers.IntegerField(read_only=True, source='get_points')
    
    class Meta:
        model = Answer
        fields = ('question', 'body', 'points')


@extend_schema_serializer()
class CompletionSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True)
    user = UserWithoutOrganizationSerializer(read_only=True)
    score = serializers.IntegerField(source='get_score', read_only=True)
    
    class Meta:
        model = Completion
        fields = ('id', 'user', 'test', 'answers', 'score')


class AnswerBodyCreationSerializer(serializers.Serializer):
    picked_variant = VariantSerializer(required=False)
    picked_variants = VariantSerializer(many=True, required=False)
    code = serializers.CharField(required=False)
    
    def to_representation(self, instance):
        match instance.answer.question.type:
            case 'text' | 'radio':
                return {
                    'picked_variant': VariantSerializer(instance.picked_variant).data,
                }
            case 'check':
                return {
                    'picked_variants': VariantSerializer(instance.picked_variants.all(), many=True).data,
                }
            case 'code':
                return {
                    'code': instance.code,
                }
            case _:
                return {}
    
    def create(self, validated_data):
        question = validated_data['answer'].question
        match question.type:
            case 'text':
                variant = question.textbody.variants.filter(text__iexact=validated_data['picked_variant']['text'].rstrip().lstrip()).first()
                if variant is None:
                    variant = question.textbody.variants.create(text=validated_data['picked_variant']['text'], is_correct=False)
                created_body = TextAnswerBody.objects.create(
                    picked_variant=variant,
                    answer=validated_data['answer']
                )
            case 'radio':
                variant = question.radiobody.variants.filter(text=validated_data['picked_variant']['text']).first()
                created_body = RadioAnswerBody.objects.create(
                    picked_variant=variant,
                    answer=validated_data['answer']
                )
            case 'check':
                variants = question.checkbody.variants.filter(text__in=[v['text'] for v in validated_data['picked_variants']])
                created_body = CheckAnswerBody.objects.create(
                    answer=validated_data['answer']
                )
                created_body.picked_variants.set(variants)
            case 'code':
                created_body = CodeAnswerBody.objects.create(
                    code=validated_data['code'],
                    answer=validated_data['answer']
                )
            case _:
                raise ValueError('Question type is not defined')
        return created_body


class AnswerCreationSerializer(serializers.ModelSerializer):
    body = AnswerBodyCreationSerializer()
    
    class Meta:
        model = Answer
        fields = ('question', 'body')
    
    def create(self, validated_data):
        body_data = validated_data.pop('body')
        answer = Answer.objects.create(**validated_data)
        body_serializer = AnswerBodyCreationSerializer(data=body_data)
        body_serializer.is_valid(raise_exception=True)
        body_serializer.save(answer=answer)
        return answer


class CompletionCreationSerializer(serializers.ModelSerializer):
    answers = AnswerCreationSerializer(many=True)
    test = serializers.SlugRelatedField(slug_field='public_uuid', queryset=Test.objects.all())
    score = serializers.IntegerField(read_only=True, source='get_score')
    
    class Meta:
        model = Completion
        fields = ('id', 'user', 'test', 'answers', 'score')
        read_only_fields = ('score', 'user')
    
    def create(self, validated_data):
        answers = validated_data.pop('answers')
        completion = Completion.objects.create(
            **validated_data
        )
        for answer_data in answers:
            answer_data['question'] = answer_data['question'].pk
            answer_serializer = AnswerCreationSerializer(data=answer_data)
            answer_serializer.is_valid(raise_exception=True)
            answer_serializer.save(completion=completion)
        return completion
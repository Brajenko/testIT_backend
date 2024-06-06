from typing import Union

from rest_framework import serializers

from drf_spectacular.utils import extend_schema_serializer

from groups.models import Group
from groups.serializers import GroupWithoutMembersSerializer
from .models import *

class VariantIsCorrectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Variant
        fields = ('id', 'text', 'is_correct')
        read_only_fields = ('id', )

class VariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Variant
        fields = ('id', 'text')
        read_only_fields = ('id', )

@extend_schema_serializer(
    exclude_fields=('question',)
)
class BodyCreationSerializer(serializers.Serializer):
    variants = VariantIsCorrectSerializer(many=True, required=False)
    testing_code = serializers.CharField(required=False)
    question = serializers.PrimaryKeyRelatedField(queryset=Question.objects.all(), required=False)
    strict_score = serializers.BooleanField(required=False)

    def to_representation(self, instance):
        """Create representation based on question type"""
        if instance.question.type is None:
            raise ValueError('Question type is not defined')
        match instance.question.type:
            case 'code':
                return {'testing_code': instance.testing_code}
            case 'radio':
                return {'variants': VariantIsCorrectSerializer(instance.variants.all(), many=True).data}
            case 'check':
                return {'variants': VariantIsCorrectSerializer(instance.variants.all(), many=True).data, 'strict_score': instance.strict_score}
            case 'text':
                return {'variants': VariantIsCorrectSerializer(instance.variants.filter(is_correct=True), many=True).data}
            case _:
                return super().to_representation(instance)
    
    def create(self, validated_data):
        """Creates body with variants"""
        question = validated_data['question']
        variants = validated_data.pop('variants', [])
        # create question body based on question type
        Body: QuestionBody = {
            'text': TextBody,
            'radio': RadioBody,
            'check': CheckBody,
            'code': CodeBody,
        }[question.type]
        created_body = Body.objects.create(**validated_data)
        
        # create variants for text, radio and check questions
        if question.type in ['text', 'radio', 'check']:
            created_variants = []
            for variant in variants:
                created_variants.append(
                    Variant.objects.create(**variant)
                )
            created_body.variants.set(created_variants) # type: ignore

        return created_body

class QuestionCreationSerializer(serializers.ModelSerializer):
    body = BodyCreationSerializer()
    test = serializers.PrimaryKeyRelatedField(queryset=Test.objects.all(), required=False)

    class Meta:
        model = Question
        fields = ('id', 'text', 'test', 'type', 'points', 'number_in_test', 'body')
        extra_kwargs = {
            'test': {'write_only': True},
        }
    
    def create(self, validated_data):
        """Creates question with body"""
        body_data = validated_data.pop('body')
        question = Question.objects.create(**validated_data)
        body_data['question'] = question.pk
        body_serializer = BodyCreationSerializer(data=body_data)
        body_serializer.is_valid(raise_exception=True)
        body_serializer.save()
        return question
    
    def validate(self, attrs):
        # validate variants base on question type
        body = attrs['body']
        qtype = attrs['type']
        if body.get('variants'):
            variants = body['variants']
            correct_count = 0
            for variant in variants:
                if variant.get('is_correct', True):
                    correct_count += 1
            match qtype:
                case 'radio':
                    if correct_count != 1:
                        raise serializers.ValidationError('Radio question must have exactly one correct variant')
                case 'check':
                    if correct_count < 1:
                        raise serializers.ValidationError('Check question must have at least one correct variant')
                case 'text':
                    if correct_count < 1:
                        raise serializers.ValidationError('Text question must have at least one correct variant')
        return attrs

class TestCreationSerializer(serializers.ModelSerializer):
    questions = QuestionCreationSerializer(many=True)
    available_for = GroupWithoutMembersSerializer(many=True, read_only=True)
    
    class Meta:
        model = Test
        fields = ('id', 'name', 'creator', 'questions', 'available_for', 'public_uuid')
        read_only_fields = ('creator', 'public_uuid')

    def create(self, validated_data):
        """Creates test with questions"""
        questions = validated_data.pop('questions')
        validated_data.update({'creator': self.context['request'].user})
        test = Test.objects.create(**validated_data)
        for question in questions:
            question['test'] = test.pk
            question_serializer = QuestionCreationSerializer(data=question)
            question_serializer.is_valid(raise_exception=True)
            question_serializer.save()
        return test
    
    def validate_questions(self, questions):
        # check if all question numbers in test are unique
        qnumbers = set()
        for question in questions:
            number = question.get('number_in_test')
            if number in qnumbers:
                raise serializers.ValidationError('Question numbers must be unique')
            qnumbers.add(number)
        return questions


class CompletionVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Variant
        fields = ('id', 'text')
        extra_kwargs = {
            'id': {'required': False},
            'text': {'required': False}
        }

class BodySerializer(serializers.Serializer):
    variants = VariantSerializer(many=True, required=False)
    testing_code = serializers.CharField(required=False)
    strict_score = serializers.BooleanField(required=False)
    
    def to_representation(self, instance):
        """Create representation based on question type"""
        if instance.question.type is None:
            raise ValueError('Question type is not defined')
        match instance.question.type:
            case 'code' | 'text':
                return {}
            case 'radio':
                return {'variants': VariantSerializer(instance.variants.all(), many=True).data}
            case 'check':
                return {'variants': VariantSerializer(instance.variants.all(), many=True).data, 'strict_score': instance.strict_score}
            case _:
                return super().to_representation(instance)
            
class QuestionSerializer(serializers.ModelSerializer):
    body = BodySerializer()

    class Meta:
        model = Question
        fields = ('id', 'text', 'type', 'number_in_test', 'points', 'body')

class TestSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True)
    class Meta:
        model = Test
        fields = ('id', 'name', 'creator', 'questions', 'public_uuid')
        read_only_fields = ('id', 'name', 'creator', 'questions', 'public_uuid')

class AllowToGroupSerializer(serializers.Serializer):
    group = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all())

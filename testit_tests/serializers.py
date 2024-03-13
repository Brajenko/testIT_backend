from rest_framework.serializers import ModelSerializer, ValidationError, IntegerField
from drf_writable_nested.serializers import WritableNestedModelSerializer
from .models import *

from drf_spectacular.utils import extend_schema_serializer, OpenApiExample


class TextQuestionSerializer(ModelSerializer):
    class Meta:
        model = TextQuestion
        fields = ('id', 'title', 'description', 'number_in_test', 'answer')


class RadioQuestionSerializer(ModelSerializer):
    class Meta:
        model = RadioQuestion
        fields = ('id', 'title', 'description',
                  'number_in_test', 'variants', 'answer')
    
    def validate(self, attrs):
        """
        Check if answer presented in variants
        """
        if attrs['answer'] not in attrs['variants']:
            raise ValidationError(f'Answer "{attrs['answer']}" must be in variants.')
        return super().validate(attrs)


class CheckQuestionSerializer(ModelSerializer):
    class Meta:
        model = CheckQuestion
        fields = ('id', 'title', 'description',
                  'number_in_test', 'variants', 'answers')
    
    def validate(self, attrs):
        """
        Check if answer presented in variants
        """
        for answer in attrs['answers']:
            if answer not in attrs['variants']:
                raise ValidationError(f'Answer "{answer}" must be in variants.')
        return super().validate(attrs)


class CodeQuestionSerializer(ModelSerializer):
    class Meta:
        model = CodeQuestion
        fields = ('id', 'title', 'description',
                  'number_in_test', 'testing_code')


class NoAnswerTextQuestionSerializer(TextQuestionSerializer):
    class Meta(TextQuestionSerializer.Meta):
        fields = ('id', 'title', 'description',
                  'number_in_test')


class NoAnswerRadioQuestionSerializer(RadioQuestionSerializer):
    class Meta(RadioQuestionSerializer.Meta):
        fields = ('id', 'title', 'description',
                  'number_in_test', 'variants')

class NoAnswerCheckQuestionSerializer(CheckQuestionSerializer):
    class Meta(CheckQuestionSerializer.Meta):
        fields = ('id', 'title', 'description',
                  'number_in_test', 'variants')

class NoAnswerCodeQuestionSerializer(CodeQuestionSerializer):
    class Meta(CodeQuestionSerializer.Meta):
        fields = ('id', 'title', 'description',
                  'number_in_test')


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'Valid example 1',
            summary='4 questions',
            description='Test with 4 questions with different types',
            value={
                "text_questions": [
                    {
                        "id": 1,
                        "title": "text question",
                        "description": "some description",
                        "number_in_test": 1,
                        "answer": "answer 1"
                    }
                ],
                "radio_questions": [
                    {
                        "id": 1,
                        "title": "radio question",
                        "description": "some description",
                        "number_in_test": 2,
                        "variants": [
                            "variant 1",
                            "variant 2",
                            "variant 3",
                            "variant 4"
                        ],
                        "answer": "variant 2"
                    }
                ],
                "check_questions": [
                    {
                        "id": 1,
                        "title": "check question",
                        "description": "some description",
                        "number_in_test": 3,
                        "variants": [
                            "variant 1",
                            "variant 2",
                            "variant 3",
                            "variant 4",
                            "variant 5",
                            "variant 6"
                        ],
                        "answers": [
                            "variant 1",
                            "variant 3",
                            "variant 4"
                        ]
                    }
                ],
                "code_questions": [
                    {
                        "id": 1,
                        "title": "code question",
                        "description": "some description",
                        "number_in_test": 4,
                        "testing_code": "print('this code works!!!')"
                    }
                ]
            },
            request_only=True,  # signal that example only applies to requests
        ),
        OpenApiExample(
            'Not Valid example',
            summary='4 questions 1 wrong',
            description='Test with 4 questions where radio question is wrong',
            value={
                "text_questions": [
                    {
                        "title": "text question",
                        "description": "some description",
                        "number_in_test": 1,
                        "answer": "answer 1"
                    }
                ],
                "radio_questions": [
                    {
                        "title": "radio question",
                        "description": "some description",
                        "number_in_test": 2,
                        "variants": [
                            "variant 1",
                            "variant 2",
                            "variant 3",
                            "variant 4"
                        ],
                        "answer": "variant 5"
                    }
                ],
                "check_questions": [
                    {
                        "title": "check question",
                        "description": "some description",
                        "number_in_test": 3,
                        "variants": [
                            "variant 1",
                            "variant 2",
                            "variant 3",
                            "variant 4",
                            "variant 5",
                            "variant 6"
                        ],
                        "answers": [
                            "variant 1",
                            "variant 3",
                            "variant 4"
                        ]
                    }
                ],
                "code_questions": [
                    {
                        "title": "code question",
                        "description": "some description",
                        "number_in_test": 4,
                        "testing_code": "print('this code works!!!')"
                    }
                ]
            },
            request_only=True,  # signal that example only applies to requests
        ),
    ]
)
class TestSerializer(WritableNestedModelSerializer):
    text_questions = TextQuestionSerializer(many=True)
    radio_questions = RadioQuestionSerializer(many=True)
    check_questions = CheckQuestionSerializer(many=True)
    code_questions = CodeQuestionSerializer(many=True)

    class Meta:
        model = Test
        fields = ['id', 'text_questions', 'radio_questions',
                  'check_questions', 'code_questions']

    def create(self, validated_data):
        """Adds user to data before creating"""
        user = self.context['request'].user
        validated_data['creator'] = user
        return super().create(validated_data)


class NoAnswerTestSerializer(ModelSerializer):
    text_questions = NoAnswerTextQuestionSerializer(many=True)
    radio_questions = NoAnswerRadioQuestionSerializer(many=True)
    check_questions = NoAnswerCheckQuestionSerializer(many=True)
    code_questions = NoAnswerCodeQuestionSerializer(many=True)

    class Meta:
        model = Test
        fields = ['id', 'text_questions', 'radio_questions',
                  'check_questions', 'code_questions']

class TextAnswerSerializer(ModelSerializer):
    class Meta:     
        model = TextAnswer
        fields = ['id', 'answer', 'question']

class RadioAnswerSerializer(ModelSerializer):
    class Meta:     
        model = RadioAnswer
        fields = ['id', 'answer', 'question']
    
    def validate(self, attrs):
        """
        Check if answer presented in question variants
        """
        if attrs['answer'] not in attrs['question'].variants:
            raise ValidationError(f'Answer "{attrs['answer']}" must be in variants.')
        return super().validate(attrs)

class CheckAnswerSerializer(ModelSerializer):
    class Meta:     
        model = CheckAnswer
        fields = ['id', 'answers', 'question']
    
    def validate(self, attrs):
        """
        Check if answers presented in question variants
        """
        for answer in attrs['answers']:
            if answer not in attrs['question'].variants:
                raise ValidationError(f'Answer "{answer}" must be in variants.')
        return super().validate(attrs)
    
class CodeAnswerSerializer(ModelSerializer):
    class Meta:     
        model = CodeAnswer
        fields = ['id', 'code', 'question']

class CompletionSerializer(WritableNestedModelSerializer):
    text_answers = TextAnswerSerializer(many=True)
    radio_answers = RadioAnswerSerializer(many=True)
    check_answers = CheckAnswerSerializer(many=True)
    code_answers = CodeAnswerSerializer(many=True)
    
    class Meta:
        model = Completion
        fields = ['id', 'test', 'text_answers', 'radio_answers', 'check_answers', 'code_answers']
    
    def create(self, validated_data):
        """Adds user to data before creating"""
        user = self.context['request'].user
        validated_data['student'] = user
        return super().create(validated_data)

class NoAnswersCompletionSerializer(CompletionSerializer):
    class Meta(CompletionSerializer.Meta):
        pass

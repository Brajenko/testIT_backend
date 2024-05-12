from rest_framework import serializers

from .models import *

class VariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Variant
        fields = ('id', 'text', 'is_correct')
        extra_kwargs = {
            'is_correct': {'write_only': True},
        }

class BodySerializer(serializers.ModelSerializer):
    variants = VariantSerializer(many=True, required=False)
    testing_code = serializers.CharField(required=False)
    
    
    def __init__(self, *args, **kwargs):
        # Initiate the superclass normally
        super(BodySerializer, self).__init__(*args, **kwargs)
        
        # get question type from context, instance or data
        type_from_context = self._context.get('type', None)
        type_from_instance = getattr(getattr(getattr(self, 'instance', None), 'question', None), 'type', None)
        type_from_data = getattr(
            Question.objects.filter(
                # get question id from initial data
                id=getattr(self, 'initial_data', {}).get('question_id', None)
            ).first(),
            'type',
            None
        )
        self.qtype = type_from_context or type_from_instance or type_from_data
        
    
    def to_representation(self, instance):
        """Create representation based on question type"""
        if self.qtype is None:
            raise ValueError('Question type is not defined')
        match self.qtype:
            case 'text':
                return {}
            case 'code':
                return {}
            case 'radio' | 'check':
                return {'variants': VariantSerializer(instance.variants.all(), many=True).data}
            case _:
                return super().to_representation(instance)
    
    def validate_variants(self, variants):
        """Validate variants based on question type"""
        # Get question type from context or initial data
        if self.qtype is None:
            raise ValueError('Question type is not defined')
        if self.qtype == 'code':
            return variants
        correct_count = 0
        for variant in variants:
            if variant.get('is_correct', True):
                correct_count += 1
        match self.qtype:
            case 'text':
                if correct_count < 1:
                    raise serializers.ValidationError('Text question must have at least one correct variant')
            case 'radio':
                if correct_count != 1:
                    raise serializers.ValidationError('Radio question must have exactly one correct variant')
            case 'check':
                if correct_count < 1:
                    raise serializers.ValidationError('Check question must have at least one correct variant')
        return variants
    
    def create(self, validated_data):
        question = Question.objects.get(id=validated_data['question_id'])
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

class QuestionSerializer(serializers.ModelSerializer):
    body = BodySerializer()

    class Meta:
        model = Question
        fields = ('id', 'title', 'type', 'description', 'test', 'number_in_test', 'body')
        
    def __init__(self, *args, **kwargs):
        # Initiate the superclass normally
        super(QuestionSerializer, self).__init__(*args, **kwargs)
        # add question type to context, so we can use it in BodySerializer
        type = None
        if getattr(self, 'initial_data', None):
            type = self.initial_data.get('type', None) # type: ignore
        elif getattr(self, 'instance', None):
            type = self.instance.type # type: ignore
        self._context.update({'type': type})
    
    def create(self, validated_data):
        body_data = validated_data.pop('body')
        question = Question.objects.create(**validated_data)
        body_data['question_id'] = question.pk
        body_serializer = BodySerializer(data=body_data)
        body_serializer.is_valid(raise_exception=True)
        body_serializer.save()
        return question

class TestSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True)
    
    class Meta:
        model = Test
        fields = ('id', 'name', 'creator', 'questions')
        read_only_fields = ('creator', )
        
    def create(self, validated_data):
        questions = validated_data.pop('questions')
        test = Test.objects.create(**validated_data)
        for question in questions:
            question['test'] = test
            question_serializer = QuestionSerializer(data=question)
            question_serializer.is_valid(raise_exception=True)
            question_serializer.save()
        return test

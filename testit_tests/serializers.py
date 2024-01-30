from rest_framework.serializers import ModelSerializer, ValidationError
from .models import Test, Completion

class TestSerializer(ModelSerializer):
    class Meta:
        model = Test
        fields = '__all__'
    
    def validate_content(self, content):
        if not content:
            raise ValidationError("This field is required.")
        for question_number, question in enumerate(content):
            variants = question.get('variants', None)
            test_cases = question.get('test_cases', None)
            answers = question.get('answers', None)
            match question['type']:
                case 'text':
                    if answers is None:
                        raise ValidationError('answer are not provided')
                case 'code':
                    if test_cases is None:
                        raise ValidationError('test_cases are not provided')
                case 'radio' | 'check':
                    if variants is None:
                        raise ValidationError('variants are not provided')
                    if answers is None:
                        raise ValidationError('answer are not provided')
        return content
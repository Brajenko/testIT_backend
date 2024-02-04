from collections import OrderedDict, Counter

from rest_framework.serializers import ModelSerializer, ValidationError, IntegerField
from .models import Test, Completion

class TestSerializer(ModelSerializer):
    class Meta:
        model = Test
        fields = "__all__"
    
    def validate_content(self, content):
        if not content:
            raise ValidationError("This field is required.")
        if type(content) is not list:
            raise ValidationError("This field must be list.")
        
        for qnumber, question in enumerate(content, 1):
            if type(question) is not dict:
                raise ValidationError("All objects must be dictionaries.")
            
            qtype = question.get("type", None)
            title = question.get("title", None)
            description = question.get("description", None)
            variants = question.get("variants", None)
            test_cases = question.get("test_cases", None)
            answers = question.get("answers", None)
            
            if not qtype:
                raise ValidationError(f"Question {qnumber}: Question type is not provided.") 
            elif qtype not in ("text", "code", "radio", "check"):
                raise ValidationError(f"Question {qnumber}: Question type is in wrong format.")
            
            if not title:
                raise ValidationError(f"Question {qnumber}: Question title is not provided.")
            elif type(title) is not str:
                raise ValidationError(f"Question {qnumber}: Question title must be string.")
                        
            if qtype == "text":
                # Проверим, что варианты ответов существуют
                if not answers or type(answers) is not list:
                    raise ValidationError(f"Question {qnumber}: Answers (list) is required.")
                if any(map(lambda ans: type(ans) is not str, answers)):
                    raise ValidationError(f"Question {qnumber}: Answers must be strings.")
            elif qtype == "code":
                # Проверим, что-нибудь)))
                # Например валидируем тесткейсы
                ...
            elif qtype in ("radio", "check"):
                # Проверим, что есть варианты и правильные варианты,
                # и что правильные варианты есть в обычных
                if not answers or type(answers) is not list:
                    raise ValidationError(f"Question {qnumber}: Answers (list) is required.")
                if any(map(lambda ans: type(ans) is not str, answers)):
                    raise ValidationError(f"Question {qnumber}: Answers must be strings.")
                if not variants or type(variants) is not list:
                    raise ValidationError(f"Question {qnumber}: Variants (list) is required.")
                if any(map(lambda var: type(var) is not str, variants)):
                    raise ValidationError(f"Question {qnumber}: Variants must be strings.")
                for answer in answers:
                    if answer not in variants:
                        raise ValidationError(f"Question {qnumber}: Answer '{answer}' not in variants list.")
            
        return content


class CompletionSerializer(ModelSerializer):
    class Meta:
        model = Completion
        fields = ("__all__")
    
    def validate_content(self, content):
        # Проверим что в content нужные типы данных
        if not content:
            raise ValidationError(f"Content is required.")
        if type(content) is not list:
            raise ValidationError(f"Content must be list.")
        for ans in content:
            if type(ans) is not list and type(ans) is not str and type(ans) is not int:
                raise ValidationError(f"Wrong answers format.")
        return content
    
    def validate(self, data: OrderedDict):
        test: Test = data["test"]
        student = data["student"]
        content: list = data["content"]
        score = 0
        for qnumber, (question, answer) in enumerate(zip(test.content, content), 1):
            # Валидация
            if question["type"] in ("radio", "text"):
                if type(answer) is not str and type(answer) is not list and len(answer) != 1:
                    raise ValidationError(f"Question {qnumber}: Multiple answers for question with only one answer.")
            if question["type"] == "radio":
                if answer not in question["variants"]:
                    raise ValidationError(f"Question {qnumber}: Answer not in question variants.")
            if question["type"] == "check":
                for ans in answer:
                    if ans not in question["variants"]:
                        raise ValidationError(f"Question {qnumber}: Answer not in question variants.")
                    
            # Подсчет очков
            if question["type"] in ("radio", "text"):
                if answer in question["answers"]:
                    score += 10
            elif question["type"] == "check":
                # за каждый неправильный вариант (либо лишний, либо не отмеченный) снимаем по 3 очка,
                # в минус уйти нельзя max(0))
                answers_count = len(question["answers"])
                right_answers = list((Counter(question["answers"]) & Counter(answer)).elements())
                score += max(10 - abs(len(right_answers) - answers_count) * 3, 0)
                
        data["score"] = score
        
        return data
    
    # def create(self, validated_data):
    #     compl = Completion()
    #     compl.student = validated_data["student"]
    #     compl.test = validated_data["test"]
    #     compl.score = validated_data["score"]
    #     compl.content = validated_data["content"]
        
    #     return compl
        
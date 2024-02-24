from collections import OrderedDict, Counter
from typing import Optional

from rest_framework.serializers import ModelSerializer, ValidationError, IntegerField
from .models import Test, Completion


class ParseQuestionError:
    def __init__(self, error_text: str, qnumber: Optional[int] = None) -> None:
        if qnumber is None:
            raise ValidationError(error_text)
        raise ValidationError(f"Question {qnumber}: {error_text}")


class TestSerializer(ModelSerializer):
    class Meta:
        model = Test
        fields = "__all__"
    
    def validate_content(self, content):
        if type(content) is not list:
            raise ParseQuestionError("This field must be list.")
        for qnumber, question in enumerate(content, 1):
            if type(question) is not dict:
                raise ParseQuestionError("All objects must be dictionaries.")
            qtype = question.get("type", None)
            if not qtype:
                raise ParseQuestionError("Question type is not provided.", qnumber)
            title = question.get("title", None)
            description = question.get("description", None)
            variants = question.get("variants", None)
            test_cases = question.get("test_cases", None)
            answers = question.get("answers", None)
            
            if not qtype:
                raise ParseQuestionError(f"Question type is not provided.", qnumber) 
            elif qtype not in ("text", "code", "radio", "check"):
                raise ParseQuestionError(f"Question type is in wrong format.", qnumber)
            
            if not title:
                raise ParseQuestionError(f"Question title is not provided.", qnumber)
            elif type(title) is not str:
                raise ParseQuestionError(f"Question title must be string.", qnumber)
                        
            if qtype == "text":
                # Проверим, что варианты ответов существуют
                if not answers or type(answers) is not list:
                    raise ParseQuestionError(f"Answers (list) is required.", qnumber)
                if any(map(lambda ans: type(ans) is not str, answers)):
                    raise ParseQuestionError(f"Answers must be strings.", qnumber)
            elif qtype == "code":
                # Проверим, что-нибудь)))
                # Например валидируем тесткейсы
                ...
            elif qtype in ("radio", "check"):
                # Проверим, что есть варианты и правильные варианты,
                # и что правильные варианты есть в обычных
                if not answers or type(answers) is not list:
                    raise ParseQuestionError(f"Answers (list) is required.", qnumber)
                if any(map(lambda ans: type(ans) is not str, answers)):
                    raise ParseQuestionError(f"Answers must be strings.", qnumber)
                if not variants or type(variants) is not list:
                    raise ParseQuestionError(f"Variants (list) is required.", qnumber)
                if any(map(lambda var: type(var) is not str, variants)):
                    raise ParseQuestionError(f"Variants must be strings.", qnumber)
                for answer in answers:
                    if answer not in variants:
                        raise ParseQuestionError(f"Answer '{answer}' not in variants list.", qnumber)
            
        return content


class CompletionSerializer(ModelSerializer):
    class Meta:
        model = Completion
        fields = ("__all__")
    
    def validate_content(self, content):
        # Проверим что в content нужные типы данных
        if not content:
            raise ParseQuestionError(f"Content is required.")
        if type(content) is not list:
            raise ParseQuestionError(f"Content must be list.")
        for ans in content:
            if type(ans) is not list and type(ans) is not str and type(ans) is not int:
                raise ParseQuestionError(f"Wrong answers format.")
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
                    raise ParseQuestionError(f"Multiple answers for question with only one answer.", qnumber)
            if question["type"] == "radio":
                if answer not in question["variants"]:
                    raise ParseQuestionError(f"Answer not in question variants.", qnumber)
            if question["type"] == "check":
                for ans in answer:
                    if ans not in question["variants"]:
                        raise ParseQuestionError(f"Answer not in question variants.", qnumber)
                    
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
        
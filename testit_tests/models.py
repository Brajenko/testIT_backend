import uuid

from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.contrib.auth import get_user_model


User = get_user_model()


class AbstractQuestion(models.Model):
    class Meta:
        abstract = True
        
    title = models.CharField(max_length=255)
    description = models.TextField(max_length=511)
    number_in_test = models.PositiveSmallIntegerField()

class AbstractQuestionWithAnswer(AbstractQuestion):
    class Meta:
        abstract = True
        
    answer = models.CharField(max_length=255)
    
class AbstractQuestionWithAnswers(AbstractQuestion):
    class Meta:
        abstract = True
        
    answers = ArrayField(base_field=models.CharField())
    
class AbstractQuestionWithVariants(AbstractQuestion):
    class Meta:
        abstract = True
        
    variants = ArrayField(base_field=models.CharField())

class TextQuestion(AbstractQuestionWithAnswer):
    pass

class RadioQuestion(AbstractQuestionWithAnswer, AbstractQuestionWithVariants):
    pass

class CheckQuestion(AbstractQuestionWithAnswers, AbstractQuestionWithVariants):
    pass

class CodeQuestion(AbstractQuestion):
    testing_code = models.TextField()
    

class Test(models.Model):
    public_uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    text_questions = models.ManyToManyField(TextQuestion)
    radio_questions = models.ManyToManyField(RadioQuestion)
    check_questions = models.ManyToManyField(CheckQuestion)
    code_questions = models.ManyToManyField(CodeQuestion)

class AbstractAnswer(models.Model):
    class Meta:
        abstract = True
        
class AbstractAnswerWithTextAnswer(AbstractAnswer):
    class Meta:
        abstract = True
    answer = models.CharField(max_length=255)

class TextAnswer(AbstractAnswerWithTextAnswer):
    question = models.ForeignKey(TextQuestion, on_delete=models.CASCADE)

class RadioAnswer(AbstractAnswerWithTextAnswer):
    question = models.ForeignKey(RadioQuestion, on_delete=models.CASCADE)

class CheckAnswer(AbstractAnswer):
    question = models.ForeignKey(CheckQuestion, on_delete=models.CASCADE)
    answers = ArrayField(models.CharField())

class CodeAnswer(AbstractAnswer):
    question = models.ForeignKey(CodeQuestion, on_delete=models.CASCADE)
    code = models.TextField()

class Completion(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    text_answers = models.ManyToManyField(TextAnswer)
    radio_answers = models.ManyToManyField(RadioAnswer)
    check_answers = models.ManyToManyField(CheckAnswer)
    code_answers = models.ManyToManyField(CodeAnswer)
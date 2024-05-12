from django.utils.translation import gettext_lazy as _
from django.db import models

class Question(models.Model):
    title = models.CharField(_('title'), max_length=150)
    description = models.TextField(_('description'), blank=True, default='')
    type = models.CharField(_('question type'), max_length=10, choices=(
        ('text', 'text'),
        ('radio', 'radio'),
        ('check', 'check'),
        ('code', 'code'),
    ))
    test = models.ForeignKey('Test', on_delete=models.CASCADE, related_name='questions')
    number_in_test = models.PositiveSmallIntegerField(_('question position in test'), default=1)

    @property
    def body(self) -> 'QuestionBody':
        """Returns question body based on question type"""
        body_attr_name = self.type + 'body_set'
        return getattr(self, body_attr_name).first() 

    def __str__(self) -> str:
        return self.title

class Variant(models.Model):
    text = models.TextField(_('variant text'))
    is_correct = models.BooleanField(_('is variant correct'), default=True)

class QuestionBody(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    
    class Meta:
        abstract = True
    
class TextBody(QuestionBody):
    variants = models.ManyToManyField(Variant, related_name='text_question')
    
class CodeBody(QuestionBody):
    testing_code = models.TextField(_('testing code'))
    
class RadioBody(QuestionBody):
    variants = models.ManyToManyField(Variant, related_name='radio_question')
    
class CheckBody(QuestionBody):
    variants = models.ManyToManyField(Variant, related_name='check_question')
    
class Test(models.Model):
    name = models.CharField(_('test name'), max_length=150)
    creator = models.ForeignKey('users.User', on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.name
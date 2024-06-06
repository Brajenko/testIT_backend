import random
import string

from django.db import models
from django.utils.translation import gettext_lazy as _


def get_length_8_uuid() -> str:
    alphabet = string.ascii_lowercase + string.digits
    return ''.join(random.choices(alphabet, k=8))


class Question(models.Model):
    text = models.TextField(_('text'))
    type = models.CharField(
        _('question type'),
        max_length=10,
        choices=(
            ('text', 'text'),
            ('radio', 'radio'),
            ('check', 'check'),
            ('code', 'code'),
        ),
    )
    test = models.ForeignKey('Test', on_delete=models.CASCADE, related_name='questions')
    number_in_test = models.PositiveSmallIntegerField(_('question position in test'), default=1)
    points = models.PositiveSmallIntegerField(_('points for question'), default=1)

    @property
    def body(self) -> 'QuestionBody':
        """Returns question body based on question type"""
        body_attr_name = self.type + 'body'
        return getattr(self, body_attr_name)

    def __str__(self) -> str:
        return self.text[:10]


class Variant(models.Model):
    text = models.CharField(_('variant text'))
    is_correct = models.BooleanField(_('is variant correct'), default=True)

    def __str__(self) -> str:
        return self.text


class QuestionBody(models.Model):
    question = models.OneToOneField(Question, on_delete=models.CASCADE)

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
    strict_score = models.BooleanField(_('is score calculation strict'), default=True)


class Test(models.Model):
    name = models.CharField(_('test name'), max_length=150)
    creator = models.ForeignKey('users.User', on_delete=models.CASCADE)
    available_for = models.ManyToManyField('auth.Group', related_name='available_tests')
    public_uuid = models.CharField(
        'public uuid', max_length=8, unique=True, blank=True, default=get_length_8_uuid
    )

    def __str__(self) -> str:
        return self.name

    def regenerate_uuid(self):
        self.public_uuid = get_length_8_uuid()
        self.save()
        return self.public_uuid

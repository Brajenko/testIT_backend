from django.db import models
from .utils import run_code


class Completion(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    test = models.ForeignKey('questions.Test', on_delete=models.CASCADE)
    score = models.PositiveSmallIntegerField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def get_score(self) -> int:
        user_score = 0
        for answer in self.answers.all():   # type: ignore
            user_score += answer.get_points()
        self.score = user_score
        self.save()
        return self.score


class Answer(models.Model):
    completion = models.ForeignKey(Completion, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey('questions.Question', on_delete=models.CASCADE)

    @property
    def body(self):
        return getattr(self, self.question.type + 'answerbody')

    def get_points(self):
        match self.question.type:
            case 'text' | 'radio':
                return self.question.points * self.body.picked_variant.is_correct
            case 'check':
                if self.question.body.strict_score:
                    return (
                        self.body.picked_variants.filter(is_correct=True).count()
                        == self.question.body.variants.filter(is_correct=True).count()
                    ) * self.question.points
                else:
                    return (
                        self.body.picked_variants.filter(is_correct=True).count()
                        / self.body.picked_variants.all().count()
                    ) * self.question.points
            case 'code':
                if self.body.is_correct is None:
                    run_result = run_code(
                        self.body.code + '\n' * 2 + self.question.body.testing_code
                    )
                    self.body.is_correct = run_result['is_correct']
                    self.body.errors = run_result['errors']
                    self.body.save()
                return self.body.is_correct * self.question.points


class AbstractAnswerBody(models.Model):
    answer = models.OneToOneField(Answer, on_delete=models.CASCADE)

    class Meta:
        abstract = True


class TextAnswerBody(AbstractAnswerBody):
    picked_variant = models.ForeignKey('questions.Variant', on_delete=models.CASCADE)


class RadioAnswerBody(AbstractAnswerBody):
    picked_variant = models.ForeignKey('questions.Variant', on_delete=models.CASCADE)


class CheckAnswerBody(AbstractAnswerBody):
    picked_variants = models.ManyToManyField('questions.Variant')


class CodeAnswerBody(AbstractAnswerBody):
    code = models.TextField()
    is_correct = models.BooleanField(null=True)
    errors = models.TextField(null=True, blank=True)

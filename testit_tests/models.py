from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()


class Test(models.Model):
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.JSONField()


class Completion(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    score = models.PositiveIntegerField()
    content = models.JSONField()
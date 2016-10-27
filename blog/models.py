from __future__ import unicode_literals

from django.db import models

# Create your models here.

class Blog(models.Model):
    name = models.CharField(max_length=50)
    text = models.TextField()
    time = models.DateTimeField()
    locked = models.BooleanField(default=0)

    @classmethod
    def exists(cls, id):
        return len(cls.objects.filter(id=id)) > 0
from __future__ import unicode_literals

from django.db import models

# Create your models here.

class Blog(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=50)
    text = models.TextField()

    @classmethod
    def getById(cls, id):
        return cls.objects.get(id=id)

    @classmethod
    def exists(cls, id):
        return len(cls.objects.filter(id=id)) > 0
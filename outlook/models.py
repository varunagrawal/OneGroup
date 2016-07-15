from django.db import models


class Contact(models.Model):
    name = models.CharField(max_length=256)
    email = models.EmailField()
    person_id = models.CharField(max_length=128)
    face_id = models.CharField(max_length=128)
    weight = models.FloatField()
    last_tagged = models.TimeField()
    group = models.CharField(max_length=128)



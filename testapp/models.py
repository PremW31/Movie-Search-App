
# Create your models here.
from django.db import models
from django.contrib.auth.models import User

class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie_id = models.IntegerField()
    title = models.CharField(max_length=255)
    poster = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.title
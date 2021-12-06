from django.db import models
from django.db.models.base import Model
from django.db.models.fields import related

# Create your models here.

class Creator(models.Model):
    creator_id = models.CharField(max_length=100, primary_key=True)
    creator_name = models.CharField(max_length=100)

    def __str__(self):
        return self.creator_name

class Avatar(models.Model):
    avatar_id = models.IntegerField(primary_key=True)
    avatar_name = models.CharField(max_length=100)
    imageURL = models.CharField(max_length=200)
    creator = models.ForeignKey(Creator, on_delete=models.CASCADE, related_name='avatars')
    price = models.IntegerField()
    created_at = models.DateTimeField()

    def __str__(self):
        return self.avatar_name

class Item(models.Model):
    item_id = models.IntegerField(primary_key=True)
    item_name = models.CharField(max_length=100)
    avatar = models.ManyToManyField(Avatar, related_name='items')
    imageURL = models.CharField(max_length=100)
    creator = models.ForeignKey(Creator, on_delete=models.CASCADE, related_name='items')
    price = models.IntegerField()
    created_at = models.DateTimeField()

    def __str__(self):
        return self.item_name
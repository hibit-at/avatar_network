from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Creator(models.Model):
    creator_id = models.CharField(max_length=200, primary_key=True)
    creator_name = models.CharField(max_length=200)

    def __str__(self):
        return self.creator_name


class Avatar(models.Model):
    avatar_id = models.IntegerField(primary_key=True)
    avatar_name = models.CharField(max_length=200)
    imageURL = models.CharField(max_length=200)
    creator = models.ForeignKey(
        Creator, on_delete=models.CASCADE, related_name='avatars')
    price = models.IntegerField()
    created_at = models.DateTimeField()
    item_hot = models.IntegerField(default=0)
    item_num_0 = models.IntegerField(default=0)
    item_num_1 = models.IntegerField(default=0)
    item_num_2 = models.IntegerField(default=0)
    item_num_3 = models.IntegerField(default=0)
    item_num_4 = models.IntegerField(default=0)
    item_num_5 = models.IntegerField(default=0)
    item_num_6 = models.IntegerField(default=0)

    def __str__(self):
        return self.avatar_name


class Item(models.Model):
    item_id = models.IntegerField(primary_key=True)
    item_name = models.CharField(max_length=200)
    avatar = models.ManyToManyField(Avatar, related_name='items', blank=True)
    imageURL = models.CharField(max_length=200)
    creator = models.ForeignKey(
        Creator, on_delete=models.CASCADE, related_name='items')
    price = models.IntegerField()
    created_at = models.DateTimeField()

    def __str__(self):
        return self.item_name


class Customer(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, primary_key=True)
    VRCID = models.CharField(max_length=100)
    message = models.CharField(max_length=100)
    isSupporter = models.BooleanField(default=False)

    def __str__(self):
        if self.VRCID != '':
            return str(self.VRCID)
        else:
            return str(self.user)


class Folder(models.Model):
    editor = models.ForeignKey(Customer, on_delete=models.CASCADE)
    name = models.TextField(max_length=50, default='')
    description = models.TextField(max_length=100)
    fav_avatar = models.ManyToManyField(Avatar)
    fav_item = models.ManyToManyField(Item)
    isOpen = models.BooleanField(default=False)

    def __str__(self):
        return self.name

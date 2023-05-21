import requests
import re
import os
import sys
import django
from datetime import datetime, timedelta
import pytz


def process():

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kaogaii2.settings')
    django.setup()
    from app.models import Avatar

    for avatar in Avatar.objects.all():
        print(avatar)
        avatar.item_num_6 = avatar.item_num_5
        avatar.item_num_5 = avatar.item_num_4
        avatar.item_num_4 = avatar.item_num_3
        avatar.item_num_3 = avatar.item_num_2
        avatar.item_num_2 = avatar.item_num_1
        avatar.item_num_1 = avatar.item_num_0
        avatar.item_num_0 = avatar.items.all().count()
        avatar.item_hot = avatar.item_num_0 - avatar.item_num_6
        avatar.save()

if __name__ == '__main__':
    process()

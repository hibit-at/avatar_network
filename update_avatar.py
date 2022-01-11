import requests
import re
import os
import sys
import django
from datetime import datetime, timedelta
import pytz

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kaogaii2.settings')
django.setup()
from app.models import Avatar, Item

criteria = datetime.now(pytz.timezone('Asia/Tokyo')) - timedelta(days=7)

for avatar in Avatar.objects.filter(created_at__lt = criteria).order_by('created_at')[:100]:
    avatar_id = avatar.avatar_id
    print(f'{avatar_id} {avatar}')
    # link process
    url = f"https://booth.pm/ja/items/{avatar_id}"
    txt = requests.get(url).text
    if 'BOOTH | お探しの商品が見つかりませんでした… (404)' in txt:
        print(f'{avatar} is deleted')
        avatar.delete()
        continue
    pat = r'<script type="application/ld\+json">(.*?)</script>'
    check = re.findall(pat,txt)
    if len(check) == 0:
        print('parse impossible')
        avatar.created_at = datetime.now(pytz.timezone('Asia/Tokyo'))
        avatar.save()
        continue
    avatar.created_at = datetime.now(pytz.timezone('Asia/Tokyo'))
    avatar.save()
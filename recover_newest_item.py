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

for item in Item.objects.order_by('-created_at'):
    item_id = item.item_id
    print(f'{item_id} {item}')
    # link process
    url = f"https://booth.pm/ja/items/{item_id}"
    txt = requests.get(url).text
    if 'BOOTH | お探しの商品が見つかりませんでした… (404)' in txt:
        print(f'{item} is deleted')
        item.delete()
        continue
    pat = r'<script type="application/ld\+json">(.*?)</script>'
    check = re.findall(pat,txt)
    if len(check) == 0:
        print('parse impossible')
        item.created_at = datetime.now(pytz.timezone('Asia/Tokyo'))
        item.save()
        continue
    main_txt = re.findall(pat,txt)[0]
    pat = r'https://booth.pm/(.*?)/items/(\d+)'
    link_ids = re.findall(pat,main_txt)
    link_ids = [L[1] for L in link_ids]
    pat = r'https://[0-9a-zA-Z_\-]+.booth.pm/items/(\d+)'
    link_ids2 = re.findall(pat,main_txt)
    link_ids.extend(link_ids2)
    pat = r'<script id="json_modules" type="application/json">(.*?)</script>'
    scr_txt = re.findall(pat,txt)[0]
    pat = r'https://booth.pm/(.*?)/items/(\d+)'
    link_ids3 = re.findall(pat,scr_txt)
    link_ids3 = [L[1] for L in link_ids3]
    pat = r'https://[0-9a-zA-Z_\-]+.booth.pm/items/(\d+)'
    link_ids4 = re.findall(pat,scr_txt)
    link_ids.extend(link_ids3)
    link_ids.extend(link_ids4)
    link_ids = list(set(link_ids))
    print(link_ids)
    for link_id in link_ids:
        if Avatar.objects.filter(avatar_id = link_id).exists():
            avatar_object = Avatar.objects.get(avatar_id = link_id)
            item.avatar.add(avatar_object)
            print(f'{avatar_object}({link_id}) linked!')
    item.created_at = datetime.now(pytz.timezone('Asia/Tokyo'))
    item.save()
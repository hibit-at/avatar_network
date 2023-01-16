

import requests
import re
import os
import sys
import django
from datetime import datetime, timedelta
import pytz

from name_validation import org_rep

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kaogaii2.settings')
django.setup()
from app.models import Creator, Item, Avatar

page = 1

while(True):
    print(page)
    url = f'https://booth.pm/ja/browse/3D%E8%A1%A3%E8%A3%85%E3%83%BB%E8%A3%85%E9%A3%BE%E5%93%81?page={page}'
    txt = requests.get(url).text
    pat = r'data-tracking="click_item" href="https://booth.pm/ja/items/(.*?)">(.*?)</a></div>'
    items = re.findall(pat, txt)
    # print(items)
    if len(items) == 0:
        break
    pat = r'<div class="item-card__shop-name">(.*?)</div>'
    creator_names = re.findall(pat, txt)
    creator_names = [org_rep(c) for c in creator_names]
    pat = r'data-tracking="click" rel="noopener" href="https://(.*?).booth.pm/">'
    creator_ids = re.findall(pat, txt)
    pat = r'<div class="price u-text-primary u-text-left u-tpg-caption2">¥ (.*?)</div>'
    prices = re.findall(pat, txt)
    # print(prices)
    prices = [int(p.replace(',', '').replace('~', '')) for p in prices]
    pat = r'<div class="item-card__thumbnail-images">(.*?)</div>'
    imagedivs = re.findall(pat, txt)
    imageURLs = []
    for imagediv in imagedivs:
        pat = r'data-tracking="click_item" data-original="https://booth.pximg.net/(.*?)_base_resized.jpg"'
        res = re.findall(pat, imagediv)
        if len(res) == 0:
            imageURLs.append('error')
            continue
        imageURLs.append(f'https://booth.pximg.net/{res[0]}_base_resized.jpg')
    forzip = zip(items, creator_ids, creator_names, prices, imageURLs)
    for item, creator_id, creator_name, price, imageURL in forzip:
        item_id = item[0]
        item_name = item[1]
        item_name = org_rep(item_name)
        print(item_id, item_name, creator_id, creator_name, price)
        # creator add
        defaults = {'creator_name': creator_name}
        Creator.objects.update_or_create(
            creator_id=creator_id,
            defaults=defaults,
        )
        # item add
        update_time = datetime.now(pytz.timezone('Asia/Tokyo'))
        # if already keep time
        isExist = False
        if Item.objects.filter(item_id=item_id).exists():
            update_time = Item.objects.get(item_id=item_id).created_at
            isExist = True
        else:
            print('new item has come!')
        defaults = {
            'item_name': item_name,
            'price': price,
            'creator': Creator.objects.get(creator_id=creator_id),
            'imageURL': imageURL,
            'created_at': update_time,
        }
        item = Item.objects.update_or_create(
            item_id=item_id,
            defaults=defaults,
        )[0]
        # link process
        if isExist:
            continue
        url = f"https://booth.pm/ja/items/{item_id}"
        txt = requests.get(url).text
        if 'BOOTH | お探しの商品が見つかりませんでした… (404)' in txt:
            print(f'{item} is deleted')
            item.delete()
            continue
        pat = r'<script type="application/ld\+json">(.*?)</script>'
        check = re.findall(pat, txt)
        if len(check) == 0:
            print('parse impossible')
            item.created_at = datetime.now(pytz.timezone('Asia/Tokyo'))
            item.save()
            continue
        main_txt = re.findall(pat, txt)[0]
        pat = r'https://booth.pm/(.*?)/items/(\d+)'
        link_ids = re.findall(pat, main_txt)
        link_ids = [L[1] for L in link_ids]
        pat = r'https://[0-9a-zA-Z_\-]+.booth.pm/items/(\d+)'
        link_ids2 = re.findall(pat, main_txt)
        link_ids.extend(link_ids2)
        pat = r'<script type="application/ld\+json">(.*?)</script>'
        if len(re.findall(pat,txt)) == 0:
            # escpae for error 2023/1/17
            print('parse impossible')
            continue
        scr_txt = re.findall(pat, txt)[0]
        pat = r'https://booth.pm/(.*?)/items/(\d+)'
        link_ids3 = re.findall(pat, scr_txt)
        link_ids3 = [L[1] for L in link_ids3]
        pat = r'https://[0-9a-zA-Z_\-]+.booth.pm/items/(\d+)'
        link_ids4 = re.findall(pat, scr_txt)
        link_ids.extend(link_ids3)
        link_ids.extend(link_ids4)
        link_ids = list(set(link_ids))
        print(link_ids)
        for link_id in link_ids:
            if Avatar.objects.filter(avatar_id=link_id).exists():
                avatar_object = Avatar.objects.get(avatar_id=link_id)
                item.avatar.add(avatar_object)
                print(f'{avatar_object}({link_id}) linked!')
        item.created_at = datetime.now(pytz.timezone('Asia/Tokyo'))
        item.save()

    page += 1

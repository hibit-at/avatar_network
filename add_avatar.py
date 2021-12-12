import requests
import re
import os
import django
from datetime import date, datetime
import pytz

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kaogaii2.settings')
django.setup()

from app.models import Creator, Avatar

targets = [
    ('&amp;', '&'),
    ('&gt;', '>'),
    ('&lt;', '<'),
    ('&#39;', "'"),
    ('&quot;', '"'),
]


def name_validation(org):
    ans = org
    for target in targets:
        before = target[0]
        after = target[1]
        if before in org:
            ans = ans.replace(before, after)
    return ans


page = 1

while(True):
    print(page)
    url = f'https://booth.pm/ja/browse/3D%E3%82%AD%E3%83%A3%E3%83%A9%E3%82%AF%E3%82%BF%E3%83%BC?page={page}'
    txt = requests.get(url).text
    pat = r'https://([\w_].*?).?booth.pm/items/(\d+)'
    res = re.findall(pat, txt)
    if len(res) == 0:
        break
    pat = r'data-tracking="click_item" href="https://booth.pm/ja/items/(.*?)">(.*?)</a></div>'
    avatars = re.findall(pat, txt)
    pat = r'<div class="item-card__shop-name">(.*?)</div>'
    creator_names = re.findall(pat, txt)
    creator_names = [name_validation(c) for c in creator_names]
    pat = r'data-tracking="click" rel="noopener" href="https://(.*?).booth.pm/">'
    creator_ids = re.findall(pat, txt)
    pat = r'<div class="price u-text-primary u-text-left u-tpg-caption2">¥ (.*?)</div>'
    prices = re.findall(pat, txt)
    prices = [int(p.replace(',', '').replace('~', '')) for p in prices]
    pat = r'<div class="item-card__thumbnail-images">(.*?)</div>'
    imagedivs = re.findall(pat, txt)
    imageURLs = []
    for imagediv in imagedivs:
        pat = r'data-tracking="click_item" data-original="https://booth.pximg.net/(.*?)_base_resized.jpg"'
        res = re.findall(pat, imagediv)
        if len(res) > 0:
            imageURLs.append(
                f'https://booth.pximg.net/{res[0]}_base_resized.jpg')
        else:
            imageURLs.append(
                f'https://4.bp.blogspot.com/-toaP1vMGZAM/UNbkIddJNqI/AAAAAAAAJTk/MeuaawYOaLw/s1600/mark_question.png')
    forzip = zip(avatars, creator_names, creator_ids, prices, imageURLs)
    for avatar, creator_name, creator_id, price, imageURL in forzip:
        avatar_id = avatar[0]
        avatar_name = avatar[1]
        avatar_name = name_validation(avatar_name)
        print(avatar_id, avatar_name, creator_id, creator_name, price)
        # creator add
        defaults = {'creator_name': creator_name}
        Creator.objects.update_or_create(
            creator_id=creator_id,
            defaults=defaults,
        )
        # avatar add
        defaults = {
            'avatar_name': avatar_name,
            'price': price,
            'imageURL': imageURL,
            'creator': Creator.objects.get(creator_id=creator_id),
            'created_at': datetime.now(pytz.timezone('Asia/Tokyo'))
        }
        if Avatar.objects.filter(avatar_id=avatar_id).exists():
            defaults['created_at'] = Avatar.objects.get(avatar_id=avatar_id).created_at
        else:
            print('new avatar has been searched')
        Avatar.objects.update_or_create(
            avatar_id=avatar_id,
            defaults=defaults
        )

    page += 1

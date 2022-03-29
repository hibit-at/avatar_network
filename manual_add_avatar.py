import os
from datetime import datetime
from urllib import request
import pytz
import re
import requests


def add_avatar(avatar_id):
    import django
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

    url = f'https://booth.pm/ja/items/{avatar_id}'

    text = requests.get(url).text

    def name_validation(org):
        ans = org
        for target in targets:
            before = target[0]
            after = target[1]
            if before in org:
                ans = ans.replace(before, after)
        return ans


    pat = r'<title>(.*?) - (.*?) - BOOTH</title>'
    res = re.findall(pat, text)
    avatar_name = name_validation(res[0][0])
    print(avatar_name)

    pat = r'<div class="variation-price u-text-right">¥ (.*?)</div>'
    res = re.findall(pat,text)
    price = int(res[0].replace(',',''))
    print(price)

    pat = r'https://booth.pximg.net/c/620x620(.*?)_base_resized.jpg'
    res = re.findall(pat,text)
    imageURL = f'https://booth.pximg.net/c/620x620{res[0]}_base_resized.jpg'
    print(imageURL)

    pat = r'rel="noopener" href="https://(.*?).booth.pm/"><div class="u-d-flex u-align-items-center"><img alt="(.*?)"'
    res = re.findall(pat,text)
    creator_id, creator_name = res[0]
    print(creator_id, creator_name)

    defaults = {'creator_name': creator_name}
    creator = Creator.objects.update_or_create(
        creator_id=creator_id,
        defaults=defaults,
    )

    defaults = {
        'avatar_name': avatar_name,
        'price': price,
        'imageURL': imageURL,
        'creator': creator[0],
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

if __name__ == '__main__':
    add_avatar(0)

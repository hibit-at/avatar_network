import os
from datetime import datetime
import pytz
import re
import requests


def add_item(item_id):
    import django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kaogaii2.settings')
    django.setup()
    from app.models import Creator, Item

    targets = [
        ('&amp;', '&'),
        ('&gt;', '>'),
        ('&lt;', '<'),
        ('&#39;', "'"),
        ('&quot;', '"'),
    ]

    url = f'https://booth.pm/ja/items/{item_id}'

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
    item_name = name_validation(res[0][0])
    print(item_name)

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
        'item_name': item_name,
        'price': price,
        'imageURL': imageURL,
        'creator': creator[0],
        'created_at': datetime.now(pytz.timezone('Asia/Tokyo'))
    }

    if Item.objects.filter(item_id=item_id).exists():
        defaults['created_at'] = Item.objects.get(item_id=item_id).created_at
    else:
        print('new item has been searched')
    Item.objects.update_or_create(
        item_id=item_id,
        defaults=defaults
    )

if __name__ == '__main__':
    add_item(0)

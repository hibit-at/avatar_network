import os
from datetime import datetime
import pytz
import re
import requests


def add_item(item_id):
    import django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kaogaii2.settings')
    django.setup()
    from app.models import Creator, Item, Avatar

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
    item = Item.objects.update_or_create(
        item_id=item_id,
        defaults=defaults
    )[0]
    url = f"https://booth.pm/ja/items/{item_id}"
    txt = requests.get(url).text
    if 'BOOTH | お探しの商品が見つかりませんでした… (404)' in txt:
        print(f'{item} is deleted')
        item.delete()
        return
    pat = r'<script type="application/ld\+json">(.*?)</script>'
    check = re.findall(pat, txt)
    if len(check) == 0:
        print('parse impossible')
        item.created_at = datetime.now(pytz.timezone('Asia/Tokyo'))
        item.save()
        return
    main_txt = re.findall(pat, txt)[0]
    pat = r'https://booth.pm/(.*?)/items/(\d+)'
    link_ids = re.findall(pat, main_txt)
    link_ids = [L[1] for L in link_ids]
    pat = r'https://[0-9a-zA-Z_\-]+.booth.pm/items/(\d+)'
    link_ids2 = re.findall(pat, main_txt)
    link_ids.extend(link_ids2)
    txt = txt.replace('\n','')
    pat = r'<p class="autolink break-words font-noto-sans typography-16 whitespace-pre-line">(.*?)<section class="container">'
    scr_txt = re.findall(pat, txt)[0]
    print(scr_txt)
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

if __name__ == '__main__':
    add_item(0)

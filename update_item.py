import requests
import re
import os
import sys
import django
from datetime import datetime, timedelta
import pytz

def item_link_process(item_id):
    import django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kaogaii2.settings')
    django.setup()
    from app.models import Creator, Item, Avatar

    item = Item.objects.get(item_id=item_id)
    
    url = f"https://booth.pm/ja/items/{item_id}"
    txt = requests.get(url).text
    if 'BOOTH | お探しの商品が見つかりませんでした… (404)' in txt:
        print(f'{item} is deleted')
        item.delete()
        return
    # parse first step
    pat = r'<script type="application/ld\+json">(.*?)</script>'
    txt = txt.replace('\n','')
    check = re.findall(pat, txt)
    if len(check) > 0:
        main_txt = re.findall(pat, txt)[0]
        pat = r'https://booth.pm/(.*?)/items/(\d+)'
        link_ids = re.findall(pat, main_txt)
        link_ids = [L[1] for L in link_ids]
        pat = r'https://[0-9a-zA-Z_\-]+.booth.pm/items/(\d+)'
        link_ids2 = re.findall(pat, main_txt)
        link_ids.extend(link_ids2)
    else:
        print('first parse failure')
    # parse second step
    pat = r'<p class="autolink break-words font-noto-sans typography-16 whitespace-pre-line">(.*?)<section class="container">'
    if len(re.findall(pat,txt)) > 0:
        scr_txt = re.findall(pat, txt)[0]
        print(scr_txt)
        pat = r'https://booth.pm/(.*?)/items/(\d+)'
        link_ids3 = re.findall(pat, scr_txt)
        link_ids3 = [L[1] for L in link_ids3]
        pat = r'https://[0-9a-zA-Z_\-]+.booth.pm/items/(\d+)'
        link_ids4 = re.findall(pat, scr_txt)
        link_ids.extend(link_ids3)
        link_ids.extend(link_ids4)
    else:
        print('second step failure')
    # parse third step
    pat = r'<section class="shop__text">(.*?)<section>'
    check = re.findall(pat, txt)
    if len(check) > 0:
        main_txt = re.findall(pat, txt)[0]
        pat = r'https://booth.pm/(.*?)/items/(\d+)'
        link_ids = re.findall(pat, main_txt)
        link_ids = [L[1] for L in link_ids]
        pat = r'https://[0-9a-zA-Z_\-]+.booth.pm/items/(\d+)'
        link_ids2 = re.findall(pat, main_txt)
        link_ids.extend(link_ids2)
    link_ids = list(set(link_ids))
    print(link_ids)
    for link_id in link_ids:
        if Avatar.objects.filter(avatar_id=link_id).exists():
            avatar_object = Avatar.objects.get(avatar_id=link_id)
            item.avatar.add(avatar_object)
            print(f'{avatar_object}({link_id}) linked!')
    return

def process(force=False):
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kaogaii2.settings')
    django.setup()
    from app.models import Avatar, Item

    criteria = datetime.now(pytz.timezone('Asia/Tokyo')) - timedelta(days=7)

    target_items = Item.objects.all()
    if not force:
        target_items = target_items.filter(created_at__lt=criteria)
    target_items = target_items.order_by('created_at')[:100]

    for item in target_items:
        item_id = item.item_id
        print(f'{item_id} {item}')
        # link process
        item_link_process(item_id)
        item.created_at = datetime.now(pytz.timezone('Asia/Tokyo'))
        item.save()


if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] == 'force':
            print('force update')
            process(True)
    else:
        process()

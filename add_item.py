import requests
import re
import os
import sys
import django
from datetime import datetime
import pytz

ITEM_PATTERN = re.compile(r'data-tracking="click_item" href="https://booth.pm/ja/items/(.*?)">(.*?)</a></div>')
CREATOR_NAME_PATTERN = re.compile(r'<div class="item-card__shop-name">(.*?)</div>')
CREATOR_ID_PATTERN = re.compile(r'data-tracking="click" rel="noopener" href="https://(.*?).booth.pm/">')
PRICE_PATTERN = re.compile(r'<div class="price u-text-primary u-text-left u-tpg-caption2">¥ (.*?)</div>')
DIV_PATTERN =  re.compile(r'<div class="item-card__thumbnail-images">(.*?)</div>')
IMG_URL_PATTERN = re.compile(r'data-tracking="click_item" data-original="https://booth.pximg.net/(.*?)_base_resized.jpg"')

def build_url(page, keyword=None):
    base_url = f'https://booth.pm/ja/browse/3D%E8%A1%A3%E8%A3%85%E3%83%BB%E8%A3%85%E9%A3%BE%E5%93%81?page={page}'
    if keyword:
        return base_url + f'&q={requests.utils.quote(keyword)}'
    return base_url

def extract_price(price_str):
    return int(''.join(re.findall(r'\d', price_str)))

def extract_image_url(imagediv):
    match = re.search(IMG_URL_PATTERN, imagediv)
    return f'https://booth.pximg.net/{match.group(1)}_base_resized.jpg' if match else 'error'

def main(keyword=None):

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kaogaii2.settings')
    django.setup()
    from app.models import Creator, Item
    from update_item import item_link_process
    from name_validation import org_rep

    page = 1

    while(True):
        url = build_url(page, keyword)
        txt = requests.get(url).text
        items = ITEM_PATTERN.findall(txt)
        if len(items) == 0:
            break
        creator_names = [org_rep(name) for name in CREATOR_NAME_PATTERN.findall(txt)]
        creator_ids = CREATOR_ID_PATTERN.findall(txt)
        prices = [extract_price(price) for price in PRICE_PATTERN.findall(txt)]
        imagedivs =DIV_PATTERN.findall(txt)
        imageURLs = [extract_image_url(div) for div in imagedivs]
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
            # if already, keep time and skip link
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
            item_link_process(item_id)

        page += 1


if __name__ == '__main__':
    keyword = None
    if len(sys.argv) > 1:
        keyword = sys.argv[1]
    main(keyword)

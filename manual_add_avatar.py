import os
from datetime import datetime
import pytz
import re
import requests

from name_validation import org_rep

def add_avatar(avatar_id):
    import django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kaogaii2.settings')
    django.setup()
    from app.models import Creator, Avatar


    url = f'https://booth.pm/ja/items/{avatar_id}'
    text = requests.get(url).text
    pat = r'<title>(.*?) - (.*?) - BOOTH</title>'
    res = re.findall(pat, text)
    avatar_name = org_rep(res[0][0])
    print(avatar_name)

    pat = r'<div class="variation-price u-text-right">¥ (.*?)</div>'
    res = re.findall(pat,text)
    price = int(res[0].replace(',',''))
    print(price)

    pat = r'https://booth.pximg.net/c/620x620(.*?)_base_resized.jpg'
    res = re.findall(pat,text)
    imageURL = f'https://booth.pximg.net/c/620x620{res[0]}_base_resized.jpg'
    print(imageURL)

    # pat = r'rel="noopener" href="https://(.*?).booth.pm/"><div class="u-d-flex u-align-items-center"><img alt="(.*?)"'
    pat = r'rel="noopener" href="https://(.*?).booth.pm/"><img alt="(.*?)"'
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
    import sys
    arg = sys.argv
    if len(arg) == 2:
        add_avatar(arg[1])

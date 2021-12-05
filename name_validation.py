import requests
import re
import csv
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kaogaii2.settings')
django.setup()
from app.models import Creator, Avatar, Item

targets = [
    ('&amp;', '&'),
    ('&gt;', '>'),
    ('&lt;', '<'),
    ('&#39;', "'"),
    ('&quot;', '"'),
]


def org_rep(org):
    ans = org
    debug_count = 0
    for target in targets:
        before = target[0]
        after = target[1]
        if before in org:
            ans = ans.replace(before, after)
            print(f'{before} is replaced to {after} in {org}')
    return ans


for avatar in Avatar.objects.all():
    ans_name = avatar.avatar_name
    ans_name = org_rep(ans_name)
    avatar.avatar_name = ans_name
    avatar.save()

for item in Item.objects.all():
    ans_name = item.item_name
    ans_name = org_rep(ans_name)
    item.item_name = ans_name
    item.save()

for creator in Creator.objects.all():
    ans_name = creator.creator_name
    ans_name = org_rep(ans_name)
    creator.creator_name = ans_name
    creator.save()

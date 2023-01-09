import os
import django


def process():

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kaogaii2.settings')
    django.setup()
    from app.models import Avatar, Item, Folder

    #reset

    for avatar in Avatar.objects.all():
        avatar.want = 0
    
    for item in Item.objects.all():
        item.want = 0
        

if __name__ == '__main__':
    process()

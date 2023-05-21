import os

def weight_item_process(item_id):
    import django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kaogaii2.settings')
    django.setup()
    from app.models import Creator, Item, Avatar

    for item in Item.objects.all():
        # print(item)
        weight_value = 0
        for avatar in item.avatar.all():
            # print(f'...{avatar}')
            item_num = avatar.item_num_0
            # print(item_num)
            if(item_num == 0):
                item_num = 1
            weight_value += 1/item_num
        # print(weight_value)
        item.weight = weight_value
        item.save()

if __name__ == '__main__':
    weight_item_process(0)

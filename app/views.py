from django.shortcuts import render
from django.db.models import Q, Count

from app.forms import *
from app.models import *

# Create your views here.


def index(request):
    params = {}
    avatars = Avatar.objects.order_by('?')[:5]
    items = Item.objects.order_by('?')[:5]
    recent_avatars = Avatar.objects.order_by('-avatar_id')[:7]
    recent_items = Item.objects.order_by('-item_id')[:7]
    hot_avatars = Avatar.objects.order_by('-item_hot')[:5]
    params['avatars'] = avatars
    params['items'] = items
    params['recent_avatars'] = recent_avatars
    params['recent_items'] = recent_items
    params['hot_avatars'] = hot_avatars
    return render(request, 'index.html', params)


def creator(request, creator_id=''):
    creators = Creator.objects.all()
    avatar_query = Avatar.objects.annotate(num_items=Count('items'))
    avatar_query = avatar_query.order_by('price','-num_items')
    item_query =Item.objects.annotate(num_avatars=Count('avatar'))
    item_query = item_query.order_by('price','-num_avatars')
    creators = creators.prefetch_related(models.Prefetch(
        'avatars', queryset=avatar_query))
    creators = creators.prefetch_related(models.Prefetch(
        'items', queryset=item_query))
    creator = creators.get(creator_id=creator_id)
    params = {'creator': creator}
    return render(request, 'creator.html', params)


def creators(request, page=1, word='', free_only=False):
    if 'page' in request.GET:
        page = int(request.GET['page'])
    if 'word' in request.GET:
        word = request.GET['word']
    if 'free_only' in request.GET:
        free_only = request.GET['free_only']
    span = 9
    start = (page-1)*span
    end = page*span
    creators = Creator.objects.all()
    avatar_query = Avatar.objects.annotate(num_items=Count('items'))
    item_query = Item.objects.annotate(num_avatars=Count('avatar'))
    initial = {}
    if free_only:
        creators = creators.filter(Q(avatars__price=0) | Q(items__price=0))
        avatar_query = avatar_query.filter(price=0)
        item_query = item_query.filter(price=0)
        initial['free_only'] = free_only
    if word != '':
        creators = creators.filter(creator_name__contains=word)
        initial['word'] = word
    form = Filter(initial=initial)
    total = creators.count()
    avatar_query = avatar_query.order_by('price', '-num_items')
    item_query = item_query.order_by('price', '-num_avatars')
    creators = creators.prefetch_related(models.Prefetch(
        'avatars', queryset=avatar_query))
    creators = creators.prefetch_related(models.Prefetch(
        'items', queryset=item_query))
    creators = creators.annotate(total_item=Count('avatars__items'))
    creators = creators.order_by('-total_item')[start:end]
    params = {'creators': creators, 'page': page}
    params['form'] = form
    params['word'] = word
    params['free_only'] = free_only
    params['total'] = total
    return render(request, 'creators.html', params)


def avatar(request, avatar_id=1):
    params = {}
    creator_id = Avatar.objects.get(avatar_id=avatar_id).creator.creator_id
    items = Item.objects.annotate(num_avatars=Count('avatar'))
    items = items.filter(avatar__avatar_id=avatar_id)
    genuine_items = items.filter(creator__creator_id=creator_id)
    genuine_items = genuine_items.order_by('num_avatars', 'price')
    normal_items = items.exclude(creator__creator_id=creator_id)
    normal_items = normal_items.order_by('num_avatars', 'price')
    avatar = Avatar.objects.get(avatar_id=avatar_id)
    params['avatar'] = avatar
    params['normal_items'] = normal_items
    params['genuine_items'] = genuine_items
    return render(request, 'avatar.html', params)


def avatars(request, page=1, word='', free_only=False, sort_hot=False):
    params = {}
    if 'page' in request.GET:
        page = int(request.GET['page'])
    if 'word' in request.GET:
        word = request.GET['word']
    if 'free_only' in request.GET:
        free_only = request.GET['free_only']
    if 'sort_hot' in request.GET:
        sort_hot = request.GET['sort_hot']
    words = word.split()
    span = 18
    start = (page-1)*span
    end = page*span
    avatars = Avatar.objects.all()
    initial = {}
    if free_only:
        avatars = avatars.filter(price=0)
        initial['free_only'] = free_only
    if word != '':
        initial['word'] = word
        for w in words:
            avatars = avatars.filter(avatar_name__contains=w)
    params['total'] = avatars.count()
    if sort_hot:
        avatars = avatars.order_by('-item_hot','price')[start:end]
        initial['sort_hot'] = sort_hot
    else:
        avatars = avatars.annotate(num_items=Count('items'))
        avatars = avatars.order_by('-num_items', 'price')[start:end]
    params['avatars'] = avatars
    params['page'] = page
    params['free_only'] = free_only
    params['word'] = word
    form = Filter(initial=initial)
    params['form'] = form
    params['sort_hot'] = sort_hot
    return render(request, 'avatars.html', params)


def item(request, item_id=''):
    item = Item.objects.get(item_id=item_id)
    params = {'item': item}
    return render(request, 'item.html', params)


def items(request, page=1, word='', free_only=False):
    params = {}
    if 'page' in request.GET:
        page = int(request.GET['page'])
    if 'word' in request.GET:
        word = request.GET['word']
    if 'free_only' in request.GET:
        free_only = request.GET['free_only']
    words = word.split()
    print(words)
    span = 18
    start = (page-1)*span
    end = page*span
    items = Item.objects.annotate(num_avatars=Count('avatar'))
    initial = {}
    if free_only:
        items = items.filter(price=0)
        initial['free_only'] = free_only
    if word != '':
        initial['word'] = word
        for w in words:
            or_words = w.split('||')
            or_query = Q()
            for o in or_words:
                print(o)
                or_query = or_query | Q(item_name__contains=o)
            items = items.filter(or_query)
    params['total'] = items.count()
    items = items.order_by('-num_avatars', 'price')[start:end]
    params['items'] = items
    params['page'] = page
    params['free_only'] = free_only
    params['word'] = word
    form = Filter(initial=initial)
    params['form'] = form
    return render(request, 'items.html', params)


def info(request):
    params = {}
    avatars = Avatar.objects.annotate(num_items=Count('items'))
    avatars = avatars.order_by('-num_items')
    top_avatar_id = avatars[0].avatar_id
    items = Item.objects.annotate(num_avatars=Count('avatar'))
    items = items.order_by('-num_avatars')
    top_item_id = items[0].item_id
    params['top_avatar_id'] = top_avatar_id
    params['top_item_id'] = top_item_id
    return render(request, 'info.html', params)


def suspend(request):
    return render(request, 'suspend.html')


def debug(request):
    import datetime
    import pytz
    ago = datetime.datetime.now(pytz.timezone('Asia/Tokyo')) - datetime.timedelta(days=7)
    print(ago)
    avatar_new_cnt = Avatar.objects.filter(created_at__gt=ago).count()
    new_avatars = Avatar.objects.filter(
        created_at__gt=ago).order_by('-created_at')[:30]
    avatar_old_cnt = Avatar.objects.filter(created_at__lt=ago).count()
    old_avatars = Avatar.objects.filter(
        created_at__lt=ago).order_by('created_at')[:30]
    item_new_cnt = Item.objects.filter(created_at__gt=ago).count()
    new_items = Item.objects.filter(
        created_at__gt=ago).order_by('-created_at')[:30]
    item_old_cnt = Item.objects.filter(created_at__lt=ago).count()
    old_items = Item.objects.filter(
        created_at__lt=ago).order_by('created_at')[:30]
    params = {}
    params['new_avatars'] = new_avatars
    params['old_avatars'] = old_avatars
    params['avatar_new_cnt'] = avatar_new_cnt
    params['avatar_old_cnt'] = avatar_old_cnt
    params['new_items'] = new_items
    params['old_items'] = old_items
    params['item_new_cnt'] = item_new_cnt
    params['item_old_cnt'] = item_old_cnt
    return render(request, 'debug.html', params)

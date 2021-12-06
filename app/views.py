from django.shortcuts import render

from app.forms import *
from app.models import *
from django.db.models import Count

# Create your views here.


def index(request):
    params = {}
    avatars = Avatar.objects.order_by('?')[:5]
    items = Item.objects.order_by('?')[:5]
    recent_avatars = Avatar.objects.order_by('-created_at')[:7]
    recent_items = Item.objects.order_by('-created_at')[:7]
    params['avatars'] = avatars
    params['items'] = items
    params['recent_avatars'] = recent_avatars
    params['recent_items'] = recent_items
    return render(request, 'index.html', params)


def creator(request, creator_id=''):
    creator = Creator.objects.get(creator_id=creator_id)
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
    creators = Creator.objects.annotate(total_item=Count('avatars__items'))
    creators = creators.order_by('-total_item')[start:end]
    params = {'creators': creators, 'page': page}
    return render(request, 'creators.html', params)


def avatar(request, avatar_id=1):
    avatar = Avatar.objects.get(avatar_id=avatar_id)
    params = {'avatar': avatar}
    return render(request, 'avatar.html', params)


def avatars(request, page=1, word='', free_only=False):
    if 'page' in request.GET:
        page = int(request.GET['page'])
    if 'word' in request.GET:
        word = request.GET['word']
    if 'free_only' in request.GET:
        free_only = request.GET['free_only']
    span = 18
    start = (page-1)*span
    end = page*span
    avatars = Avatar.objects.annotate(num_items=Count('items'))
    initial = {}
    if free_only:
        avatars = avatars.filter(price=0)
        initial['free_only'] = free_only
    if word != '':
        avatars = avatars.filter(avatar_name__contains=word)
        initial['word'] = word
    avatars = avatars.order_by('-num_items')[start:end]
    params = {'avatars': avatars, 'page': page}
    params['free_only'] = free_only
    params['word'] = word
    form = Filter(initial=initial)
    params['form'] = form
    return render(request, 'avatars.html', params)


def item(request, item_id=''):
    item = Item.objects.get(item_id=item_id)
    params = {'item': item}
    return render(request, 'item.html', params)


def items(request, page=1, word='', free_only=False):
    if 'page' in request.GET:
        page = int(request.GET['page'])
    if 'word' in request.GET:
        word = request.GET['word']
    if 'free_only' in request.GET:
        free_only = request.GET['free_only']
    span = 18
    start = (page-1)*span
    end = page*span
    items = Item.objects.annotate(num_avatars=Count('avatar'))
    initial = {}
    if free_only:
        items = items.filter(price=0)
        initial['free_only'] = free_only
    if word != '':
        items = items.filter(item_name__contains=word)
        initial['word'] = word
    items = items.order_by('-num_avatars')[start:end]
    params = {'items': items, 'page': page}
    params['free_only'] = free_only
    params['word'] = word
    form = Filter(initial=initial)
    params['form'] = form
    return render(request, 'items.html', params)

from django.shortcuts import redirect, render
from django.db.models import Q, Count
from django.urls import reverse
from allauth.socialaccount.models import SocialAccount
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

from app.forms import *
from app.models import *

# utils

targets = [
    ('&amp;', '&'),
    ('&gt;', '>'),
    ('&lt;', '<'),
    ('&#39;', "'"),
    ('&quot;', '"'),
]


def name_validation(org):
    ans = org
    for target in targets:
        before = target[0]
        after = target[1]
        if before in org:
            ans = ans.replace(before, after)
    return ans

# Create your views here.


def get_random_avatars_and_items():
    avatars = Avatar.objects.order_by('?')[:5]
    items = Item.objects.order_by('?')[:5]
    return avatars, items


def get_recent_avatars_and_items():
    recent_avatars = Avatar.objects.order_by('-avatar_id')[:5]
    recent_items = Item.objects.order_by('-item_id')[:5]
    return recent_avatars, recent_items


def get_hot_avatars():
    hot_avatars = Avatar.objects.order_by('-item_hot')[:5]
    return hot_avatars


def get_wanted_avatars_and_items():
    wanted_avatars = Avatar.objects.all().annotate(
        want=Count('want_avatar')).exclude(want=0).order_by('-want')[:5]
    wanted_items = Item.objects.all().annotate(want=Count(
        'want_item')).exclude(want=0).order_by('-want')[:5]
    return wanted_avatars, wanted_items


def index(request):
    params = {}
    user = request.user
    if user.is_authenticated:
        social = SocialAccount.objects.get(user=user)
        params['social'] = social
        # activate
        if not Customer.objects.filter(user=user).exists():
            customer = Customer.objects.create(user=user)
            Folder.objects.create(
                editor=customer, name=f'{str(user)}\'s favorite')
            print('customer instance created')

    avatars, items = get_random_avatars_and_items()
    recent_avatars, recent_items = get_recent_avatars_and_items()
    hot_avatars = get_hot_avatars()
    wanted_avatars, wanted_items = get_wanted_avatars_and_items()
    supporters = Customer.objects.filter(
        isSupporter=True).exclude(user__is_staff=True)

    params.update({
        'avatars': avatars,
        'items': items,
        'recent_avatars': recent_avatars,
        'recent_items': recent_items,
        'hot_avatars': hot_avatars,
        'supporters': supporters,
        'wanted_avatars': wanted_avatars,
        'wanted_items': wanted_items,
    })

    return render(request, 'index.html', params)


def get_creator_with_avatars_and_items(creator_id):
    creators = Creator.objects.all()
    avatar_query = Avatar.objects.annotate(
        num_items=Count('items')).order_by('price', '-num_items')
    item_query = Item.objects.annotate(num_avatars=Count(
        'avatar')).order_by('price', '-num_avatars')

    creators = creators.prefetch_related(
        models.Prefetch('avatars', queryset=avatar_query))
    creators = creators.prefetch_related(
        models.Prefetch('items', queryset=item_query))

    return creators.get(creator_id=creator_id)


def creator(request, creator_id=''):
    params = {}
    user = request.user
    if user.is_authenticated:
        social = SocialAccount.objects.get(user=user)
        params['social'] = social

    creator = get_creator_with_avatars_and_items(creator_id)

    if Customer.objects.filter(highlight=creator).exists():
        setattr(creator, 'isHighlight', True)
    params['creator'] = creator

    if request.method == 'POST':
        post = request.POST
        print(post)
        if 'highlight' in post:
            user.customer.highlight = creator
            user.customer.save()
            return redirect('app:creator', creator_id=creator_id)
        if 'cancel' in post:
            user.customer.highlight = None
            user.customer.save()
            return redirect('app:creator', creator_id=creator_id)

    return render(request, 'creator.html', params)


def get_filtered_creators_with_avatars_and_items(word='', free_only=False, sort_item=None):
    creators = Creator.objects.all()
    avatar_query = Avatar.objects.annotate(num_items=Count('items'))
    item_query = Item.objects.annotate(num_avatars=Count('avatar'))

    if free_only:
        creators = creators.filter(Q(avatars__price=0) | Q(items__price=0))
        avatar_query = avatar_query.filter(price=0)
        item_query = item_query.filter(price=0)

    if word != '':
        creators = creators.filter(creator_name__contains=word)

    avatar_query = avatar_query.order_by('price', '-num_items')
    item_query = item_query.order_by('price', '-num_avatars')

    creators = creators.prefetch_related(
        models.Prefetch('avatars', queryset=avatar_query))
    creators = creators.prefetch_related(
        models.Prefetch('items', queryset=item_query))

    if sort_item is None:
        # sort_by_total_items
        creators = creators.annotate(total_item=Count(
            'avatars__items')).order_by('-total_item')
    else:
        # sort_by_total_avatars
        creators = creators.annotate(total_avatar=Count(
            'items__avatar')).order_by('-total_avatar')

    return creators


def creators(request, page=1, word='', free_only=False, sort_item=None):
    params = {}
    user = request.user
    if user.is_authenticated:
        social = SocialAccount.objects.get(user=user)
        params['social'] = social

    page = int(request.GET.get('page', page))
    word = request.GET.get('word', word)
    free_only = request.GET.get('free_only', free_only)

    span = 9
    start = (page-1)*span
    end = page*span

    creators = get_filtered_creators_with_avatars_and_items(
        word=word, free_only=free_only, sort_item=sort_item)

    total = creators.count()
    creators = creators[start:end]

    initial = {'word': word, 'free_only': free_only}
    form = Filter(initial=initial)

    params.update({
        'creators': creators,
        'page': page,
        'form': form,
        'word': word,
        'free_only': free_only,
        'total': total,
    })

    return render(request, 'creators.html', params)


def avatar(request, avatar_id=1, page=1, sort_latest=False):
    params = {}
    user = request.user
    avatar = Avatar.objects.get(avatar_id=avatar_id)
    if user.is_authenticated:
        social = SocialAccount.objects.get(user=user)
        params['social'] = social
        folders = Folder.objects.filter(
            editor=request.user.customer).order_by('-pk')
        some_added = False
        some_added_want = False
        for folder in folders:
            notadd = avatar not in folder.fav_avatar.all()
            setattr(folder, 'notadd', notadd)
            if not notadd:
                some_added = True
            notadd_want = avatar not in folder.want_avatar.all()
            setattr(folder, 'notadd_want', notadd_want)
            if not notadd_want:
                some_added_want = True
        params['folders'] = folders
        params['folders_some_added'] = some_added
        params['folders_some_added_want'] = some_added_want
    page = int(request.GET.get('page', page))
    sort_latest = request.GET.get('sort_latest', sort_latest)
    params['sort_latest'] = sort_latest
    span = 200
    start = (page-1)*span
    end = page*span
    creator_id = Avatar.objects.get(avatar_id=avatar_id).creator.creator_id
    items = Item.objects.annotate(num_avatars=Count('avatar'))
    items = items.filter(avatar__avatar_id=avatar_id)
    genuine_items = items.filter(creator__creator_id=creator_id)
    genuine_items = genuine_items.order_by('num_avatars', 'price')
    normal_items = items.exclude(creator__creator_id=creator_id)
    total = normal_items.count()
    print(sort_latest)
    if sort_latest:
        if sort_latest == 'off':
            redirect_url = reverse('app:avatar', args=[avatar_id])
            # redirect_url += '?page=' + page
            return redirect(redirect_url)
        normal_items = normal_items.order_by('-item_id')[start:end]
    else:
        normal_items = normal_items.order_by(
            'num_avatars', 'price', '-item_id')[start:end]
    for normal_item in normal_items:
        if Customer.objects.filter(highlight=normal_item.creator):
            print("hit")
            setattr(normal_item, 'isHighlight', True)
    params.update({
        'page': page,
        'avatar': avatar,
        'total': total,
        'normal_items': normal_items,
        'genuine_items': genuine_items,
    })
    if request.method == "POST":
        post = request.POST
        print(post)
        if 'add' in post:
            pk = post['add']
            folder = Folder.objects.get(pk=pk)
            folder.fav_avatar.add(avatar)
            return redirect('app:avatar', avatar_id=avatar_id)
        if 'add_want' in post:
            print('want!')
            pk = post['add_want']
            print(pk)
            folder = Folder.objects.get(pk=pk)
            folder.want_avatar.add(avatar)
            return redirect('app:avatar', avatar_id=avatar_id)
    return render(request, 'avatar.html', params)


def avatars(request, page=1, word='', free_only=False, sort_hot=False):
    params = {}
    user = request.user
    if user.is_authenticated:
        social = SocialAccount.objects.get(user=user)
        params['social'] = social
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
            if "-" in w:  # "-"が含まれる単語を検出
                exclude_words = w.split('-')[1:]  # 単語を"-"で分割し、除外する単語を取得
                exclude_query = Q()
                for e_word in exclude_words:
                    exclude_query = exclude_query | Q(avatar_name__contains=e_word)
                avatars = avatars.exclude(exclude_query)  # 除外条件を適用
            else:
                or_words = w.split('||')
                or_query = Q()
                for o in or_words:
                    print(o)
                    or_query = or_query | Q(avatar_name__contains=o)
                avatars = avatars.filter(or_query)
    params['total'] = avatars.count()
    if sort_hot:
        if sort_hot == 'off':
            redirect_url = reverse('app:avatars')
            redirect_url += '?word=' + word
            if free_only:
                redirect_url += '&free_only=on'
            return redirect(redirect_url)
        avatars = avatars.annotate(num_items=Count('items'))
        avatars = avatars.order_by(
            '-item_hot', '-num_items', 'price')[start:end]
        initial['sort_hot'] = sort_hot
    else:
        avatars = avatars.annotate(num_items=Count('items'))
        avatars = avatars.order_by('-num_items', 'price')[start:end]
    for avatar in avatars:
        if Customer.objects.filter(highlight=avatar.creator).exists():
            setattr(avatar, 'isHighlight', True)
    if user.is_authenticated:
        folders = Folder.objects.filter(editor=user.customer).order_by('-pk')
        folder_fav_avatars = dict(
            [(folder, folder.fav_avatar.all()) for folder in folders])
        folder_want_avatars = dict(
            [(folder, folder.want_avatar.all()) for folder in folders])
        for avatar in avatars:
            setattr(avatar, 'folders_owned', set(
                filter(lambda folder: avatar in folder_fav_avatars[folder], folders)))
            setattr(avatar, 'folders_wanted', set(
                filter(lambda folder: avatar in folder_want_avatars[folder], folders)))
        params['folders'] = folders
    params['avatars'] = avatars
    params['page'] = page
    params['free_only'] = free_only
    params['word'] = word
    form = Filter(initial=initial)
    params['form'] = form
    params['sort_hot'] = sort_hot
    return render(request, 'avatars.html', params)


def item(request, item_id=''):
    params = {}
    user = request.user
    item = Item.objects.get(item_id=item_id)
    params['item'] = item
    if user.is_authenticated:
        social = SocialAccount.objects.get(user=user)
        params['social'] = social
        folders = Folder.objects.filter(
            editor=request.user.customer).order_by('-pk')
        some_added = False
        some_added_want = False
        for folder in folders:
            notadd = item not in folder.fav_item.all()
            setattr(folder, 'notadd', notadd)
            if not notadd:
                some_added = True
            notadd_want = item not in folder.want_item.all()
            setattr(folder, 'notadd_want', notadd_want)
            if not notadd_want:
                some_added_want = True
        params['folders'] = folders
        params['folders_some_added'] = some_added
        params['folders_some_added_want'] = some_added_want
    avatars = item.avatar.all().order_by('price')
    for avatar in avatars:
        if Customer.objects.filter(highlight=avatar.creator).exists():
            print("hit")
            setattr(avatar, 'isHighlight', True)
    params['avatars'] = avatars
    if request.method == "POST":
        post = request.POST
        print(post)
        if 'add' in post:
            pk = post['add']
            folder = Folder.objects.get(pk=pk)
            folder.fav_item.add(item)
            return redirect('app:item', item_id=item_id)
        if 'add_want' in post:
            print('want')
            pk = post['add_want']
            folder = Folder.objects.get(pk=pk)
            folder.want_item.add(item)
            return redirect('app:item', item_id=item_id)
    return render(request, 'item.html', params)


def items(request, page=1, word='', free_only=False, sort_latest=False):
    params = {}
    user = request.user
    if user.is_authenticated:
        social = SocialAccount.objects.get(user=user)
        params['social'] = social
    if 'page' in request.GET:
        page = int(request.GET['page'])
    if 'word' in request.GET:
        word = request.GET['word']
    if 'free_only' in request.GET:
        free_only = request.GET['free_only']
    if 'sort_latest' in request.GET:
        sort_latest = request.GET['sort_latest']
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
            if "-" in w:  # "-"が含まれる単語を検出
                exclude_words = w.split('-')[1:]  # 単語を"-"で分割し、除外する単語を取得
                exclude_query = Q()
                for e_word in exclude_words:
                    exclude_query = exclude_query | Q(item_name__contains=e_word)
                items = items.exclude(exclude_query)  # 除外条件を適用
            else:
                or_words = w.split('||')
                or_query = Q()
                for o in or_words:
                    print(o)
                    or_query = or_query | Q(item_name__contains=o)
                items = items.filter(or_query)


    if sort_latest:
        if sort_latest == 'off':
            print('off!')
            redirect_url = reverse('app:items')
            redirect_url += '?word=' + word
            if free_only:
                redirect_url += '&free_only=on'
            return redirect(redirect_url)
        print('latest!')
        items = items.order_by('-item_id', '-num_avatars', 'price')
    else:
        items = items.order_by('-num_avatars', 'price')

    params['total'] = items.count()
    items = items[start:end]

    for item in items:
        if Customer.objects.filter(highlight=item.creator).exists():
            setattr(item, 'isHighlight', True)
    if user.is_authenticated:
        folders = Folder.objects.filter(editor=user.customer).order_by('-pk')
        folder_fav_items = dict(
            [(folder, folder.fav_item.all()) for folder in folders])
        folder_want_items = dict(
            [(folder, folder.want_item.all()) for folder in folders])
        for item in items:
            setattr(item, 'folders_owned', set(
                filter(lambda folder: item in folder_fav_items[folder], folders)))
            setattr(item, 'folders_wanted', set(
                filter(lambda folder: item in folder_want_items[folder], folders)))
        params['folders'] = folders
    params['items'] = items
    params['page'] = page
    params['free_only'] = free_only
    params['word'] = word
    form = Filter(initial=initial)
    params['form'] = form
    params['sort_latest'] = sort_latest
    return render(request, 'items.html', params)


def info(request):
    params = {}
    user = request.user
    if user.is_authenticated:
        social = SocialAccount.objects.get(user=user)
        params['social'] = social
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
    ago = datetime.datetime.now(pytz.timezone(
        'Asia/Tokyo')) - datetime.timedelta(days=7)
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


def userpage(request, tid=''):
    params = {}
    user = request.user
    if user.is_authenticated:
        social = SocialAccount.objects.get(user=user)
        params['social'] = social
    customer = Customer.objects.get(user__username=tid)
    params['customer'] = customer
    folders = Folder.objects.filter(editor=customer)
    params['folders'] = folders
    if request.method == 'POST':
        post = request.POST
        print(post)
        if 'VRCID' in post:
            VRCID = post['VRCID']
            customer.VRCID = VRCID
            customer.save()
        if 'message' in post:
            message = post['message']
            customer.message = message
            customer.save()
        if 'create_new' in post:
            for folder in Folder.objects.filter(editor=customer):
                criteria = 0
                criteria += folder.fav_avatar.all().count()
                criteria += folder.fav_item.all().count()
                criteria += folder.want_avatar.all().count()
                criteria += folder.want_item.all().count()
                if criteria == 0:
                    params['error'] = 'ERROR : 空のフォルダがある状態では新規フォルダは作成できません。'
                    return render(request, 'userpage.html', params)
            count = Folder.objects.filter(editor=customer).count()
            if count > 0 and not customer.isSupporter:
                params['error'] = 'ERROR : 複数のフォルダを作成するには、サポーターになる必要があります。'
                return render(request, 'userpage.html', params)
            Folder.objects.create(
                editor=user.customer,
                name=f'{user.customer}\'s favorite {count+1}',
            )
            return redirect('app:userpage', tid=tid)

    return render(request, 'userpage.html', params)


def folder(request, pk=0):
    params = {}
    user = request.user
    if user.is_authenticated:
        social = SocialAccount.objects.get(user=user)
        params['social'] = social
    folder = Folder.objects.get(pk=pk)
    if not folder.isOpen and user.customer != folder.editor:
        return redirect('app:index')
    params['folder'] = folder
    if request.method == 'POST':
        post = request.POST
        print(post)
        if 'avatar_remove' in post:
            remove_id = post['avatar_remove']
            avatar = Avatar.objects.get(avatar_id=remove_id)
            folder.fav_avatar.remove(avatar)
            return redirect('app:folder', pk=pk)
        if 'item_remove' in post:
            remove_id = post['item_remove']
            item = Item.objects.get(item_id=remove_id)
            folder.fav_item.remove(item)
            return redirect('app:folder', pk=pk)
        if 'avatar_remove_want' in post:
            remove_id = post['avatar_remove_want']
            avatar = Avatar.objects.get(avatar_id=remove_id)
            folder.want_avatar.remove(avatar)
            return redirect('app:folder', pk=pk)
        if 'item_remove_want' in post:
            remove_id = post['item_remove_want']
            item = Item.objects.get(item_id=remove_id)
            folder.want_item.remove(item)
            return redirect('app:folder', pk=pk)
        if 'delete' in post:
            delete = post['delete']
            if folder.name == delete:
                folder.delete()
            return redirect('app:userpage', tid=request.user.username)
        if 'name' in post:
            name = post['name']
            folder.name = name
            folder.save()
            name = post['name']
            folder.name = name
            folder.save()
            description = post['description']
            folder.description = description
            folder.isOpen = 'public' in post
            folder.isNSFW = 'NSFW' in post
            folder.save()
            return redirect('app:folder', pk=pk)
        if 'swap' in post:
            pre_fav_avatars = []
            pre_fav_items = []
            pre_want_avatars = []
            pre_want_items = []
            for avatar in folder.fav_avatar.all():
                pre_fav_avatars.append(avatar.avatar_id)
                folder.fav_avatar.remove(avatar)
            for item in folder.fav_item.all():
                pre_fav_items.append(item.item_id)
                folder.fav_item.remove(item)
            for avatar in folder.want_avatar.all():
                pre_want_avatars.append(avatar.avatar_id)
                folder.want_avatar.remove(avatar)
            for item in folder.want_item.all():
                pre_want_items.append(item.item_id)
                folder.want_item.remove(item)
            print(pre_fav_avatars)
            print(pre_fav_items)
            print(pre_want_avatars)
            print(pre_want_items)
            for avatar_id in pre_fav_avatars:
                avatar = Avatar.objects.get(avatar_id=avatar_id)
                folder.want_avatar.add(avatar)
            for item_id in pre_fav_items:
                item = Item.objects.get(item_id=item_id)
                folder.want_item.add(item)
            for avatar_id in pre_want_avatars:
                avatar = Avatar.objects.get(avatar_id=avatar_id)
                folder.fav_avatar.add(avatar)
            for item_id in pre_want_items:
                item = Item.objects.get(item_id=item_id)
                folder.fav_item.add(item)
            return redirect('app:folder', pk=pk)

    return render(request, 'folder.html', params)


@login_required
def recommend(request):
    params = {}
    user = request.user
    if user.is_authenticated:
        social = SocialAccount.objects.get(user=user)
        params['social'] = social
    params['avatars'] = AvatarQueue.objects.all()
    params['items'] = ItemQueue.objects.all()
    params['relations'] = RelationQueue.objects.all()
    if request.method == "POST":
        post = request.POST
        print(post)
        if 'avatar_id' in post:
            avatar_id = post['avatar_id'].split('/')[-1]
            if Avatar.objects.filter(avatar_id=avatar_id).exists():
                params['error'] = '! ERROR : このアバターは既に登録されています。'
                return render(request, 'recommend.html', params)
            if AvatarQueue.objects.filter(avatar_id=avatar_id).exists():
                params['error'] = '! ERROR : このアバターは既に推薦キューに入っています。'
                return render(request, 'recommend.html', params)
            import requests
            import re
            url = f'https://booth.pm/ja/items/{avatar_id}'
            text = requests.get(url).text
            print(text)
            pat = r'<title>(.*?) - BOOTH</title>'
            res = re.findall(pat, text)
            if len(res) == 0:
                params['error'] = 'URL の解析に失敗しました。'
                return render(request, 'recommend.html', params)
            avatar_name = name_validation(res[0])
            pat = r'"description":"(.*?)"'
            res = re.findall(pat, text)
            print(res)
            if len(res) == 0:
                params['error'] = 'URL の解析に失敗しました。'
                return render(request, 'recommend.html', params)
            describe = res[0][:200]
            print(describe)
            AvatarQueue.objects.create(
                avatar_id=avatar_id,
                avatar_name=avatar_name,
                describe=describe,
            )
            params['success'] = f'{avatar_name} をキューに追加しました。'
            return render(request, 'recommend.html', params)
        if 'item_id' in post:
            item_id = post['item_id'].split('/')[-1]
            if Item.objects.filter(item_id=item_id).exists():
                params['error'] = '! ERROR : このアイテムは既に登録されています。'
                return render(request, 'recommend.html', params)
            if ItemQueue.objects.filter(item_id=item_id).exists():
                params['error'] = '! ERROR : このアイテムは既に推薦キューに入っています。'
                return render(request, 'recommend.html', params)
            import requests
            import re
            url = f'https://booth.pm/ja/items/{item_id}'
            text = requests.get(url).text
            print(text)
            pat = r'<title>(.*?) - BOOTH</title>'
            res = re.findall(pat, text)
            if len(res) == 0:
                params['error'] = 'URL の解析に失敗しました。'
                return render(request, 'recommend.html', params)
            item_name = name_validation(res[0])
            pat = r'"description":"(.*?)"'
            res = re.findall(pat, text)
            print(res)
            if len(res) == 0:
                params['error'] = 'URL の解析に失敗しました。'
                return render(request, 'recommend.html', params)
            describe = res[0][:200]
            print(describe)
            ItemQueue.objects.create(
                item_id=item_id,
                item_name=item_name,
                describe=describe,
            )
            params['success'] = f'{item_name} をキューに追加しました。'
            return render(request, 'recommend.html', params)
        if 'approve' in post:
            avatar_id = post['approve']
            import sys
            sys.path.append('../')
            from manual_add_avatar import add_avatar
            add_avatar(avatar_id)
            AvatarQueue.objects.get(avatar_id=avatar_id).delete()
            return redirect('app:recommend')
        if 'decline' in post:
            avatar_id = post['decline']
            AvatarQueue.objects.get(avatar_id=avatar_id).delete()
            return redirect('app:recommend')
        if 'approve_item' in post:
            item_id = post['approve_item']
            import sys
            sys.path.append('../')
            from manual_add_item import add_item
            add_item(item_id)
            ItemQueue.objects.get(item_id=item_id).delete()
            return redirect('app:recommend')
        if 'decline_item' in post:
            item_id = post['decline_item']
            ItemQueue.objects.get(item_id=item_id).delete()
            return redirect('app:recommend')
        if 'relation_avatar' in post and 'relation_item' in post:
            relation_avatar = post['relation_avatar']
            relation_item = post['relation_item']
            if relation_avatar == '':
                params['error'] = 'AvatarURL の解析に失敗しました。'
                return render(request, 'recommend.html', params)
            if relation_item == '':
                params['error'] = 'ItemURL の解析に失敗しました。'
                return render(request, 'recommend.html', params)
            avatar_id = relation_avatar.split('/')[-1]
            item_id = relation_item.split('/')[-1]
            if not Avatar.objects.filter(avatar_id=avatar_id).exists():
                params['error'] = 'このアバターはシステムに登録されていません。先に登録お願いします。'
                return render(request, 'recommend.html', params)
            if not Item.objects.filter(item_id=item_id).exists():
                params['error'] = 'このアイテムはシステムに登録されていません。先に登録お願いします。'
                return render(request, 'recommend.html', params)
            avatar = Avatar.objects.get(avatar_id=avatar_id)
            item = Item.objects.get(item_id=item_id)
            print(avatar)
            print(item)
            if item in avatar.items.all():
                params['error'] = 'すでにアバターとアイテムは関連付けられています。'
                return render(request, 'recommend.html', params)
            if RelationQueue.objects.filter(avatar=avatar, item=item).exists():
                params['error'] = 'すでに同じ内容の推薦があります'
                return render(request, 'recommend.html', params)
            relation = RelationQueue.objects.create(
                avatar=avatar,
                item=item,
            )
            print(relation)
            params['success'] = f'{relation} をキューに追加しました。'
            return render(request, 'recommend.html', params)
        if 'approve_relation' in post:
            pk = post['approve_relation']
            print(pk)
            relation = RelationQueue.objects.get(pk=pk)
            avatar = relation.avatar
            item = relation.item
            avatar.items.add(item)
            relation.delete()
        if 'decline_relation' in post:
            pk = post['decline_relation']
            RelationQueue.objects.get(pk=pk).delete()

    return render(request, 'recommend.html', params)


def folders(request):
    params = {}
    user = request.user
    if user.is_authenticated:
        social = SocialAccount.objects.get(user=user)
        params['social'] = social
    folders = Folder.objects.filter(isOpen=True).annotate(num=Count(
        'fav_avatar') + Count('fav_item') + Count('want_avatar') + Count('want_item'))
    folders = folders.exclude(num=0).order_by('?')[:7]
    params['folders'] = folders
    return render(request, 'folders.html', params)


def all_folders(request):

    from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

    params = {}
    user = request.user
    if user.is_authenticated:
        social = SocialAccount.objects.get(user=user)
        params['social'] = social
    customers = Customer.objects.annotate(open_folder_count=Count('folder', filter=Q(folder__isOpen=True)))
    customers = customers.filter(open_folder_count__gte=1)
    customers = customers.order_by('-pk')

    # Pagination
    page = request.GET.get('page', 1)  # Get the 'page' query parameter, default to 1 if not found
    paginator = Paginator(customers, 9)  # Show 9 customers per page


    try:
        customers_page = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        customers_page = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        print('exceed!')
        page = paginator.num_pages
        customers_page = paginator.page(paginator.num_pages)

    params['customers'] = customers_page
    params['page'] = page
    return render(request, 'all_folders.html', params)

@login_required
def debug_folders(request):
    params = {}
    user = request.user
    # admin only
    if not user.is_staff:
        return redirect('app:index')
    if user.is_authenticated:
        social = SocialAccount.objects.get(user=user)
        params['social'] = social
    folders = Folder.objects.all()
    params['folders'] = folders
    return render(request, 'folders.html', params)


def please(request):
    params = {}
    user = request.user
    if user.is_authenticated:
        social = SocialAccount.objects.get(user=user)
        params['social'] = social
    return render(request, 'please.html', params)


def api_avatar(request):
    avatars = Avatar.objects.all()
    res = []
    for avatar in avatars:
        row = {}
        row['name'] = avatar.avatar_name
        row['price'] = avatar.price
        row['num_items'] = avatar.items.count()
        res.append(row)
    import json
    res = json.dumps(res, ensure_ascii=False, indent=4)
    return HttpResponse(res)


def api_item(request):
    items = Item.objects.all()
    res = []
    for item in items:
        row = {}
        row['name'] = item.item_name
        row['price'] = item.price
        row['num_avatars'] = item.avatar.count()
        res.append(row)
    import json
    res = json.dumps(res, ensure_ascii=False, indent=4)
    return HttpResponse(res)

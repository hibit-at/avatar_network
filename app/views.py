from django.shortcuts import redirect, render
from django.db.models import Q, Count
from django.urls import reverse
from allauth.socialaccount.models import SocialAccount
from django.contrib.auth.decorators import login_required

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


def index(request):
    params = {}
    user = request.user
    if user.is_authenticated:
        social = SocialAccount.objects.get(user=user)
        params['social'] = social
        # activate
        if not Customer.objects.filter(user=user).exists():
            customer = Customer.objects.create(
                user=user,
            )
            Folder.objects.create(
                editor=customer,
                name=f'{str(user)}\'s favorite'
            )
            print('customer instance created')
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
    params = {}
    user = request.user
    if user.is_authenticated:
        social = SocialAccount.objects.get(user=user)
        params['social'] = social
    creators = Creator.objects.all()
    avatar_query = Avatar.objects.annotate(num_items=Count('items'))
    avatar_query = avatar_query.order_by('price', '-num_items')
    item_query = Item.objects.annotate(num_avatars=Count('avatar'))
    item_query = item_query.order_by('price', '-num_avatars')
    creators = creators.prefetch_related(models.Prefetch(
        'avatars', queryset=avatar_query))
    creators = creators.prefetch_related(models.Prefetch(
        'items', queryset=item_query))
    creator = creators.get(creator_id=creator_id)
    params = {'creator': creator}
    return render(request, 'creator.html', params)


def creators(request, page=1, word='', free_only=False):
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
    # params = {'creators': creators, 'page': page}
    params['creators'] = creators
    params['page'] = page
    params['form'] = form
    params['word'] = word
    params['free_only'] = free_only
    params['total'] = total
    return render(request, 'creators.html', params)


def avatar(request, avatar_id=1, page=1):
    params = {}
    user = request.user
    avatar = Avatar.objects.get(avatar_id=avatar_id)
    if user.is_authenticated:
        social = SocialAccount.objects.get(user=user)
        params['social'] = social
        folders = Folder.objects.filter(editor=request.user.customer)
        for folder in folders:
            setattr(folder, 'notadd', avatar not in folder.fav_avatar.all())
        params['folders'] = folders
    if 'page' in request.GET:
        page = int(request.GET['page'])
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
    normal_items = normal_items.order_by('num_avatars', 'price')[start:end]
    params['page'] = page
    params['avatar'] = avatar
    params['total'] = total
    params['normal_items'] = normal_items
    params['genuine_items'] = genuine_items
    if request.method == "POST":
        post = request.POST
        print(post)
        if 'add' in post:
            pk = post['add']
            folder = Folder.objects.get(pk=pk)
            folder.fav_avatar.add(avatar)
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
            avatars = avatars.filter(avatar_name__contains=w)
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
        folders = Folder.objects.filter(editor=request.user.customer)
        for folder in folders:
            setattr(folder, 'notadd', item not in folder.fav_item.all())
        params['folders'] = folders
    if request.method == "POST":
        post = request.POST
        print(post)
        if 'add' in post:
            pk = post['add']
            folder = Folder.objects.get(pk=pk)
            folder.fav_item.add(item)
            return redirect('app:item', item_id=item_id)
    return render(request, 'item.html', params)


def items(request, page=1, word='', free_only=False):
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
                if folder.fav_avatar.all().count() + folder.fav_item.all().count() == 0:
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
    if user.customer != folder.editor:
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
            folder.save()
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

    return render(request, 'recommend.html', params)


def folders(request):
    params = {}
    user = request.user
    if user.is_authenticated:
        social = SocialAccount.objects.get(user=user)
        params['social'] = social
    folders = Folder.objects.filter(isOpen=True)
    params['folders'] = folders
    return render(request, 'folders.html', params)


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

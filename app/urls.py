from django.urls import path, include
from . import views
from django.views.generic import TemplateView

app_name = 'app'

urlpatterns = [
    path('', views.index, name='index'),
    path('', include('django.contrib.auth.urls')),
    path('avatar/<int:avatar_id>', views.avatar, name='avatar'),
    path('avatars/', views.avatars, name='avatars'),
    path('creator/<slug:creator_id>', views.creator, name='creator'),
    path('creators/', views.creators, name='creators'),
    path('item/<int:item_id>', views.item, name='item'),
    path('items/', views.items, name='items'),
    path('info/', views.info, name='info'),
    path('debug/', views.debug, name='debug'),
    path('userpage/<int:pk>', views.userpage, name='userpage'),
    path('folder/<int:pk>', views.folder, name='folder'),
    path('recommend/', views.recommend, name='recommend'),
    path('folders/', views.folders, name='folders'),
    path('all_folders/',views.all_folders,name='all_folders'),
    path('debug_folders/', views.debug_folders, name='debug_folders'),
    # path('please/', views.please, name='please'),
    path('api/avatar/', views.api_avatar, name='api_avatar'),
    path('api/item/', views.api_item, name='api_item'),
]

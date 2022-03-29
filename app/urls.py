from django.urls import path, include
from . import views

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
    # path('',views.suspend, name='suspend'),
    path('debug/', views.debug, name='debug'),
    path('userpage/<slug:tid>', views.userpage, name='userpage'),
    path('folder/<int:pk>', views.folder, name='folder'),
    path('recommend/',views.recommend, name='recommend'),
]

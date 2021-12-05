from django.urls import path
from . import views

app_name = 'app'

urlpatterns = [
    path('', views.index, name='index'),
    path('avatar/<int:avatar_id>', views.avatar, name='avatar'),
    path('avatars', views.avatars, name='avatars'),
    path('creator/<slug:creator_id>', views.creator, name='creator'),
    path('creators', views.creators, name='creators'),
    path('item/<int:item_id>', views.item, name='item'),
    path('items', views.items, name='items'),
]

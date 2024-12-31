from django.urls import path, include
from . import views
urlpatterns = [
    path('', views.index, name="index"),
    path('create-room/', views.create_room, name='create_room'),
    path('room/<str:room_name>/', views.room_view, name='room'),
    path('board', views.show_board, name='board'),

]
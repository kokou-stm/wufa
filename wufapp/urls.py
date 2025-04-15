from django.urls import path
from .views import *
from django.conf.urls.static import static

urlpatterns = [
    path('chat/', home, name='home'),
    path('', index, name='index'),
     path('login/', connection, name='login'),
    path('register/', register, name='register'),
    path('logout/', deconnexion, name='logout'),
     path('forgotpassword/', forgotpassword, name='forgotpassword'),
    path('updatepassword/<str:token>/<str:uid>/', updatepassword, name='updatepassword'),  
        path('code/', code, name='code'),
        path('edit_profile/', edit_profile, name='edit_profile'),
         path('generate_token/<str:channel_name>/', generate_agora_token, name='generate_agora_token'),

 path('call/<str:channel_name>/', call_room, name='call_room'),
    path('api/token/', generate_token, name='generate_token'),
    path('create-call/', create_call, name='create_call'),
     path("online_users/", online_users, name="online_users"),
     path('get_chat_users/', get_chat_users, name='get_chat_users'),
       path('create_chat/', create_chat, name='create_chat'),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

from django.conf.urls import url
from django.urls import re_path

from . import consumers


websocket_urlpatterns = [
    url(r'ws/chat/7/$', consumers.LikeConsumer),
    re_path(r'ws/posts/like/$', consumers.LikeConsumer),
    re_path(r'ws/bot/(?P<user_id>\w+)/$', consumers.BotConsumer),
]

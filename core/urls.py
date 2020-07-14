from django.urls import path
from rest_framework_simplejwt import views as jwt_views

from core.views import (
    CreatePostView,
    ListPostView,
    LikesAnalyticsView,
    UserActivityView,
    TokenObtainPairView, ChatView, BotFileUploadView, RegisterView, EmailActivationView,
)

app_name = 'core'

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('email/activation/<str:uidb64>/<str:token>/',
         EmailActivationView.as_view(), name='email_activation'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    path('posts/', ListPostView.as_view(), name='list_posts'),
    path('posts/create/', CreatePostView.as_view(), name='create_post'),
    path('likes/analytics/', LikesAnalyticsView.as_view(), name='likes_analytics'),
    path('user/activity/', UserActivityView.as_view(), name='user_activity'),
    path('bot/<str:filename>/', BotFileUploadView.as_view(), name='bot_file_upload'),
    path('chat/', ChatView.as_view(), name='chat'),
]

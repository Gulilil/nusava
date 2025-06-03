from django.urls import path, include 
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import (
    login_bot, get_posts, proxy_image,
    like_post, follow_user, comment_post, post_photo, share_post,
    bot_configuration, action_logs
)

urlpatterns = [
    path('login/', login_bot),
    path('posts/', get_posts),
    path('proxy-image/', proxy_image),

    path('like/', like_post),
    path('follow/', follow_user),
    path('comment/', comment_post),
    path('post/', post_photo),
    path('share/', share_post),

    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('config/', bot_configuration, name='bot_configuration'),
    path('logs/', action_logs, name='action_logs'),
]

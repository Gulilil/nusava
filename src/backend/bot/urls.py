from django.urls import path 
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import (
    login_bot, get_posts, proxy_image, register_user,
    like_post, follow_user, comment_post, post_photo,
    bot_configuration, action_logs,
    user_persona,
    automation_status, stop_dm_automation, start_dm_automation, admin_automation_overview,
    get_instagram_statistics
)

urlpatterns = [
    # Setup
    path('login/', login_bot),
    path('register/', register_user),
    path('posts/', get_posts),
    path('proxy-image/', proxy_image),
    # Action
    path('like/', like_post),
    path('follow/', follow_user),
    path('comment/', comment_post),
    path('post/', post_photo),
    # Token
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # Logging and Config
    path('config/', bot_configuration, name='bot_configuration'),
    path('logs/', action_logs, name='action_logs'),
    # Automation
    path('automation/status/', automation_status, name='automation_status'),
    path('automation/stop/', stop_dm_automation, name='stop_dm_automation'),
    path('automation/start/', start_dm_automation, name='start_dm_automation'),
    path('automation/admin/', admin_automation_overview, name='admin_automation_overview'),

    path('persona/', user_persona, name='user_persona'),
    path('stats/', get_instagram_statistics, name='get_instagram_statistics'),
]

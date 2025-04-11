from django.urls import path
from .views import login_bot, get_posts, proxy_image

urlpatterns = [
    path('login/', login_bot),
    path('posts/', get_posts),
    path('proxy-image/', proxy_image),
]

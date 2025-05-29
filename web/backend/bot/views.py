from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.http import HttpResponse
import requests

from .models import User
from .bot import InstagramBot
from instagrapi import Client
from rest_framework_simplejwt.tokens import RefreshToken
import logging
from instagrapi.exceptions import LoginRequired

logger = logging.getLogger(__name__)
user_bots = {}

def proxy_image(request):
    url = request.GET.get('url')
    if not url:
        return HttpResponse("No URL provided", status=400)

    try:
        resp = requests.get(url, stream=True)
        content_type = resp.headers.get('Content-Type', 'image/jpeg')
        response = HttpResponse(resp.content, content_type=content_type)
        response["Access-Control-Allow-Origin"] = "*"
        return response
    except Exception as e:
        return HttpResponse(str(e), status=500)

@api_view(['POST'])
@permission_classes([AllowAny])
def login_bot(request):
    username = request.data.get('username')
    password = request.data.get('password')
    if not username or not password:
        return Response({"status": "error", "message": "Username and password required"}, status=400)

    try:
        # Try existing user session login
        try:
            user = User.objects.get(username=username)
            if not user.check_password(password):
                return Response({"status": "error", "message": "Incorrect password"}, status=400)
            
            # Load existing session
            bot_client = Client()
            bot_client.load_settings(user.session_info)
            
            try:
                # Test the session by getting user info
                bot_client.account_info()
                
                # Session is valid, create bot and return success
                bot = InstagramBot(user_obj=user, password=password, session_settings=user.session_info)
                user_bots[user.id] = bot
                refresh = RefreshToken.for_user(user)
                return Response({
                    "status": "success",
                    "message": "Logged in with saved session",
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                })
                
            except LoginRequired:
                # Session is flagged, delete it and create new one
                logger.warning(f"Session flagged for user {username}, creating new session")
                
                # Try fresh login
                fresh_client = Client()
                is_success = fresh_client.login(username, password)
                
                if not is_success:
                    # Try relogin if first attempt fails
                    is_success = fresh_client.login(username, password, relogin=True)
                    if not is_success:
                        return Response({"status": "error", "message": "Instagram login failed after relogin attempt"}, status=400)
                
                # Update user with new session
                new_session = fresh_client.get_settings()
                user.session_info = new_session
                user.save()
                
                bot = InstagramBot(user_obj=user, password=password, session_settings=new_session)
                user_bots[user.id] = bot
                refresh = RefreshToken.for_user(user)
                return Response({
                    "status": "success",
                    "message": "Logged in with new session (old session was flagged)",
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                })
                
        except User.DoesNotExist:
            pass  # No existing user, try Instagram login fresh

        # Fresh Instagram login for new user
        bot_client = Client()
        is_success = bot_client.login(username, password)
        
        if not is_success:
            try:
                # Try relogin if first attempt fails
                is_success = bot_client.login(username, password, relogin=True)
                if not is_success:
                    return Response({"status": "error", "message": "Instagram login failed - incorrect credentials"}, status=400)
            except LoginRequired:
                return Response({"status": "error", "message": "Instagram login failed - account may be restricted"}, status=400)
        
        # Create new user with session
        session = bot_client.get_settings()
        user = User.objects.create(username=username, session_info=session)
        user.set_password(password)
        user.save()

        refresh = RefreshToken.for_user(user)
        bot = InstagramBot(user_obj=user, password=password, session_settings=session)
        user_bots[user.id] = bot
        return Response({
            "status": "success",
            "message": "New user created and logged in",
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        })

    except Exception as e:
        logger.error(f"Instagram login error: {str(e)}")
        return Response({"status": "error", "message": f"Instagram login error: {str(e)}"}, status=400)
    
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_posts(request):
    user = request.user
    bot = user_bots.get(user.id)
    if not bot:
        return Response({"error": "Bot not initialized for this user"}, status=400)
    try:
        posts = bot.get_recent_posts()
        return Response(posts)
    except Exception as e:
        logger.error(f"Get posts error: {e}")
        return Response({"error": "Failed to fetch posts"}, status=500)

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def like_post(request):
    user = request.user
    media_url = request.data.get('media_url')
    if not media_url:
        return Response({"error": "media_url is required"}, status=400)
    bot = user_bots.get(user.id)
    if not bot:
        return Response({'error': 'Bot not initialized for this user'}, status=400)
    try:
        bot.like_post(media_url)
        return Response({'status': 'success', 'message': 'Post liked'})
    except Exception as e:
        logger.error(f"Like post error: {e}")
        return Response({'error': 'Failed to like post'}, status=500)

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def follow_user(request):
    user = request.user
    target_username = request.data.get('target_username')
    if not target_username:
        return Response({"error": "target_username is required"}, status=400)
    bot = user_bots.get(user.id)
    if not bot:
        return Response({'error': 'Bot not initialized for this user'}, status=400)
    try:
        bot.follow_user(target_username)
        return Response({'status': 'success', 'message': 'User followed'})
    except Exception as e:
        logger.error(f"Follow user error: {e}")
        return Response({'error': 'Failed to follow user'}, status=500)

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def comment_post(request):
    user = request.user
    media_url = request.data.get('media_url')
    comment = request.data.get('comment')
    if not media_url or not comment:
        return Response({"error": "media_url and comment are required"}, status=400)
    bot = user_bots.get(user.id)
    if not bot:
        return Response({'error': 'Bot not initialized for this user'}, status=400)
    try:
        bot.comment_on_post(media_url, comment)
        return Response({'status': 'success', 'message': 'Comment posted'})
    except Exception as e:
        logger.error(f"Comment post error: {e}")
        return Response({'error': 'Failed to post comment'}, status=500)

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def post_photo(request):
    user = request.user
    image_path = request.data.get('image_path')
    caption = request.data.get('caption')
    if not image_path or not caption:
        return Response({"error": "image_path and caption are required"}, status=400)
    bot = user_bots.get(user.id)
    if not bot:
        return Response({'error': 'Bot not initialized for this user'}, status=400)
    try:
        bot.post_photo(image_path, caption)
        return Response({'status': 'success', 'message': 'Photo posted'})
    except Exception as e:
        logger.error(f"Post photo error: {e}")
        return Response({'error': 'Failed to post photo'}, status=500)

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def share_post(request):
    user = request.user
    media_url = request.data.get('media_url')
    target_usernames = request.data.get('target_usernames', [])
    if not media_url or not target_usernames:
        return Response({"error": "media_url and target_usernames are required"}, status=400)
    bot = user_bots.get(user.id)
    if not bot:
        return Response({'error': 'Bot not initialized for this user'}, status=400)
    try:
        bot.share_post_dm(media_url, target_usernames)
        return Response({'status': 'success', 'message': f'Post shared to {target_usernames}'})
    except Exception as e:
        logger.error(f"Share post error: {e}")
        return Response({'error': 'Failed to share post'}, status=500)
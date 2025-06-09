import json
import os
import tempfile
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

from .serializers import ConfigurationSerializer, ActionLogSerializer
from .models import Configuration, ActionLog
from django.core.paginator import Paginator
from .automation import automation_service

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

            # TODO Transfer user.id to LLM api to get persona
            
            if not user.check_password(password):
                return Response({"status": "error", "message": "Incorrect password"}, status=400)
            
            # Load existing session
            bot_client = Client()
            if user.session_info:
                try:
                    # Extract sessionid from session_info
                    session_data = user.session_info
                    if isinstance(session_data, str):
                        session_data = json.loads(session_data)
                    
                    sessionid = None
                    if 'authorization_data' in session_data:
                        sessionid = session_data['authorization_data'].get('sessionid')
                    else:
                        sessionid = session_data.get('sessionid')
                        
                    if sessionid:
                        # Try to login using sessionid
                        success = bot_client.login_by_sessionid(sessionid)
                        if success:
                            # Session is valid, create bot and return success
                            bot = InstagramBot(user_obj=user, password=password, session_settings=user.session_info)
                            user_bots[user.id] = bot
                            refresh = RefreshToken.for_user(user)
                            automation_service.auto_start_for_user(
                                user, 
                                min_interval=300,
                                max_interval=3600  
                            )
                            return Response({
                                "status": "success",
                                "message": "Logged in with saved session",
                                "access": str(refresh.access_token),
                                "refresh": str(refresh),
                            })
                        else:
                            # Session invalid, will create new one below
                            logger.warning(f"Session invalid for user {username}, creating new session")
                    else:
                        logger.warning(f"No sessionid found for user {username}")
                        
                except (json.JSONDecodeError, KeyError, Exception) as e:
                    logger.warning(f"Error loading session for user {username}: {e}")
            
            try:
                # Test the session by getting user info
                bot_client.account_info()
                
                # Session is valid, create bot and return success
                bot = InstagramBot(user_obj=user, password=password, session_settings=user.session_info)
                user_bots[user.id] = bot
                refresh = RefreshToken.for_user(user)
                automation_service.auto_start_for_user(
                    user, 
                    min_interval=300,
                    max_interval=3600 
                )
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
                automation_service.auto_start_for_user(
                    user, 
                    min_interval=300,
                    max_interval=3600 
                )
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
        Configuration.objects.create(
            user=user,
            max_iteration=10,
            temperature=0.3,
            top_k=10,
            max_token=4096
        )
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
    
@api_view(['GET', 'POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def bot_configuration(request):
    """Get or update bot configuration"""
    user = request.user
    
    # Get or create configuration for user
    config, created = Configuration.objects.get_or_create(
        user=user,
        defaults={
            'max_iteration': 10,
            'temperature': 0.3,
            'top_k': 10,
            'max_token': 4096
        }
    )
    
    if request.method == 'GET':
        serializer = ConfigurationSerializer(config)
        return Response({
            'status': 'success',
            'data': serializer.data
        })
    
    elif request.method == 'POST':
        serializer = ConfigurationSerializer(config, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'status': 'success',
                'message': 'Configuration updated successfully',
                'data': serializer.data
            })
        else:
            return Response({
                'status': 'error',
                'message': 'Invalid data',
                'errors': serializer.errors
            }, status=400)
        

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def action_logs(request):
    """Get action logs for the authenticated user"""
    user = request.user
    
    # Get query parameters
    page = request.GET.get('page', 1)
    page_size = request.GET.get('page_size', 20)
    action_type = request.GET.get('action_type', '')
    status = request.GET.get('status', '')
    
    # Filter logs
    logs = ActionLog.objects.filter(user=user).order_by('-timestamp')
    
    if action_type:
        logs = logs.filter(action_type__icontains=action_type)
    if status:
        logs = logs.filter(status__icontains=status)
    
    # Paginate
    paginator = Paginator(logs, page_size)
    page_obj = paginator.get_page(page)
    
    serializer = ActionLogSerializer(page_obj, many=True)
    
    return Response({
        'status': 'success',
        'data': serializer.data,
        'pagination': {
            'current_page': page_obj.number,
            'total_pages': paginator.num_pages,
            'total_count': paginator.count,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous(),
        }
    })

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def automation_status(request):
    user = request.user
    status = automation_service.get_status_for_user(user.id)
    return Response({"status": "success", "data": status})

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def stop_dm_automation(request):
    user = request.user
    success, message = automation_service.stop_automation(user.id)
    return Response({"status": "success" if success else "error", "message": message})

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def admin_automation_overview(request):
    if not request.user.is_staff:
        return Response({"error": "Admin only"}, status=403)
    
    all_automations = automation_service.get_all_running_automations()
    return Response({"data": all_automations})
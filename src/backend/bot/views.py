import json
import os
import tempfile
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.http import HttpResponse
import requests
import environ

from .models import InstagramStatistics, User
from .bot import InstagramBot
from instagrapi import Client
from rest_framework_simplejwt.tokens import RefreshToken
import logging
from instagrapi.exceptions import LoginRequired

from .serializers import ConfigurationSerializer, ActionLogSerializer
from .models import Configuration, ActionLog
from django.core.paginator import Paginator
from .automation import automation_service

from dotenv import load_dotenv
load_dotenv()

logger = logging.getLogger(__name__)
env = environ.Env()
max_interval = env('MAX_INTERVAL', default=900, cast=int)
min_interval = env('MIN_INTERVAL', default=300, cast=int)
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
def register_user(request):
    """Register a new user with Instagram credentials"""
    username = request.data.get('username')
    password = request.data.get('password')
    
    if not username or not password:
        return Response({
            "status": "error", 
            "message": "Username and password required"
        }, status=400)

    try:
        # Check if user already exists
        if User.objects.filter(username=username).exists():
            return Response({
                "status": "error",
                "message": "User already exists"
            }, status=400)

        # Test Instagram login before creating user
        bot_client = Client()
        is_success = bot_client.login(username, password)
        
        if not is_success:
            try:
                # Try relogin if first attempt fails
                is_success = bot_client.login(username, password, relogin=True)
                if not is_success:
                    return Response({
                        "status": "error", 
                        "message": "Instagram login failed - incorrect credentials"
                    }, status=400)
            except LoginRequired:
                return Response({
                    "status": "error", 
                    "message": "Instagram login failed - account may be restricted"
                }, status=400)
        
        # Create new user with session
        session = bot_client.get_settings()
        user = User.objects.create(username=username, session_info=session)
        user.set_password(password)
        user.save()
        
        # Create default configuration
        Configuration.objects.create(
            user=user,
            max_iteration=10,
            temperature=0.3,
            top_k=10,
            max_token=4096
        )

        automation_service.auto_start_for_user(
                    user, 
                    min_interval=min_interval,
                    max_interval=max_interval 
                )
        
        # Transfer user_id for persona set
        llm_module_url = os.getenv("LLM_MODULE_URL")
        api_url = f"{llm_module_url}/user"
        data = {
            "user_id": user.id
            }
        response = requests.post(api_url, json=data)
        if (not response.status_code == 200 or not response.json()['response']):
            return Response({"status": "error", "message": "Cannot set user to llm module"}, status=400)
        refresh = RefreshToken.for_user(user)

        return Response({
            "status": "success",
            "message": "User registered successfully",
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        })

    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        return Response({
            "status": "error", 
            "message": f"Registration failed: {str(e)}"
        }, status=400)

@api_view(['POST'])
@permission_classes([AllowAny])
def login_bot(request):
    """Login existing user"""
    username = request.data.get('username')
    password = request.data.get('password')
    
    if not username or not password:
        return Response({
            "status": "error", 
            "message": "Username and password required"
        }, status=400)

    try:
        # Get existing user
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response({
                "status": "error", 
                "message": "User not found. Please register first."
            }, status=404)
            
        # Check password
        if not user.check_password(password):
            return Response({
                "status": "error", 
                "message": "Incorrect password"
            }, status=400)
        
        # Load existing session
        bot_client = Client()
        session_valid = False
        
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
                        session_valid = True
                    else:
                        logger.warning(f"Session invalid for user {username}")

            except LoginRequired:
                # Session is flagged, delete it and create new one
                logger.warning(f"Session flagged for user {username}, creating new session")
                
                # Try fresh login
                fresh_client = Client()
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
                    min_interval=min_interval,
                    max_interval=max_interval 
                )
                return Response({
                    "status": "success",
                    "message": "Logged in with new session (old session was flagged)",
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                })  
            except (json.JSONDecodeError, KeyError, LoginRequired, Exception) as e:
                logger.warning(f"Error loading session for user {username}: {e}")
        
        # If session is invalid, create new one
        if not session_valid:
            return Response({
                "status": "error", 
                "message": "Session expired or invalid. Please register again to refresh your Instagram session."
            }, status=401)
        
        # Create bot instance and tokens
        bot = InstagramBot(user_obj=user, password=password, session_settings=user.session_info)
        user_bots[user.id] = bot
        
        refresh = RefreshToken.for_user(user)
        
        # Start automation
        automation_service.auto_start_for_user(
            user, 
            min_interval=min_interval,
            max_interval=max_interval  
        )
        
        # Transfer user_id for persona set
        llm_module_url = os.getenv("LLM_MODULE_URL")
        api_url = f"{llm_module_url}/user"
        data = {
            "user_id": user.id
            }
        response = requests.post(api_url, json=data)
        if (not response.status_code == 200 or not response.json()['response']):
            return Response({"status": "error", "message": "Cannot set user to llm module"}, status=400)
        
        return Response({
            "status": "success",
            "message": "Login successful",
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        })

    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return Response({
            "status": "error", 
            "message": f"Login failed: {str(e)}"
        }, status=400)
    
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
@permission_classes([AllowAny])
def like_post(request):
    media_id = request.data.get('media_id')
    media_url = request.data.get('media_url')
    if not media_id and not media_url:
        return Response({"error": "media_id or media_url is required"}, status=400)
    user_id = request.data.get('user_id')
    if not user_id:
        user = request.user
        bot = user_bots.get(user.id)
    else:
        user = User.objects.filter(id=user_id).first()
        if not user:
            return Response({"error": "User not found"}, status=404)
        bot = InstagramBot(user_obj=user, password=user.password, session_settings=user.session_info)
    if not bot:
        return Response({'error': 'Bot not initialized for this user'}, status=400)
    try:
        bot.like_post(media_id, media_url)
        return Response({'status': 'success', 'message': 'Post liked'})
    except Exception as e:
        logger.error(f"Like post error: {e}")
        return Response({'error': 'Failed to like post'}, status=500)

@api_view(['POST'])
@permission_classes([AllowAny])
def follow_user(request):
    target_username = request.data.get('target_username')
    if not target_username:
        return Response({"error": "target_username is required"}, status=400)
    user_id = request.data.get('user_id')
    if not user_id:
        user = request.user
        bot = user_bots.get(user.id)
    else:
        user = User.objects.filter(id=user_id).first()
        if not user:
            return Response({"error": "User not found"}, status=404)
        bot = InstagramBot(user_obj=user, password=user.password, session_settings=user.session_info)
    if not bot:
        return Response({'error': 'Bot not initialized for this user'}, status=400)
    try:
        bot.follow_user(target_username)
        return Response({'status': 'success', 'message': 'User followed'})
    except Exception as e:
        logger.error(f"Follow user error: {e}")
        return Response({'error': 'Failed to follow user'}, status=500)

@api_view(['POST'])
@permission_classes([AllowAny])
def comment_post(request):
    media_id = request.data.get('media_id')
    media_url = request.data.get('media_url')
    comment = request.data.get('comment')
    if (not media_id and not media_url) or not comment:
        return Response({"error": "media_id/media_url and comment are required"}, status=400)
    user_id = request.data.get('user_id')
    if not user_id:
        user = request.user
        bot = user_bots.get(user.id)
    else:
        user = User.objects.filter(id=user_id).first()
        if not user:
            return Response({"error": "User not found"}, status=404)
        bot = InstagramBot(user_obj=user, password=user.password, session_settings=user.session_info)
    if not bot:
        return Response({'error': 'Bot not initialized for this user'}, status=400)
    try:
        bot.comment_on_post(comment, media_id, media_url)
        return Response({'status': 'success', 'message': 'Comment posted'})
    except Exception as e:
        logger.error(f"Comment post error: {e}")
        return Response({'error': 'Failed to post comment'}, status=500)

@api_view(['POST'])
@permission_classes([AllowAny])
def post_photo(request):
    image_path = request.data.get('image_path')
    caption = request.data.get('caption')
    if not image_path or not caption:
        return Response({"error": "image_path and caption are required"}, status=400)
    user_id = request.data.get('user_id')
    if not user_id:
        user = request.user
        bot = user_bots.get(user.id)
    else:
        user = User.objects.filter(id=user_id).first()
        if not user:
            return Response({"error": "User not found"}, status=404)
        bot = InstagramBot(user_obj=user, password=user.password, session_settings=user.session_info)
    if not bot:
        return Response({'error': 'Bot not initialized for this user'}, status=400)
    try:
        bot.post_photo(image_path, caption)
        return Response({'status': 'success', 'message': 'Photo posted'})
    except Exception as e:
        logger.error(f"Post photo error: {e}")
        return Response({'error': 'Failed to post photo'}, status=500)
    
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

            # Hit LLM API after save to notify
            # Try maximum tries 3 times
            max_attempt = 3
            attempt =1
            is_success = False
            while(attempt <= max_attempt and not is_success):
              llm_module_url = os.getenv("LLM_MODULE_URL")
              api_url = f"{llm_module_url}/config"
              response = requests.post(api_url)
              # Break if already success
              if (response.status_code == 200):
                is_success = True
              attempt +=1

            if (is_success):
              return Response({
                  'status': 'success',
                  'message': 'Configuration updated successfully',
                  'data': serializer.data
              })
            else:
              return Response({
                  'status': 'error',
                  'message': f'Failed to notify LLM after {max_attempt} tries',
                  'errors': serializer.errors
              }, status=400)

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

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def start_dm_automation(request):
    user = request.user
    min_interval = request.data.get('min_interval', 300)
    max_interval = request.data.get('max_interval', 900)
    
    success, message = automation_service.start_automation(user.id, min_interval, max_interval)
    
    return Response({
        "status": "success" if success else "error",
        "message": message
    })

@api_view(['GET', 'POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def user_persona(request):
    """Get or update the persona for the authenticated user"""
    user = request.user
    
    if request.method == 'GET':
        persona = getattr(user, 'persona', None)
        
        return Response({
            'status': 'success',
            'data': {
                'persona': persona
            }
        })
    
    elif request.method == 'POST':
        persona = request.data.get('persona')
        
        if persona is None:
            return Response({
                'status': 'error',
                'message': 'Persona field is required'
            }, status=400)
        
        # Update user persona
        user.persona = persona
        user.save()
        
        # Hit LLM API after save to notify
        # Try maximum tries 3 times
        max_attempt = 3
        attempt =1
        is_success = False
        while(attempt <= max_attempt and not is_success):
            llm_module_url = os.getenv("LLM_MODULE_URL")
            api_url = f"{llm_module_url}/persona"
            response = requests.post(api_url)
            # Break if already success
            if (response.status_code == 200):
                is_success = True
                attempt +=1
        return Response({
            'status': 'success',
            'message': 'Persona updated successfully',
            'data': {
                'persona': persona
            }
        })

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_instagram_statistics(request):
    """Get Instagram statistics for the authenticated user"""
    user = request.user
    
    try:
        stats = InstagramStatistics.objects.get(user=user)
        
        # Serialize the statistics data
        stats_data = {
            'followers_count': stats.followers_count,
            'following_count': stats.following_count,
            'posts_count': stats.posts_count,
            'all_likes_count': stats.all_likes_count,
            'all_comments_count': stats.all_comments_count,
            'profile_visits': stats.profile_visits,
            'profile_visits_delta': stats.profile_visits_delta,
            'website_visits': stats.website_visits,
            'website_visits_delta': stats.website_visits_delta,
            'impressions': stats.impressions,
            'impressions_delta': stats.impressions_delta,
            'reach': stats.reach,
            'reach_delta': stats.reach_delta,
            'new_followers': stats.new_followers,
            'new_likes': stats.new_likes,
            'new_comments': stats.new_comments,
            'engagement_rate': stats.engagement_rate,
            'created_at': stats.created_at,
            'updated_at': stats.updated_at,
        }
        
        return Response({
            'status': 'success',
            'data': stats_data
        })
        
    except InstagramStatistics.DoesNotExist:
        return Response({
            'status': 'error',
            'message': 'No statistics found for this user. Please run the update command first.'
        }, status=404)
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=500)
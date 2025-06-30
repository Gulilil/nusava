import os
import random
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.http import HttpResponse
import requests
import environ

from .models import InstagramStatistics, Posts, ScheduledPost, TourismObject, User
from .bot import InstagramBot
from instagrapi import Client
from rest_framework_simplejwt.tokens import RefreshToken
import logging
from instagrapi.exceptions import LoginRequired

from .serializers import ConfigurationSerializer, ActionLogSerializer
from .models import Configuration, ActionLog
from django.core.paginator import Paginator
from .automation import automation_service
from django.utils import timezone
from datetime import timedelta
from django.utils.dateparse import parse_datetime


from dotenv import load_dotenv
load_dotenv()

logger = logging.getLogger('views')
env = environ.Env()
max_interval = env('MAX_INTERVAL', default=900, cast=int)
min_interval = env('MIN_INTERVAL', default=300, cast=int)
user_bots: dict[str, InstagramBot] = {}

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
            }, status=400)        # Create new user first with empty session_info (as user requested)
        user = User.objects.create(username=username, session_info=None)
        user.set_password(password)
        user.save()
        
        client = Client()
        
        # Setup client configuration
        client.set_locale('en_SG')  # Singapore English locale
        client.set_country('SG')    # Singapore country code
        client.set_country_code(65) # Singapore country calling code
        client.set_timezone_offset(28800)  # UTC+8 (Singapore timezone)
        client.set_device({
            'manufacturer': random.choice(['samsung', 'apple', 'oppo', 'xiaomi']),
            'model': random.choice(['SM-G991B', 'iPhone13,2', 'CPH2145', 'M2007J20CG']),
            'android_version': random.choice([29, 30, 31]),
            'android_release': random.choice(['10.0', '11.0', '12.0'])
        })
        client.delay_range = [1, 3]
        
        proxy_url = env('PROXY_URL', default=None)
        client.set_proxy(proxy_url)

        try:
            # Test Instagram login - this will save session to DB if successful
            client.login(username, password)
            bot = InstagramBot(user_obj=user, password=password)
            bot.client = client
            user_bots[user.id] = bot
            logger.info(f"Instagram login successful for registration: {username}")
            
        except Exception as login_error:
            # Delete the user if Instagram login fails
            user.delete()
            logger.error(f"Instagram login failed during registration for {username}: {str(login_error)}")
            return Response({
                "status": "error", 
                "message": f"Instagram login failed: {str(login_error)}"
            }, status=400)
        
        # Create default configuration
        Configuration.objects.create(
            user=user,
            max_iteration=10,            
            temperature=0.3,
            top_k=10,
            max_token=4096
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

        automation_service.auto_start_for_user(
                    user, 
                    min_interval=min_interval,
                    max_interval=max_interval 
                )
        
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
        
        bot = user_bots.get(user.id)
        if not bot:
            try:
                # Only create new bot if not in memory
                bot = InstagramBot(user_obj=user, password=user.password)
                user_bots[user.id] = bot
            except Exception as e:
                logger.error(f"Failed to initialize bot for user {user.id}: {str(e)}")
                return Response({"error": f"Bot initialization failed: {str(e)}"}, status=500)
        
        refresh = RefreshToken.for_user(user)
        
        # Transfer user_id for persona set
        llm_module_url = os.getenv("LLM_MODULE_URL")
        api_url = f"{llm_module_url}/user"
        data = {
            "user_id": user.id
            }
        response = requests.post(api_url, json=data)
        
        # Start automation
        automation_service.auto_start_for_user(
            user, 
            min_interval=min_interval,
            max_interval=max_interval  
        )
        
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
    else:
        user = User.objects.filter(id=user_id).first()
        if not user:
            return Response({"error": "User not found"}, status=404)
    
    recent_actions = ActionLog.objects.filter(
        user=user,
        action_type='like',
        timestamp__gte=timezone.now() - timedelta(minutes=5)
    ).count()
    
    if recent_actions >= 3:  # Max 3 likes per 5 minutes
        return Response({
            "error": "Rate limit exceeded. Please wait before liking more posts."
        }, status=429)
    
    bot = user_bots.get(user.id)
    if not bot:
        try:
            # Only create new bot if not in memory
            bot = InstagramBot(user_obj=user, password=user.password)
            user_bots[user.id] = bot
        except Exception as e:
            logger.error(f"Failed to initialize bot for user {user.id}: {str(e)}")
            return Response({"error": f"Bot initialization failed: {str(e)}"}, status=500)
        
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
    else:
        user = User.objects.filter(id=user_id).first()
    
    recent_actions = ActionLog.objects.filter(
        user=user,
        action_type='follow',
        timestamp__gte=timezone.now() - timedelta(minutes=5)
    ).count()
    
    if recent_actions >= 4:  # Max 3 follow per 5 minutes
        return Response({
            "error": "Rate limit exceeded. Please wait before following"
        }, status=429)
    bot = user_bots.get(user.id)
    if not bot:
        try:
            # Only create new bot if not in memory
            bot = InstagramBot(user_obj=user, password=user.password)
            user_bots[user.id] = bot
        except Exception as e:
            logger.error(f"Failed to initialize bot for user {user.id}: {str(e)}")
            return Response({"error": f"Bot initialization failed: {str(e)}"}, status=500)
    
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
    else:
        user = User.objects.filter(id=user_id).first()

    recent_actions = ActionLog.objects.filter(
        user=user,
        action_type='comment',
        timestamp__gte=timezone.now() - timedelta(minutes=5)
    ).count()
    
    if recent_actions >= 3:  # Max 3 comment per 5 minutes
        return Response({
            "error": "Rate limit exceeded. Please wait before commenting more posts."
        }, status=429)
    
    bot = user_bots.get(user.id)
    if not bot:
        try:
            # Only create new bot if not in memory
            bot = InstagramBot(user_obj=user, password=user.password)
            user_bots[user.id] = bot
        except Exception as e:
            logger.error(f"Failed to initialize bot for user {user.id}: {str(e)}")
            return Response({"error": f"Bot initialization failed: {str(e)}"}, status=500)
    try:
        bot.comment_on_post(comment, media_id, media_url)
        return Response({'status': 'success', 'message': 'Comment posted'})
    except Exception as e:
        logger.error(f"Comment post error: {e}")
        return Response({'error': 'Failed to post comment'}, status=500)

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
@permission_classes([AllowAny])
def get_instagram_statistics(request):
    """Get Instagram statistics for the authenticated user"""
    user_id = request.data.get('user_id')
    if not user_id:
        user = request.user
    else:
        user = User.objects.filter(id=user_id).first()
    
    try:
        stats = InstagramStatistics.objects.filter(user=user).order_by('-created_at').first()
        
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

@api_view(['POST'])
@permission_classes([AllowAny])
def update_instagram_statistics(request):
    """Update Instagram statistics by fetching current data and comparing with existing"""
    user_id = request.data.get('user_id')
    if not user_id:
        user = request.user
    else:
        user = User.objects.filter(id=user_id).first()

    bot = user_bots.get(user.id)
    if not bot:
        try:
            # Only create new bot if not in memory
            bot = InstagramBot(user_obj=user, password=user.password)
            user_bots[user.id] = bot
        except Exception as e:
            logger.error(f"Failed to initialize bot for user {user.id}: {str(e)}")
            return Response({"error": f"Bot initialization failed: {str(e)}"}, status=500)
    
    try:
        # Get current statistics from Instagram
        current_stats = bot.get_account_statistics()
        # Check if statistics already exist for this user
        existing_stats = InstagramStatistics.objects.filter(user=user).order_by('-created_at').first()
        
        if existing_stats:
            # Compare and calculate differences
            new_followers = current_stats['followers_count'] - existing_stats.followers_count
            new_likes = current_stats['all_likes_count'] - existing_stats.all_likes_count
            new_comments = current_stats['all_comments_count'] - existing_stats.all_comments_count
            
            # Create new statistics entry
            new_stats = InstagramStatistics.objects.create(
                user=user,
                new_followers=new_followers,
                new_likes=new_likes,
                new_comments=new_comments,
                **current_stats
            )
            
            return Response({
                'status': 'success',
                'message': 'Statistics updated successfully',
                'data': {
                    'followers_count': new_stats.followers_count,
                    'following_count': new_stats.following_count,
                    'posts_count': new_stats.posts_count,
                    'all_likes_count': new_stats.all_likes_count,
                    'all_comments_count': new_stats.all_comments_count,
                    'new_followers': new_followers,
                    'new_likes': new_likes,
                    'new_comments': new_comments,
                    'profile_visits': new_stats.profile_visits,
                    'impressions': new_stats.impressions,
                    'reach': new_stats.reach,
                    'engagement_rate': new_stats.engagement_rate,
                    'created_at': new_stats.created_at
                }
            })
        else:
            # Create first statistics entry
            new_stats = InstagramStatistics.objects.create(
                user=user,
                new_followers=0,
                new_likes=0,
                new_comments=0,
                **current_stats
            )
            
            return Response({
                'status': 'success',
                'message': 'Initial statistics created successfully',
                'data': {
                    'followers_count': new_stats.followers_count,
                    'following_count': new_stats.following_count,
                    'posts_count': new_stats.posts_count,
                    'all_likes_count': new_stats.all_likes_count,
                    'all_comments_count': new_stats.all_comments_count,
                    'new_followers': 0,
                    'new_likes': 0,
                    'new_comments': 0,
                    'profile_visits': new_stats.profile_visits,
                    'impressions': new_stats.impressions,
                    'reach': new_stats.reach,
                    'engagement_rate': new_stats.engagement_rate,
                    'created_at': new_stats.created_at
                }
            })
            
    except Exception as e:
        logger.error(f"Update statistics error: {e}")
        return Response({
            'status': 'error',
            'message': f'Failed to update statistics: {str(e)}'
        }, status=500)

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def schedule_post(request):
    """Schedule a new post and optionally post it immediately"""
    user = request.user
    
    image_url = request.data.get('image_url')
    caption = request.data.get('caption')
    scheduled_time = request.data.get('scheduled_time')  
    reason = request.data.get('reason', 'User scheduled post')
    tourism_object_id = request.data.get('tourism_object_id')

    if not image_url or not caption or not scheduled_time:
        return Response({
            "status": "error", 
            "message": "image_url, caption, and scheduled_time are required"
        }, status=400)
    
    try:
        parsed_time = parse_datetime(scheduled_time)
        if parsed_time is None:
            return Response({
                "status": "error", 
                "message": "Invalid scheduled_time format"
            }, status=400)
        
        if parsed_time.tzinfo is None:
            parsed_time = timezone.make_aware(parsed_time)
            
        tourism_object = TourismObject.objects.get(id=tourism_object_id)
        scheduled_post = ScheduledPost.objects.create(
            user=user,
            scheduled_time=scheduled_time,
            reason=reason,
            image_url=image_url,
            caption=caption,
            tourism_object=tourism_object,
            is_posted=False
        )
        
        return Response({
            "status": "success", 
            "message": "Post scheduled successfully",
            "data": {
                "id": scheduled_post.id,
                "scheduled_time": scheduled_post.scheduled_time,
                "reason": scheduled_post.reason,
                "image_url": scheduled_post.image_url,
                "caption": scheduled_post.caption,
                "is_posted": scheduled_post.is_posted,
                "created_at": scheduled_post.created_at,
                "updated_at": scheduled_post.updated_at
            }
        })
    except Exception as e:
        logger.error(f"Schedule post error: {e}")
        return Response({
            "status": "error", 
            "message": f"Failed to schedule post: {str(e)}"
        }, status=500)

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_scheduled_posts(request):
    """Get all scheduled posts for the authenticated user"""
    user = request.user
    
    # Get query parameters
    page = request.GET.get('page', 1)
    page_size = request.GET.get('page_size', 20)
    posted_filter = request.GET.get('posted')  # 'true', 'false', or None for all
    
    # Filter posts
    posts = ScheduledPost.objects.filter(user=user).order_by('-scheduled_time')
    
    if posted_filter is not None:
        is_posted = posted_filter.lower() == 'true'
        posts = posts.filter(is_posted=is_posted)
    
    # Paginate
    paginator = Paginator(posts, page_size)
    page_obj = paginator.get_page(page)
    
    # Serialize data
    posts_data = []
    for post in page_obj:
        posts_data.append({
            'id': post.id,
            'scheduled_time': post.scheduled_time,
            'reason': post.reason,
            'image_url': post.image_url,
            'caption': post.caption,
            'is_posted': post.is_posted,
            'is_overdue': post.is_overdue,
            'created_at': post.created_at,
            'updated_at': post.updated_at,
        })
    
    return Response({
        'status': 'success',
        'data': posts_data,
        'pagination': {
            'current_page': page_obj.number,
            'total_pages': paginator.num_pages,
            'total_count': paginator.count,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous(),
        }
    })
@api_view(['GET'])
@permission_classes([AllowAny])
def get_tourism_objects(request):
    """Get all tourism objects with real metrics from database"""
    try:
        from .models import TourismObject, Posts, PostStatistics
        from django.db.models import Count, Sum, Avg
        
        # Get all tourism objects
        tourism_objects = TourismObject.objects.all().order_by('object_type', 'name')
        
        # Create response data with real metrics
        objects_data = []
        for obj in tourism_objects:
            # Get real posts data for this tourism object
            posts = Posts.objects.filter(tourism_object=obj)
            
            # Calculate real metrics
            total_posts = posts.count()
            total_likes = posts.aggregate(Sum('like_count'))['like_count__sum'] or 0
            total_comments = posts.aggregate(Sum('comment_count'))['comment_count__sum'] or 0
            
            # Calculate growth rates from last 24 hours
            twenty_four_hours_ago = timezone.now() - timedelta(hours=24)
            recent_stats = PostStatistics.objects.filter(
                tourism_object=obj,
                recorded_at__gte=twenty_four_hours_ago
            )
            
            # Calculate percentage changes
            likes_percent_increase = 0
            comments_percent_increase = 0
            
            if recent_stats.exists():
                total_likes_change = recent_stats.aggregate(Sum('likes_change'))['likes_change__sum'] or 0
                total_comments_change = recent_stats.aggregate(Sum('comments_change'))['comments_change__sum'] or 0
                
                if total_likes > 0:
                    likes_percent_increase = round((total_likes_change / total_likes) * 100, 1)
                if total_comments > 0:
                    comments_percent_increase = round((total_comments_change / total_comments) * 100, 1)
            
            object_data = {
                'id': obj.id,
                'name': obj.name,
                'object_type': obj.object_type,
                'location': obj.location,
                'rating': float(obj.rating) if obj.rating else 0.0,
                'image_url': obj.image_url,
                'metrics': {
                    'total_posts': total_posts,
                    'total_likes': total_likes,
                    'total_comments': total_comments,
                    'likes_percent_increase': likes_percent_increase,
                    'comments_percent_increase': comments_percent_increase,
                },
                'last_updated': timezone.now().isoformat()
            }
            objects_data.append(object_data)
        
        # Group by object type
        hotels = [obj for obj in objects_data if obj['object_type'] == 'hotel']
        destinations = [obj for obj in objects_data if obj['object_type'] == 'destination']
        
        return Response({
            'status': 'success',
            'data': {
                'hotels': hotels,
                'destinations': destinations,
                'total_count': len(objects_data),
                'hotels_count': len(hotels),
                'destinations_count': len(destinations)
            }
        })
        
    except Exception as e:
        logger.error(f"Error fetching tourism objects: {str(e)}")
        return Response({
            'status': 'error',
            'message': f'Failed to fetch tourism objects: {str(e)}'
        }, status=500)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_tourism_object_detail(request, object_id):
    """Get detailed metrics for a specific tourism object using real data"""
    try:
        from .models import TourismObject, Posts, PostStatistics
        from django.db.models import Sum
        
        # Get the specific tourism object
        try:
            tourism_object = TourismObject.objects.get(id=object_id)
        except TourismObject.DoesNotExist:
            return Response({
                'status': 'error',
                'message': 'Tourism object not found'
            }, status=404)
        
        # Get real posts for this tourism object
        posts = Posts.objects.filter(tourism_object=tourism_object)
        
        # Calculate real metrics
        total_posts = posts.count()
        total_likes = posts.aggregate(Sum('like_count'))['like_count__sum'] or 0
        total_comments = posts.aggregate(Sum('comment_count'))['comment_count__sum'] or 0
        
        # Calculate growth rates from last 24 hours
        twenty_four_hours_ago = timezone.now() - timedelta(hours=24)
        recent_stats = PostStatistics.objects.filter(
            tourism_object=tourism_object,
            recorded_at__gte=twenty_four_hours_ago
        )
        
        likes_percent_increase = 0
        comments_percent_increase = 0
        
        if recent_stats.exists():
            total_likes_change = recent_stats.aggregate(Sum('likes_change'))['likes_change__sum'] or 0
            total_comments_change = recent_stats.aggregate(Sum('comments_change'))['comments_change__sum'] or 0
            
            if total_likes > 0:
                likes_percent_increase = round((total_likes_change / total_likes) * 100, 1)
            if total_comments > 0:
                comments_percent_increase = round((total_comments_change / total_comments) * 100, 1)
        
        # Generate real historical data (last 7 days)
        historical_data = []
        for i in range(8):  # 8 days including today
            date = timezone.now() - timedelta(days=7-i)
            day_start = date.replace(hour=0, minute=0, second=0, microsecond=0)
            day_end = day_start + timedelta(days=1)
            
            # Get statistics for this day
            day_stats = PostStatistics.objects.filter(
                tourism_object=tourism_object,
                recorded_at__gte=day_start,
                recorded_at__lt=day_end
            )
            
            day_likes = day_stats.aggregate(Sum('like_count'))['like_count__sum'] or 0
            day_comments = day_stats.aggregate(Sum('comment_count'))['comment_count__sum'] or 0
            
            historical_data.append({
                'date': date.strftime('%Y-%m-%d'),
                'likes': day_likes,
                'comments': day_comments,
            })
        
        # Get top performing posts (real data)
        top_posts = posts.order_by('-like_count')[:5]
        top_performing_posts = []
        
        for post in top_posts:
            top_performing_posts.append({
                'id': post.id,
                'shortcode': post.shortcode,
                'media_id': post.media_id,
                'likes': post.like_count,
                'comments': post.comment_count,
                'date': post.posted_at.strftime('%Y-%m-%d') if post.posted_at else None,
                'caption': post.caption[:100] + "..." if len(post.caption) > 100 else post.caption
            })
        
        detailed_data = {
            'id': tourism_object.id,
            'name': tourism_object.name,
            'object_type': tourism_object.object_type,
            'location': tourism_object.location,
            'rating': float(tourism_object.rating) if tourism_object.rating else 0.0,
            'image_url': tourism_object.image_url,
            'metrics': {
                'total_posts': total_posts,
                'total_likes': total_likes,
                'total_comments': total_comments,
                'likes_percent_increase': likes_percent_increase,
                'comments_percent_increase': comments_percent_increase,
                'average_likes_per_post': round(total_likes / total_posts, 1) if total_posts > 0 else 0,
                'average_comments_per_post': round(total_comments / total_posts, 1) if total_posts > 0 else 0,
            },
            'historical_data': historical_data,
            'top_performing_posts': top_performing_posts
        }
        
        return Response({
            'status': 'success',
            'data': detailed_data
        })
        
    except Exception as e:
        logger.error(f"Error fetching tourism object detail: {str(e)}")
        return Response({
            'status': 'error',
            'message': f'Failed to fetch tourism object details: {str(e)}'
        }, status=500)
    
@api_view(['POST'])
@permission_classes([AllowAny])
def post_photo(request):
    image_path = request.data.get('image_path')
    caption = request.data.get('caption')
    tourism_object_id = request.data.get('tourism_object_id')
    if not image_path or not caption:
        return Response({"error": "image_path and caption are required"}, status=400)
    
    user_id = request.data.get('user_id')
    if not user_id:
        user = request.user
    else:
        user = User.objects.filter(id=user_id).first()

    bot = user_bots.get(user.id)
    if not bot:
        try:
            # Only create new bot if not in memory
            bot = InstagramBot(user_obj=user, password=user.password)
            user_bots[user.id] = bot
        except Exception as e:
            logger.error(f"Failed to initialize bot for user {user.id}: {str(e)}")
            return Response({"error": f"Bot initialization failed: {str(e)}"}, status=500)
    try:
        media = bot.post_from_cloudinary(image_path, caption, tourism_object_id)
        return Response({
            "status": "success",
            "message": "Photo posted successfully",
            "data": {
                "media_id": media.id,
                "shortcode": media.code,
                "tourism_object_id": tourism_object_id
            }
        })
    except Exception as e:
        logger.error(f"Post photo error: {e}")
        return Response({'error': 'Failed to post photo'}, status=500)
    
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_posts(request):
    """Get user's posts with tourism object information"""
    try:
        user = request.user
        
        posts = Posts.objects.filter(user=user).order_by('-posted_at')
        
        posts_data = []
        for post in posts:
            posts_data.append({
                "id": post.id,
                "media_id": post.media_id,
                "shortcode": post.shortcode,
                "caption": post.caption,
                "like_count": post.like_count,
                "comment_count": post.comment_count,
                "posted_at": post.posted_at,
                "tourism_object": {
                    "id": post.tourism_object.id,
                    "name": post.tourism_object.name,
                    "type": post.tourism_object.object_type,
                    "location": post.tourism_object.location
                }
            })
        
        return Response({
            "status": "success",
            "data": posts_data
        })
        
    except Exception as e:
        logger.error(f"Error in get_posts: {e}")
        return Response({
            "status": "error",
            "message": str(e)
        }, status=500)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_tourism_statistics(request, tourism_object_id):
    """Get statistics for a specific tourism object using bot method"""
    try:
        user = request.user
        hours = int(request.GET.get('hours', 24))
        
        bot = user_bots.get(user.id)
        if not bot:
            try:
                # Only create new bot if not in memory
                bot = InstagramBot(user_obj=user, password=user.password)
                user_bots[user.id] = bot
            except Exception as e:
                logger.error(f"Failed to initialize bot for user {user.id}: {str(e)}")
                return Response({"error": f"Bot initialization failed: {str(e)}"}, status=500)

        result = bot.get_tourism_object_stats(tourism_object_id, hours)
        
        return Response({
            "status": "success" if result["success"] else "error",
            "data": result
        })
        
    except Exception as e:
        logger.error(f"Error in get_tourism_statistics: {e}")
        return Response({
            "status": "error",
            "message": str(e)
        }, status=500)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_all_tourism_statistics(request):
    """Get statistics for all tourism objects"""
    try:
        user = request.user
        hours = int(request.GET.get('hours', 24))
        
        bot = user_bots.get(user.id)
        if not bot:
            try:
                # Only create new bot if not in memory
                bot = InstagramBot(user_obj=user, password=user.password)
                user_bots[user.id] = bot
            except Exception as e:
                logger.error(f"Failed to initialize bot for user {user.id}: {str(e)}")
                return Response({"error": f"Bot initialization failed: {str(e)}"}, status=500)
        
        result = bot.get_all_tourism_stats(hours)
        
        return Response({
            "status": "success" if result["success"] else "error",
            "data": result
        })
        
    except Exception as e:
        logger.error(f"Error in get_all_tourism_statistics: {e}")
        return Response({
            "status": "error",
            "message": str(e)
        }, status=500)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_tourism_objects_list(request):
    """Get list of tourism objects for dropdown"""
    try:
        from .models import TourismObject
        tourism_objects = TourismObject.objects.all().order_by('name')
        
        data = []
        for obj in tourism_objects:
            data.append({
                "id": obj.id,
                "name": obj.name,
                "object_type": obj.object_type,
                "location": obj.location
            })
        
        return Response({
            "status": "success",
            "data": data
        })
        
    except Exception as e:
        logger.error(f"Error in get_tourism_objects_list: {e}")
        return Response({
            "status": "error",
            "message": str(e)
        }, status=500)
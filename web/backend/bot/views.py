from rest_framework.decorators import api_view
from rest_framework.response import Response
from .bot import InstagramBot
import requests
from django.http import HttpResponse

def proxy_image(request):
    url = request.GET.get('url')
    if not url:
        return HttpResponse("No URL", status=400)

    try:
        resp = requests.get(url, stream=True)
        content_type = resp.headers.get('Content-Type', 'image/jpeg')
        response = HttpResponse(resp.content, content_type=content_type)
        response["Access-Control-Allow-Origin"] = "*"
        return response
    except Exception as e:
        return HttpResponse(str(e), status=500)

global_bot = None

@api_view(['POST'])
def login_bot(request):
    global global_bot
    username = request.data.get('username')
    password = request.data.get('password')
    global_bot = InstagramBot(username, password)
    return Response({"status": "login attempt made"})

@api_view(['GET'])
def get_posts(request):
    if not global_bot:
        return Response({"error": "Bot not initialized"}, status=400)
    posts = global_bot.get_recent_posts()
    return Response(posts)

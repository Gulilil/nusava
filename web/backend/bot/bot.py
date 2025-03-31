from instagrapi import Client
import os
from .models import BotActionLog

class InstagramBot:
    def __init__(self, username: str, password: str, session_file: str = "session.json"):
        self.username = username
        self.password = password
        self.session_file = session_file
        self.client = Client()
        self.login()

    def login(self):
        if os.path.exists(self.session_file):
            self.client.load_settings(self.session_file)
        try:
            self.client.login(self.username, self.password)
            self.client.dump_settings(self.session_file)
            print("Logged in as", self.username)
        except Exception as e:
            print(f"Login failed: {e}")

    def like_post(self, media_url: str):
        try:
            media_id = self.client.media_pk_from_url(media_url)
            self.client.media_like(media_id)
            print(f"Liked: {media_url}")
        except Exception as e:
            print(f"Like failed: {e}")

    def follow_user(self, target_username: str):
        try:
            user_id = self.client.user_id_from_username(target_username)
            self.client.user_follow(user_id)
            print(f"Followed: {target_username}")
        except Exception as e:
            print(f"Follow failed: {e}")

    def comment_on_post(self, media_url: str, comment: str):
        try:
            media_id = self.client.media_pk_from_url(media_url)
            self.client.media_comment(media_id, comment)
            print(f"Commented: {comment}")
        except Exception as e:
            print(f"Comment failed: {e}")

    def post_photo(self, image_path: str, caption: str):
        try:
            self.client.photo_upload(image_path, caption)
            print(f"Posted photo: {image_path}")
        except Exception as e:
            print(f"Post failed: {e}")

    def share_post_dm(self, media_url: str, usernames: list):
        try:
            media_id = self.client.media_pk_from_url(media_url)
            user_ids = [self.client.user_id_from_username(u) for u in usernames]
            self.client.direct_send(media_ids=[media_id], user_ids=user_ids)
            print(f"Shared via DM to: {usernames}")
        except Exception as e:
            print(f"DM Share failed: {e}")

    def send_dm(self, username: str, message: str):
        try:
            user_id = self.client.user_id_from_username(username)
            self.client.direct_send(text=message, user_ids=[user_id])
            print(f"Sent DM to {username}")
        except Exception as e:
            print(f"DM failed: {e}")
    
    def get_recent_posts(self):
        try:
            medias = self.client.user_medias_v1(self.client.user_id, 10)
            return [
                {
                    "id": str(m.pk),
                    "caption": m.caption_text,
                    "like_count": m.like_count,
                    "comment_count": m.comment_count,
                    "thumbnail_url": str(m.thumbnail_url),
                } for m in medias
            ]
        except Exception as e:
            return []

    def log(self, action_type, target, status, message):
        BotActionLog.objects.create(
            action_type=action_type,
            target=target,
            status=status,
            message=message,
        )

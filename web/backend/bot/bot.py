from instagrapi import Client
from .models import User, ActionLog

class InstagramBot:
    def __init__(self, user_obj: User, password: str, session_settings=None):
        self.username = user_obj.username
        self.password = password
        self.user_obj = user_obj
        self.client = Client()

        if session_settings:
            self.client.set_settings(session_settings)

        try:
            self.client.login(self.username, self.password)
            self.user_obj.session_json = self.client.get_settings()
            self.user_obj.save()
        except Exception as e:
            raise e

    def log(self, action_type, target, status, message):
        ActionLog.objects.create(
            user=self.user_obj,
            action_type=action_type,
            target=target,
            status=status,
            message=message,
        )

    def like_post(self, media_url: str):
        try:
            media_id = self.client.media_pk_from_url(media_url)
            self.client.media_like(media_id)
            self.log("like", media_url, "success", "Liked post")
        except Exception as e:
            self.log("like", media_url, "failed", str(e))
            raise e

    def follow_user(self, target_username: str):
        try:
            user_id = self.client.user_id_from_username(target_username)
            self.client.user_follow(user_id)
            self.log("follow", target_username, "success", "Followed user")
        except Exception as e:
            self.log("follow", target_username, "failed", str(e))
            raise e

    def comment_on_post(self, media_url: str, comment: str):
        try:
            media_id = self.client.media_pk_from_url(media_url)
            self.client.media_comment(media_id, comment)
            self.log("comment", media_url, "success", f"Commented: {comment}")
        except Exception as e:
            self.log("comment", media_url, "failed", str(e))
            raise e

    def post_photo(self, image_path: str, caption: str):
        try:
            self.client.photo_upload(image_path, caption)
            self.log("post_photo", image_path, "success", f"Posted photo")
        except Exception as e:
            self.log("post_photo", image_path, "failed", str(e))
            raise e

    def share_post_dm(self, media_url: str, usernames: list):
        try:
            media_id = self.client.media_pk_from_url(media_url)
            user_ids = [self.client.user_id_from_username(u) for u in usernames]
            self.client.direct_send(media_ids=[media_id], user_ids=user_ids)
            self.log("share_dm", media_url, "success", f"Shared to {usernames}")
        except Exception as e:
            self.log("share_dm", media_url, "failed", str(e))
            raise e

    def send_dm(self, username: str, message: str):
        try:
            user_id = self.client.user_id_from_username(username)
            self.client.direct_send(text=message, user_ids=[user_id])
            self.log("send_dm", username, "success", f"Sent DM: {message}")
        except Exception as e:
            self.log("send_dm", username, "failed", str(e))
            raise e

    def get_recent_posts(self):
        try:
            medias = self.client.user_medias_v1(self.client.user_id, 10)
            insight =self.client.insights_account
            return [
                {
                    "id": str(m.pk),
                    "caption": m.caption_text,
                    "like_count": m.like_count,
                    "comment_count": m.comment_count,
                    "shortcode": m.code,
                } for m in medias
            ]
        except Exception as e:
            self.log("get_posts", "", "failed", str(e))
            return []

    def get_settings(self):
        return self.client.get_settings()
    

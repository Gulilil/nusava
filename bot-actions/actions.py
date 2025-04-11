from instagrapi import Client
import os

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

    # Example scheduled daily post
    # def schedule_daily_post(self, image_path: str, caption: str, post_time: str = "10:00"):
    #     def job():
    #         print(f"Scheduled post at {post_time}")
    #         self.post_photo(image_path, caption)

    #     schedule.every().day.at(post_time).do(job)
    #     print(f"Daily post scheduled at {post_time}")

    #     while True:
    #         schedule.run_pending()
    #         time.sleep(1)

# --------------------- USAGE EXAMPLE ---------------------
if __name__ == "__main__":
    bot = InstagramBot('nusa.testing', 'skripsi')

    # Manual Actions
    bot.like_post("https://www.instagram.com/p/DEQBq_Gy2dc/?utm_source=ig_web_copy_link&igsh=MzRlODBiNWFlZA==")
    # bot.follow_user("alexanderjason36")
    # bot.comment_on_post("https://www.instagram.com/p/DEQBq_Gy2dc/?utm_source=ig_web_copy_link&igsh=MzRlODBiNWFlZA==", "Awesome post!")
    # bot.post_photo("your_image.jpg", "Hello from the bot!")
    # bot.share_post_dm("https://www.instagram.com/p/DEQBq_Gy2dc/?utm_source=ig_web_copy_link&igsh=MzRlODBiNWFlZA==", ["json.dumpss", "alexanderjason36"])
    # bot.send_dm("alexanderjason36", "Hey there!")

    # Auto-post daily at 10:00 AM
    # bot.schedule_daily_post("your_image.jpg", "Daily post!", post_time="10:00")

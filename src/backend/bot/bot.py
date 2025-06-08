from instagrapi import Client
from .models import User, ActionLog
from typing import List
from instagrapi.types import DirectThread

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

    def process_thread_messages(self, threads: List[DirectThread],is_pending=False):
        processed_threads = []
        
        for thread in threads:
            if not thread.messages:
                continue
                
            # Step 1: Auto-approve pending threads first (if needed)
            if is_pending:
                print(f"Auto-approving pending thread {thread.id}...")
                approval_success = self.client.direct_pending_approve(thread.id)
                if not approval_success:
                    print(f"Failed to approve thread {thread.id}")
                    continue 
                print(f"✅ Thread {thread.id} approved")
                
            # Step 2: Combine all messages from users in this thread
            user_messages = []
            latest_timestamp = None
            
            for msg in thread.messages:
                # Only include messages sent TO the bot (not from the bot)
                if msg.is_sent_by_viewer:
                    break
                else:
                    user_messages.append(msg.text.strip())
                    # Get the latest timestamp from user messages
                    if not latest_timestamp or msg.timestamp > latest_timestamp:
                        latest_timestamp = msg.timestamp
            
            # Skip if no user messages found
            if not user_messages:
                continue
                
            # Combine all reverse user messages with dots 
            combined_message = ". ".join(user_messages[::-1])        
            thread_data = {
                'thread_id': thread.id,
                'thread_pk': thread.pk,
                'username': thread.users[0].username if thread.users else 'Unknown',
                'combined_message': combined_message,
                'message_count': len(user_messages),
                'is_pending': is_pending,
                'latest_timestamp': latest_timestamp.isoformat() if latest_timestamp else '',
                'approved': True if (is_pending) else None,  # Track approval status
            }
            
            processed_threads.append(thread_data)    
        return processed_threads

    def get_all_combined_messages(self, amount=20):
        """Get all threads (regular + pending) with combined messages and auto-approve pending"""
        try:
            print("=== Getting All Combined Messages ===")
            
            all_processed = []
            
            # Get regular threads
            print("\n--- Processing Regular Threads ---")
            regular_threads = self.client.direct_threads(amount, selected_filter='unread')
            regular_processed = self.process_thread_messages(regular_threads, is_pending=False)
            all_processed.extend(regular_processed)
            
            # Get pending threads and auto-approve them
            print("\n--- Processing Pending Threads (with auto-approval) ---")
            pending_threads = self.client.direct_pending_inbox(amount)
            pending_processed = self.process_thread_messages(pending_threads, is_pending=True)
            all_processed.extend(pending_processed)
            
            # Sort by timestamp (newest first)
            all_processed.sort(key=lambda x: x['latest_timestamp'], reverse=True)
                    
            print(f"\n=== Summary ===")
            print(f"Total: {len(all_processed)} threads")
            print(f"Regular: {len(regular_processed)} threads")
            print(f"Pending: {len(pending_processed)} threads")
            return all_processed
            
        except Exception as e:
            print(f"Error getting combined messages: {str(e)}")
            return []

    def send_dm_replies(self, thread_data):
        try:
            thread_id = thread_data['thread_id']
            username = thread_data['username']
            combined_message = thread_data['combined_message']
            is_pending = thread_data['is_pending']
            
            print(f"\n--- Processing {username} ---")
            
            if is_pending and thread_data.get('approved'):
                print(f"Status: PENDING (Already approved)")
            elif is_pending:
                print(f"Status: PENDING (Not approved)")
            else:
                print(f"Status: REGULAR")
                
            print(f"Combined message: {combined_message[:150]}...")
            
            # Generate response based on combined message
            reply_text = self.generate_response(combined_message)
            
            # Send reply
            reply_success = self.client.direct_send(text=reply_text, thread_ids=[thread_id])
            
            if not reply_success:
                print("Failed to send reply")
                return False
            
            print(f"Replied: {reply_text[:50]}...")
            
            # Mark as seen
            self.client.direct_send_seen(thread_id)
            print("Marked as seen")
            
            return True
            
        except Exception as e:
            print(f"Error handling thread automation: {str(e)}")
            return False

    def start_dm_automation(self, amount=10):
        """Complete automation with optimized memory usage"""
        try:
            print("=== Starting Optimized DM Automation ===")
            
            # Get all threads
            all_threads = self.get_all_combined_messages(amount)
            
            if not all_threads:
                print("No threads to process")
                return
            
            # Process each thread
            success_count = 0
            for thread_data in all_threads:
                success = self.send_dm_replies(thread_data)
                if success:
                    success_count += 1
            
            print(f"\n=== Automation Complete ===")
            print(f"Processed: {success_count}/{len(all_threads)} threads successfully")
            
        except Exception as e:
            print(f"Error in optimized automation: {str(e)}")

    def generate_response(self, combined_message):
        """Generate travel response based on combined conversation context"""
        # TODO: Send combined_message to your LLM for better context
        return "Thanks for reaching out! I'm here to help with all your travel needs. What destination or travel service are you interested in?"
        
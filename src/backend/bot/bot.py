from datetime import timedelta, timezone
import json
import random
import time
from instagrapi import Client
from .models import PostStatistics, Posts, TourismObject, User, ActionLog
from .session_manager import SessionManager
from typing import List
from instagrapi.types import DirectThread
import requests
from dotenv import load_dotenv
load_dotenv()
import os
import logging
from .utils import download_image_from_url, cleanup_temp_file

logger = logging.getLogger(__name__)

class InstagramBot:
    def __init__(self, user_obj: User, password: str, session_settings=None):
        self.username = user_obj.username
        self.password = password
        self.user_obj = user_obj
        self.session_manager = SessionManager()
        self.client = Client()
        try:
            # Use the new session manager for proper session handling
            self.client = self.session_manager.login_user(self.username, self.password, self.user_obj)
            
            # Session is automatically saved to database in login_user method
            logger.info(f"Instagram bot initialized successfully for user: {self.username}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Instagram bot for {self.username}: {str(e)}")
            raise e

    def log(self, action_type, target, status, message):
        ActionLog.objects.create(
            user=self.user_obj,
            action_type=action_type,
            target=target,
            status=status,
            message=message,
        )

    def like_post(self, media_id: str, media_url: str = None):
        try:
            if media_url:
                media_id = self.client.media_pk_from_url(media_url)
            self.client.media_like(media_id)
            self.log("like", media_id, "success", "Liked post")
        except Exception as e:
            self.log("like", media_id, "failed", str(e))
            raise e

    def follow_user(self, target_username: str):
        try:
            user_id = self.client.user_id_from_username(target_username)
            self.client.user_follow(user_id)
            self.log("follow", target_username, "success", "Followed user")
        except Exception as e:
            self.log("follow", target_username, "failed", str(e))
            raise e

    def comment_on_post(self, comment: str, media_id: str, media_url: str = None):
        try:
            if media_url:
                media_id = self.client.media_pk_from_url(media_url)
            self.client.media_comment(media_id, comment)
            self.log("comment", media_id, "success", f"Commented: {comment}")
        except Exception as e:
            self.log("comment", media_id, "failed", str(e))
            raise e

    def post_photo(self, image_path: str, caption: str, tourism_object_id: int = None):
        try:
            media = self.client.photo_upload(image_path, caption)
            
            # Create Posts record if tourism_object is provided
            if tourism_object_id:
                try:
                    tourism_object = TourismObject.objects.get(id=tourism_object_id)
                    Posts.objects.create(
                        user=self.user_obj,
                        tourism_object=tourism_object,
                        media_id=str(media.pk),
                        shortcode=media.code,
                        caption=caption,
                        like_count=0,  # Initial counts
                        comment_count=0,
                        posted_at=media.taken_at
                    )
                    self.log("post_photo", image_path, "success", f"Posted photo and linked to {tourism_object.name}")
                except TourismObject.DoesNotExist:
                    self.log("post_photo", image_path, "warning", f"Tourism object {tourism_object_id} not found")
        except Exception as e:
            self.log("post_photo", image_path, "failed", str(e))
            raise e
    
    def post_from_cloudinary(self, image_url: str, caption: str, tourism_object_id: int) -> bool:
        """
        Post image from Cloudinary URL to Instagram
        
        Parameters
        ----------
        image_url: str
            Cloudinary image URL
        caption: str
            Post caption
            
        Returns
        -------
        bool
            Success status
        """
        temp_file_path = None
        try:
            # Download image from Cloudinary to temp file
            temp_file_path = download_image_from_url(image_url)
            
            # Upload to Instagram using instagrapi
            media = self.client.photo_upload(
                path=temp_file_path,
                caption=caption
            )
            
            if tourism_object_id:
                try:
                    tourism_object = TourismObject.objects.get(id=tourism_object_id)
                    Posts.objects.create(
                        user=self.user_obj,
                        tourism_object=tourism_object,
                        media_id=str(media.pk),
                        shortcode=media.code,
                        caption=caption,
                        like_count=0,
                        comment_count=0,
                        posted_at=media.taken_at
                    )
                    self.log("post_from_cloudinary", image_url, "success", f"Posted from Cloudinary and linked to {tourism_object.name}")
                except TourismObject.DoesNotExist:
                    self.log("post_from_cloudinary", image_url, "warning", f"Tourism object {tourism_object_id} not found")
            else:
                self.log("post_from_cloudinary", image_url, "success", "Posted from Cloudinary without tourism object link")
            
            return True
            
            
        except Exception as e:
            self.log("post_photo", temp_file_path, "failed", str(e))
            return False
            
        finally:
            # Clean up temporary file
            if temp_file_path:
                cleanup_temp_file(temp_file_path)

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
            
            print(f"\n--- Processing {username} ---")
            
            # Generate response based on combined message (should return list of messages)
            reply_messages = self.generate_response(combined_message, username)
            
            if not reply_messages:
                print("No response generated")
                return False
            
            
            print(f"Sending {len(reply_messages)} message(s) to {username}")
            
            # Send each message with realistic delays to simulate human behavior
            for i, message in enumerate(reply_messages):
                if not message or not message.strip():
                    continue
                    
                print(f"Sending message {i+1}/{len(reply_messages)}: {message[:50]}...")
                
                # Send the message
                reply_success = self.client.direct_send(text=message, thread_ids=[thread_id])
                
                if not reply_success:
                    print(f"Failed to send message {i+1}")
                    return False
                                
                if i < len(reply_messages) - 1:
                    typing_delay = min(max(len(message) * 0.05, 2), 8)  # 2-8 seconds based on length
                    print(f"typing delay: {typing_delay:.1f} seconds...")
                    time.sleep(typing_delay)

            self.log("dm_reply", username, "success", f"Replied to {username}")
            # Mark as seen after all messages are sent
            self.client.direct_send_seen(thread_id)
            print(f"✅ All messages sent to {username}")
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
                return {"success": 0, "total": 0, "message": "No threads to process"}
            
            # Process each thread
            success_count = 0
            total_threads = len(all_threads)
            for i, thread_data in enumerate(all_threads):
                success = self.send_dm_replies(thread_data)
                if success:
                    success_count += 1
                if i < total_threads - 1: 
                    if total_threads <= 3:
                        sleep_time = random.randint(10, 15)   # 10-15 seconds for few messages
                    elif total_threads <= 10:
                        sleep_time = random.randint(15, 30)  # 15-30 seconds for moderate
                    else:
                        sleep_time = random.randint(30, 60) # 30-60 seconds for many messages
                    
                    print(f"⏰ Waiting {sleep_time} seconds before next reply...")
                    time.sleep(sleep_time)
            
            result_message = f"Processed: {success_count}/{len(all_threads)} threads successfully"
            
            return {
                "success": success_count,
                "total": len(all_threads),
                "message": result_message
            }
            
        except Exception as e:
            print(f"Error in optimized automation: {str(e)}")
            return {"success": 0, "total": 0, "message": f"Error: {str(e)}"}

    def generate_response(self, combined_message: str, username: str):
        """Generate travel response based on combined conversation context"""
        llm_module_url = os.getenv("LLM_MODULE_URL")
        api_url = f"{llm_module_url}/chat"
        data = {
            "chat_message": combined_message,
            "sender_id": username
            }

        response = requests.post(api_url, json=data)

        if (response.status_code == 200):
            response_json = response.json()
            return response_json['response']
        else:
            return None
    
    # ============= STATISTICS ==============
    def get_account_statistics(self):
        """Get comprehensive account statistics using user_info_v1 and insights_account"""
        try:
            # Get basic account info
            user_info = self.client.user_info_v1(self.client.user_id)
            
            # Get account insights
            insights = self.client.insights_account()
            
            # Get all posts to calculate total likes and comments
            all_medias = self.client.user_medias_v1(self.client.user_id, amount=0)  # 0 means all
            
            total_likes = sum(media.like_count for media in all_medias)
            total_comments = sum(media.comment_count for media in all_medias)
            
            stats_data = {
                'followers_count': user_info.follower_count,
                'following_count': user_info.following_count,
                'posts_count': user_info.media_count,
                'all_likes_count': total_likes,
                'all_comments_count': total_comments,
                
                # Account insights - Profile metrics
                'profile_visits': insights.get('profile_visits', 0),
                'profile_visits_delta': insights.get('profile_visits_delta', 0),
                'website_visits': insights.get('website_visits', 0),
                'website_visits_delta': insights.get('website_visits_delta', 0),
                
                # Content metrics
                'impressions': insights.get('impressions', 0),
                'impressions_delta': insights.get('impressions_delta', 0),
                'reach': insights.get('reach'),
                'reach_delta': insights.get('reach_delta'),
            }
            
            return stats_data
            
        except Exception as e:
            self.log("get_statistics", "", "failed", str(e))
            raise e
        
    def update_post_statistics(self):
        """
        Update statistics for posts linked to tourism objects
        Called by get_account_statistics to update post stats
        """
        try:
            # Get all posts from Instagram
            all_medias = self.client.user_medias_v1(self.client.user_id, amount=50)
            
            updated_posts = 0
            new_statistics = 0
            
            for media in all_medias:
                try:
                    media_id = str(media.pk)
                    current_likes = media.like_count
                    current_comments = media.comment_count
                    
                    # Find corresponding Posts record in our database
                    try:
                        post_record = Posts.objects.get(user=self.user_obj, media_id=media_id)
                    except Posts.DoesNotExist:
                        # Skip if this post is not linked to any tourism object
                        continue
                    
                    # Update the post's current counts
                    post_record.like_count = current_likes
                    post_record.comment_count = current_comments
                    post_record.save()
                    updated_posts += 1
                    
                    # Get the most recent statistics record for this post
                    previous_stat = PostStatistics.objects.filter(
                        post=post_record
                    ).order_by('-recorded_at').first()
                    
                    # Calculate changes
                    likes_change = 0
                    comments_change = 0
                    
                    if previous_stat:
                        likes_change = current_likes - previous_stat.like_count
                        comments_change = current_comments - previous_stat.comment_count
                        
                        # Only create new record if there are changes or it's been more than 6 hours
                        time_diff = timezone.now() - previous_stat.recorded_at
                        if likes_change == 0 and comments_change == 0 and time_diff < timedelta(hours=1):
                            continue   # Skip if no changes and recent record exists
                    
                    # Create new statistics record
                    PostStatistics.objects.create(
                        tourism_object=post_record.tourism_object,
                        post=post_record,
                        like_count=current_likes,
                        comment_count=current_comments,
                        likes_change=likes_change,
                        comments_change=comments_change,
                        recorded_at=timezone.now()
                    )
                    new_statistics += 1
                    
                    self.log("update_post_stats", media_id, "success", 
                           f"Updated stats for {post_record.tourism_object.name}")
                    
                except Exception as e:
                    logger.error(f"Error processing media {media.pk}: {e}")
                    continue
            
            logger.info(f"Post statistics updated: {updated_posts} posts, {new_statistics} new records")
            return {
                "success": True,
                "updated_posts": updated_posts,
                "new_statistics": new_statistics
            }
            
        except Exception as e:
            logger.error(f"Error updating post statistics: {e}")
            self.log("update_post_stats", "", "failed", str(e))
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_account_statistics(self):
        """Get comprehensive account statistics and update post statistics"""
        try:
            # Get basic account info
            user_info = self.client.user_info_v1(self.client.user_id)
            
            # Get account insights
            insights = self.client.insights_account()
            
            # Get all posts to calculate total likes and comments
            all_medias = self.client.user_medias_v1(self.client.user_id, amount=0)  # 0 means all
            
            total_likes = sum(media.like_count for media in all_medias)
            total_comments = sum(media.comment_count for media in all_medias)
            
            # Update post statistics for tourism objects
            post_stats_result = self.update_post_statistics()
            
            stats_data = {
                'followers_count': user_info.follower_count,
                'following_count': user_info.following_count,
                'posts_count': user_info.media_count,
                'all_likes_count': total_likes,
                'all_comments_count': total_comments,
                
                # Account insights - Profile metrics
                'profile_visits': insights.get('profile_visits', 0),
                'profile_visits_delta': insights.get('profile_visits_delta', 0),
                'website_visits': insights.get('website_visits', 0),
                'website_visits_delta': insights.get('website_visits_delta', 0),
                
                # Content metrics
                'impressions': insights.get('impressions', 0),
                'impressions_delta': insights.get('impressions_delta', 0),
                'reach': insights.get('reach'),
                'reach_delta': insights.get('reach_delta'),
                
                # Post statistics update result
                'post_stats_update': post_stats_result
            }
            
            return stats_data
            
        except Exception as e:
            self.log("get_statistics", "", "failed", str(e))
            raise e

    def get_tourism_object_stats(self, tourism_object_id: int, hours: int = 24):
        """Get statistics for a specific tourism object"""
        try:
            tourism_object = TourismObject.objects.get(id=tourism_object_id)
            since_date = timezone.now() - timedelta(hours=hours)
            
            # Get all posts for this tourism object
            posts = Posts.objects.filter(
                user=self.user_obj, 
                tourism_object=tourism_object
            )
            
            if not posts.exists():
                return {
                    "success": True,
                    "tourism_object": tourism_object.name,
                    "message": "No posts found for this tourism object"
                }
            
            # Get latest statistics for each post
            total_likes = 0
            total_comments = 0
            posts_data = []
            
            for post in posts:
                latest_stat = PostStatistics.objects.filter(
                    post=post,
                    recorded_at__gte=since_date
                ).order_by('-recorded_at').first()
                
                if latest_stat:
                    total_likes += latest_stat.like_count
                    total_comments += latest_stat.comment_count
                    posts_data.append({
                        "shortcode": post.shortcode,
                        "media_id": post.media_id,
                        "caption": post.caption[:100] + "..." if len(post.caption) > 100 else post.caption,
                        "likes": latest_stat.like_count,
                        "comments": latest_stat.comment_count,
                        "likes_change": latest_stat.likes_change,
                        "comments_change": latest_stat.comments_change,
                        "posted_at": post.posted_at,
                        "last_updated": latest_stat.recorded_at
                    })
            
            # Calculate growth rates
            likes_growth = 0
            comments_growth = 0
            
            if posts_data:
                total_likes_change = sum(p["likes_change"] for p in posts_data)
                total_comments_change = sum(p["comments_change"] for p in posts_data)
                
                if total_likes > 0:
                    likes_growth = (total_likes_change / (total_likes - total_likes_change)) * 100 if (total_likes - total_likes_change) > 0 else 0
                if total_comments > 0:
                    comments_growth = (total_comments_change / (total_comments - total_comments_change)) * 100 if (total_comments - total_comments_change) > 0 else 0
            
            self.log("get_tourism_stats", str(tourism_object_id), "success", 
                   f"Retrieved stats for {tourism_object.name}")
            
            return {
                "success": True,
                "tourism_object": {
                    "id": tourism_object.id,
                    "name": tourism_object.name,
                    "type": tourism_object.object_type,
                    "location": tourism_object.location
                },
                "period_hours": hours,
                "summary": {
                    "total_posts": len(posts_data),
                    "total_likes": total_likes,
                    "total_comments": total_comments,
                    "average_likes": total_likes / len(posts_data) if posts_data else 0,
                    "average_comments": total_comments / len(posts_data) if posts_data else 0,
                    "likes_growth_rate": round(likes_growth, 2),
                    "comments_growth_rate": round(comments_growth, 2)
                },
                "posts": sorted(posts_data, key=lambda x: x["likes"], reverse=True)
            }
            
        except TourismObject.DoesNotExist:
            self.log("get_tourism_stats", str(tourism_object_id), "failed", "Tourism object not found")
            return {"success": False, "error": "Tourism object not found"}
        except Exception as e:
            self.log("get_tourism_stats", str(tourism_object_id), "failed", str(e))
            return {"success": False, "error": str(e)}

    def get_all_tourism_stats(self, hours: int = 24):
        """Get statistics for all tourism objects that have posts"""
        try:
            # Get all tourism objects that have posts from this user
            tourism_objects_with_posts = TourismObject.objects.filter(
                posts__user=self.user_obj
            ).distinct()
            
            all_stats = []
            
            for tourism_object in tourism_objects_with_posts:
                stats = self.get_tourism_object_stats(tourism_object.id, hours)
                if stats["success"]:
                    all_stats.append(stats)
            
            self.log("get_all_tourism_stats", "", "success", 
                   f"Retrieved stats for {len(all_stats)} tourism objects")
            
            return {
                "success": True,
                "total_objects": len(all_stats),
                "period_hours": hours,
                "tourism_objects": all_stats
            }
            
        except Exception as e:
            self.log("get_all_tourism_stats", "", "failed", str(e))
            return {"success": False, "error": str(e)}

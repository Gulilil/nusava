import threading
import time
import random
from django.conf import settings
from .models import User, ActionLog
from .bot import InstagramBot

class DMAutomationService:
    """Singleton service that manages automation for all users"""
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.running_automations = {}  # user_id -> thread
            self.automation_flags = {}     # user_id -> stop_flag
            self.user_bots = {}           # user_id -> bot_instance
            self.initialized = True
    
    def auto_start_for_user(self, user, min_interval=300, max_interval=900):
        """
        Automatically start automation when user logs in
        This gets called from the login view
        """
        if user.id in self.running_automations:
            # Already running, just return success
            return True, "Automation already running"
        
        return self.start_automation(user.id, min_interval, max_interval)
    
    def start_automation(self, user_id, min_interval=300, max_interval=900):
        """Start automation for specific user"""
        if user_id in self.running_automations:
            return False, "Automation already running for this user"
        
        try:
            user = User.objects.get(id=user_id)
            
            # Create bot instance for this user
            bot = InstagramBot(user_obj=user, password=user.password, 
                             session_settings=user.session_info)
            self.user_bots[user_id] = bot
            
            # Create stop flag for this user
            self.automation_flags[user_id] = threading.Event()
            
            # Create dedicated thread for this user
            thread = threading.Thread(
                target=self._automation_worker,
                args=(user_id, min_interval, max_interval),
                daemon=False,
                name=f"dm_automation_user_{user_id}"  # Named thread for debugging
            )
            
            self.running_automations[user_id] = thread
            thread.start()
            
            bot.log("dm_automation", "", "success", 
                   f"Automation started for user {user.username}")
            
            return True, f"Automation started for user {user.username}"
            
        except Exception as e:
            return False, f"Error starting automation: {str(e)}"
    
    def stop_automation(self, user_id):
        """Stop automation for specific user"""
        if user_id not in self.running_automations:
            return False, "No automation running for this user"
        
        try:
            # Signal this user's thread to stop
            self.automation_flags[user_id].set()
            
            # Wait for this user's thread to finish
            thread = self.running_automations[user_id]
            thread.join(timeout=10)
            
            # Cleanup for this user
            del self.running_automations[user_id]
            del self.automation_flags[user_id]
            if user_id in self.user_bots:
                self.user_bots[user_id].log("dm_automation", "", "success", "Automation stopped")
                del self.user_bots[user_id]
            
            return True, "Automation stopped"
            
        except Exception as e:
            return False, f"Error stopping automation: {str(e)}"
    
    def _automation_worker(self, user_id, min_interval, max_interval):
        """Worker function for specific user - runs in separate thread"""
        try:
            bot = self.user_bots[user_id]
            user = User.objects.get(id=user_id)
            
            bot.log("dm_automation", "", "info", 
                   f"Worker started for {user.username} (ID: {user_id})")
            
            while not self.automation_flags[user_id].is_set():
                try:
                    # Get messages for THIS specific user
                    messages = bot.get_direct_messages()
                    unread = [msg for msg in messages if not msg['is_seen']]
                    
                    if unread:
                        bot.log("dm_automation", "", "info", 
                               f"User {user.username}: Found {len(unread)} unread messages")
                        
                        for msg in unread:
                            bot.log("new_dm", msg['username'], "info",
                                   f"New message from {msg['username']}: {msg['text'][:50]}...")
                    
                    # Random sleep for THIS user
                    sleep_time = random.randint(min_interval, max_interval)
                    bot.log("dm_automation", "", "info", 
                           f"User {user.username}: Sleeping for {sleep_time} seconds")
                    
                    # Sleep in chunks to allow quick stopping
                    for _ in range(0, sleep_time, 10):
                        if self.automation_flags[user_id].is_set():
                            break
                        time.sleep(10)
                        
                except Exception as e:
                    bot.log("dm_automation", "", "error", 
                           f"Loop error for user {user.username}: {str(e)}")
                    time.sleep(60)  # Wait before retrying
            
            bot.log("dm_automation", "", "success", 
                   f"Worker stopped for {user.username}")
            
        except Exception as e:
            try:
                user = User.objects.get(id=user_id)
                ActionLog.objects.create(
                    user=user,
                    action_type="dm_automation",
                    target="",
                    status="error",
                    message=f"Worker error for {user.username}: {str(e)}"
                )
            except:
                pass
    
    def get_status_for_user(self, user_id):
        """Get automation status for specific user"""
        return {
            'is_running': user_id in self.running_automations,
            'user_id': user_id,
            'thread_name': f"dm_automation_user_{user_id}" if user_id in self.running_automations else None
        }
    
    def get_all_running_automations(self):
        """Get status of all running automations"""
        return {
            user_id: {
                'is_running': True,
                'thread_name': thread.name,
                'thread_alive': thread.is_alive()
            }
            for user_id, thread in self.running_automations.items()
        }

# Global service instance
automation_service = DMAutomationService()
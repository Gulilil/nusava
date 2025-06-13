import threading
import time
import random
import logging
from django.conf import settings
from .models import User, ActionLog
from .bot import InstagramBot

logger = logging.getLogger('automation')

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
            return True, "Automation already running"
        
        return self.start_automation(user.id, min_interval, max_interval)
    
    def start_automation(self, user_id, min_interval=300, max_interval=900):
        """Start automation for specific user"""
        if user_id in self.running_automations:
            return False, "Automation already running for this user"
        
        try:
            user = User.objects.get(id=user_id)
            
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
            
            logger.info(f"Automation thread started successfully for user {user.username} (ID: {user_id})")

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
                    result = bot.start_dm_automation(amount=20)
                    if result and result.get('total', 0) > 0: 
                        logger.info(f"Automation cycle completed for {user.username}: {result.get('message', 'Success')}")
                    else:
                        logger.debug(f"No new messages to process for {user.username}")
                    
                    sleep_time = random.randint(min_interval // 30, max_interval // 30) * 30
                    logger.debug(f"Next check for {user.username} in {sleep_time} seconds")
                    
                    for _ in range(0, sleep_time, 30):
                        if self.automation_flags[user_id].is_set():
                            break
                        time.sleep(30)
                        
                except Exception as e:
                    logger.error(f"Automation loop error for user {user.username}: {str(e)}")
                    time.sleep(60) 
            
            logger.info(f"Automation worker stopped for {user.username}")
            
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
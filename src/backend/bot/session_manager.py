import os
import json
import logging
import random
import environ
import tempfile
from pathlib import Path
from instagrapi import Client
from instagrapi.exceptions import LoginRequired
import requests
from .models import User

BASE_DIR = Path(__file__).resolve().parent.parent
logger = logging.getLogger(__name__)
env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

class SessionManager:
    """
    Manages Instagram sessions using temporary files for deployed servers
    Session data flows: DB -> Temp file -> instagrapi -> DB -> Delete temp file
    """
    
    def __init__(self):
        """
        Initialize session manager for deployed environments
        Uses temporary files that are cleaned up after use
        """
        pass
    
    def create_temp_session_file(self, session_data: dict) -> str:
        """
        Create a temporary session file from session data
        
        Parameters
        ----------
        session_data: dict
            Session data from database
            
        Returns
        -------
        str
            Path to temporary session file
        """
        try:
            # Create temporary file with .json extension
            with tempfile.NamedTemporaryFile(mode='w', suffix='_session.json', delete=False) as temp_file:
                json.dump(session_data, temp_file, indent=2)
                temp_path = temp_file.name
            
            logger.info(f"Created temporary session file: {temp_path}")
            return temp_path
            
        except Exception as e:
            logger.error(f"Failed to create temporary session file: {str(e)}")
            raise e
    
    def load_session_from_db(self, client: Client, user: User) -> bool:
        """
        Load session from database using temporary file
        
        Parameters
        ----------
        client: Client
            Instagrapi client instance
        user: User
            Django user model instance
            
        Returns
        -------
        bool
            Success status
        """
        if not user.session_info:
            logger.info(f"No session info in database for user: {user.username}")
            return False
            
        temp_file_path = None
        try:
            # Create temporary session file from database data
            temp_file_path = self.create_temp_session_file(user.session_info)
            
            # Load session using instagrapi
            client.load_settings(temp_file_path)
            logger.info(f"Session loaded from database for user: {user.username}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load session for {user.username}: {str(e)}")
            return False
            
        finally:
            # Clean up temporary file
            if temp_file_path and os.path.exists(temp_file_path):
                try:
                    os.unlink(temp_file_path)
                    logger.debug(f"Cleaned up temporary session file: {temp_file_path}")
                except Exception as e:
                    logger.warning(f"Failed to clean up temp file {temp_file_path}: {e}")
    
    def save_session_to_db(self, client: Client, user: User) -> bool:
        """
        Save client session to database using temporary file
        
        Parameters
        ----------
        client: Client
            Instagrapi client instance
        user: User
            Django user model instance
            
        Returns
        -------
        bool
            Success status
        """
        temp_file_path = None
        try:
            # Create temporary file for session dump
            with tempfile.NamedTemporaryFile(mode='w', suffix='_session.json', delete=False) as temp_file:
                temp_file_path = temp_file.name
            
            # Dump session to temporary file
            client.dump_settings(temp_file_path)
            
            # Read session data from temporary file
            with open(temp_file_path, 'r') as f:
                session_data = json.load(f)
              # Save to database
            user.session_info = session_data
            user.save()
            
            logger.info(f"Session saved to database for user: {user.username}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save session for {user.username}: {str(e)}")
            return False
            
        finally:
            # Clean up temporary file
            if temp_file_path and os.path.exists(temp_file_path):
                try:
                    os.unlink(temp_file_path)
                    logger.debug(f"Cleaned up temporary session file: {temp_file_path}")
                except Exception as e:
                    logger.warning(f"Failed to clean up temp file {temp_file_path}: {e}")
    
    def login_user(self, username: str, password: str, user: User = None) -> Client:
        """
        Login user with session management using temporary files
        
        Parameters
        ----------
        username: str
            Instagram username
        password: str
            Instagram password
        user: User, optional
            Django user model instance
            
        Returns
        -------
        Client
            Authenticated instagrapi client
            
        Raises
        ------
        Exception
            If login fails completely
        """
        if user is None:
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                raise Exception(f"User {username} not found in database")
        
        client = Client()
        client.set_locale('id_ID')
        client.set_country('ID')
        client.set_country_code(62)
        client.set_timezone_offset(25200)  # UTC+7
        
        # Set common Indonesian device characteristics
        client.set_device({
            'manufacturer': random.choice(['samsung', 'oppo', 'vivo', 'xiaomi']),
            'model': random.choice(['SM-A325F', 'CPH2113', 'V2027', 'M2006C3LG']),
            'android_version': random.choice([28, 29, 30]),
            'android_release': random.choice(['9.0', '10.0', '11.0'])
        })
        
        # Add delays for more human-like behavior
        client.delay_range = [1, 3]
        client.set_proxy(env('PROXY_URL', default=None))
        
        login_via_session = False
        login_via_password = False
        
        # First, try to load existing session from database if available
        if user.session_info and self.load_session_from_db(client, user):
            try:
                # Try to login with existing session
                client.login(username, password)
                
                # Validate session by checking timeline
                try:
                    client.get_timeline_feed()
                    login_via_session = True
                    logger.info(f"Successfully logged in via existing session: {username}")
                except LoginRequired:
                    logger.info("Existing session is invalid, will try fresh login")
                    
            except Exception as e:
                logger.info(f"Couldn't login user using existing session: {str(e)}")
        
        # If no existing session or session login failed, try fresh Instagram login
        if not login_via_session:
            try:
                if user.session_info and 'uuids' in user.session_info:
                    client.set_uuids(user.session_info['uuids'])
                
                logger.info(f"Attempting fresh Instagram login: {username}")
                if client.login(username, password):
                    login_via_password = True
                    # Save the new session to database
                    self.save_session_to_db(client, user)
                    logger.info(f"Successfully logged in via password: {username}")
                    
            except Exception as e:
                logger.error(f"Instagram login failed for {username}: {str(e)}")
        
        # Check if any login method worked
        if not login_via_password and not login_via_session:
            raise Exception(f"Instagram login failed for {username}")
        
        return client
    
    def update_user_session_in_db(self, user: User, client: Client):
        """
        Update user's session info in database
        
        Parameters
        ----------
        user: User
            Django user model instance
        client: Client
            Authenticated instagrapi client
        """
        try:
            self.save_session_to_db(client, user)
            logger.info(f"Updated database session for user: {user.username}")
        except Exception as e:
            logger.error(f"Failed to update database session for {user.username}: {str(e)}")
    
    def clear_user_session(self, user: User) -> bool:
        """
        Clear user's session from database
        
        Parameters
        ----------
        user: User
            Django user model instance
            
        Returns
        -------
        bool
            Success status
        """
        try:
            user.session_info = None
            user.save()
            logger.info(f"Cleared session for user: {user.username}")
            return True
        except Exception as e:
            logger.error(f"Failed to clear session for {user.username}: {str(e)}")
            return False

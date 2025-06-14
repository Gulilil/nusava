from django.core.management.base import BaseCommand
from django.utils import timezone
from bot.models import InstagramStatistics, User
from instagrapi import Client
import os
from bot.bot import InstagramBot
import logging
import time
import signal
import sys
from datetime import datetime

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Update Instagram statistics for a specific user with optional scheduling'

    def __init__(self):
        super().__init__()
        self.running = True
        self.bot = None
        self.user = None

    def add_arguments(self, parser):
        parser.add_argument(
            'username',
            type=str,
            help='Instagram username to update statistics for'
        )
        parser.add_argument(
            'password',
            type=str,
            help='Instagram password for the user'
        )
        parser.add_argument(
            '--schedule',
            action='store_true',
            help='Run as scheduled job instead of one-time update'
        )
        parser.add_argument(
            '--hours',
            type=int,
            default=6,
            help='Update interval in hours when using --schedule (default: 6)'
        )

    def signal_handler(self, signum, frame):
        self.stdout.write("\nReceived interrupt signal. Stopping scheduler...")
        self.running = False
        sys.exit(0)

    def initialize_bot(self, username, password):
        """Initialize the bot and login once"""
        try:
            # Get user from database
            self.user = User.objects.get(username=username)
            self.stdout.write(f"[{datetime.now()}] Found user: {username}")
            
            # Initialize bot
            session_settings = self.user.session_info if self.user.session_info else None
            self.bot = InstagramBot(self.user, password, session_settings)
            self.stdout.write(f"[{datetime.now()}] Bot initialized and logged in successfully")
            
            return True
                
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f"[{datetime.now()}] User '{username}' not found in database")
            )
            return False
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"[{datetime.now()}] Error initializing bot: {str(e)}")
            )
            logger.error(f"Error initializing bot for {username}: {str(e)}")
            return False

    def update_single_stats(self):
        """Run a single statistics update using existing bot instance"""
        try:
            if not self.bot or not self.user:
                self.stdout.write(
                    self.style.ERROR(f"[{datetime.now()}] Bot not initialized. Please initialize first.")
                )
                return False
            
            # Get current statistics from Instagram
            current_stats = self.bot.get_account_statistics()
            self.stdout.write(f"[{datetime.now()}] Retrieved current statistics from Instagram")
            
            # Check if statistics already exist for this user
            try:
                existing_stats = InstagramStatistics.objects.get(user=self.user)
                self.stdout.write(f"[{datetime.now()}] Found existing statistics, comparing...")
                
                # Compare and set boolean flags
                new_followers = current_stats['followers_count'] > existing_stats.followers_count
                new_likes = current_stats['all_likes_count'] > existing_stats.all_likes_count
                new_comments = current_stats['all_comments_count'] > existing_stats.all_comments_count
                
                # Update existing statistics
                for key, value in current_stats.items():
                    setattr(existing_stats, key, value)
                
                existing_stats.new_followers = new_followers
                existing_stats.new_likes = new_likes
                existing_stats.new_comments = new_comments
                existing_stats.save()
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f"[{datetime.now()}] Updated statistics for {self.user.username}:\n"
                        f"  Followers: {existing_stats.followers_count} (New: {new_followers})\n"
                        f"  Total likes: {existing_stats.all_likes_count} (New: {new_likes})\n"
                        f"  Total comments: {existing_stats.all_comments_count} (New: {new_comments})"
                    )
                )
                
            except InstagramStatistics.DoesNotExist:
                # Create new statistics
                new_stats = InstagramStatistics.objects.create(
                    user=self.user,
                    new_followers=False,  # First time, so no comparison
                    new_likes=False,
                    new_comments=False,
                    **current_stats
                )
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f"[{datetime.now()}] Created new statistics for {self.user.username}:\n"
                        f"  Followers: {new_stats.followers_count}\n"
                        f"  Following: {new_stats.following_count}\n"
                        f"  Posts: {new_stats.posts_count}\n"
                        f"  Total likes: {new_stats.all_likes_count}\n"
                        f"  Total comments: {new_stats.all_comments_count}"
                    )
                )
            
            return True
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"[{datetime.now()}] Error updating statistics: {str(e)}")
            )
            logger.error(f"Error updating statistics for {self.user.username}: {str(e)}")
            return False

    def handle(self, *args, **options):
        username = options['username']
        password = options['password']
        schedule = options['schedule']
        hours = options['hours']
        
        # Initialize bot and login once at the beginning
        if not self.initialize_bot(username, password):
            self.stdout.write(self.style.ERROR("Failed to initialize bot. Exiting."))
            return
        
        if not schedule:
            # Run once and exit
            self.update_single_stats()
            return
        
        # Scheduled mode
        interval_seconds = hours * 3600  # Convert hours to seconds
        
        # Set up signal handler for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

        self.stdout.write(f"Starting Instagram statistics scheduler...")
        self.stdout.write(f"Username: {username}")
        self.stdout.write(f"Update interval: {hours} hours")
        self.stdout.write(f"Press Ctrl+C to stop\n")

        # Run initial update
        self.update_single_stats()

        # Schedule periodic updates
        while self.running:
            try:
                self.stdout.write(f"[{datetime.now()}] Waiting {hours} hours for next update...")
                time.sleep(interval_seconds)
                if self.running:
                    self.update_single_stats()
            except KeyboardInterrupt:
                break

        self.stdout.write("Scheduler stopped.")
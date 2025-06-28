from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone
from .persona import get_default_persona

class UserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError("The Username must be set")
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if not extra_fields.get('is_staff') or not extra_fields.get('is_superuser'):
            raise ValueError("Superuser must have is_staff=True and is_superuser=True")

        return self.create_user(username, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    id = models.BigAutoField(primary_key=True)
    username = models.CharField(max_length=100, unique=True)
    session_info = models.JSONField(blank=True, null=True)
    persona = models.JSONField(default=get_default_persona, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.username

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    def __str__(self):
        return self.username
    
# ActionLog model
class ActionLog(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='action_logs')
    action_type = models.CharField(max_length=50)
    target = models.TextField(blank=True)
    status = models.CharField(max_length=20)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.timestamp}] {self.user.username} - {self.action_type}"

# Configuration model
class Configuration(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='configurations')
    temperature = models.FloatField(default=0.3)
    top_k = models.IntegerField(default=10)
    max_token = models.IntegerField(default=4096)
    max_iteration = models.IntegerField(default=10)

    def __str__(self):
        return f"Configuration for {self.user.username}"
    
class InstagramStatistics(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='instagram_stats')
    
    # Account basic info
    followers_count = models.IntegerField(default=0)
    following_count = models.IntegerField(default=0)
    posts_count = models.IntegerField(default=0)
    all_likes_count = models.IntegerField(default=0)
    all_comments_count = models.IntegerField(default=0)

    # Account insights - Profile metrics
    profile_visits = models.IntegerField(default=0)
    profile_visits_delta = models.IntegerField(default=0)
    website_visits = models.IntegerField(default=0)
    website_visits_delta = models.IntegerField(default=0)
    
    # Content metrics
    impressions = models.IntegerField(default=0)
    impressions_delta = models.IntegerField(default=0)
    reach = models.IntegerField(null=True, blank=True)
    reach_delta = models.IntegerField(null=True, blank=True)

    # boolean metrics
    new_followers = models.IntegerField(default=0)
    new_comments = models.IntegerField(default=0)
    new_likes = models.IntegerField(default=0)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Instagram Statistics'
        verbose_name_plural = 'Instagram Statistics'
    
    def __str__(self):
        return f"{self.user.username} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
    
    @property
    def engagement_rate(self):
        """Calculate basic engagement rate if we have posts and followers"""
        if self.followers_count > 0 and self.posts_count > 0:
            # This is a simplified calculation
            return round((self.impressions / self.followers_count) * 100, 2) if self.impressions > 0 else 0
        return 0
    
class TourismObject(models.Model):
    OBJECT_TYPES = [
        ('hotel', 'Hotel'),
        ('destination', 'Destination'),
    ]
    
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    object_type = models.CharField(max_length=20, choices=OBJECT_TYPES)
    location = models.CharField(max_length=255)
    rating = models.FloatField(null=True, blank=True)
    image_url = models.URLField(blank=True)
    def __str__(self):
        return f"{self.name} ({self.object_type})"
    
class Posts(models.Model):
    """Model to store actual posted Instagram content"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    tourism_object = models.ForeignKey(TourismObject, on_delete=models.CASCADE, related_name='posts')
    media_id = models.CharField(max_length=100, unique=True)  # Instagram media pk
    shortcode = models.CharField(max_length=50, unique=True)  # Instagram shortcode
    caption = models.TextField()
    like_count = models.IntegerField(default=0)  # Current like count
    comment_count = models.IntegerField(default=0)  # Current comment count
    posted_at = models.DateTimeField()  # When posted on Instagram
    created_at = models.DateTimeField(auto_now_add=True)  # When record was created
    updated_at = models.DateTimeField(auto_now=True)  # When record was last updated
    
    class Meta:
        ordering = ['-posted_at']
        indexes = [
            models.Index(fields=['user', 'tourism_object']),
            models.Index(fields=['media_id']),
            models.Index(fields=['shortcode']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.shortcode} ({self.tourism_object.name})"

class PostStatistics(models.Model):
    """Historical statistics for posts linked to tourism objects"""
    tourism_object = models.ForeignKey(TourismObject, on_delete=models.CASCADE, related_name='post_statistics')
    post = models.ForeignKey(Posts, on_delete=models.CASCADE, related_name='statistics')
    like_count = models.IntegerField(default=0)
    comment_count = models.IntegerField(default=0)
    recorded_at = models.DateTimeField(auto_now_add=True)
    
    # Track changes since last snapshot
    likes_change = models.IntegerField(default=0)
    comments_change = models.IntegerField(default=0)
    
    class Meta:
        unique_together = ['post', 'recorded_at']
        ordering = ['-recorded_at']
        indexes = [
            models.Index(fields=['tourism_object', 'recorded_at']),
            models.Index(fields=['post', 'recorded_at']),
        ]
    
    def __str__(self):
        return f"{self.tourism_object.name} - {self.post.shortcode} ({self.recorded_at})"

class ScheduledPost(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='scheduled_posts')
    scheduled_time = models.DateTimeField()
    reason = models.TextField()
    image_url = models.TextField()
    caption = models.TextField()
    is_posted = models.BooleanField(default=False)
    tourism_object = models.ForeignKey(TourismObject, on_delete=models.CASCADE, null=True, blank=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['scheduled_time']
        verbose_name = 'Scheduled Post'
        verbose_name_plural = 'Scheduled Posts'
    
    def __str__(self):
        return f"{self.user.username} - {self.scheduled_time.strftime('%Y-%m-%d %H:%M')} - {'Posted' if self.is_posted else 'Pending'}"
    
    @property
    def is_overdue(self):
        """Check if the scheduled time has passed and post is not yet posted"""
        return timezone.now() > self.scheduled_time and not self.is_posted

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Administrator'),
        ('editor', 'Editor'),
        ('publisher', 'Publisher'),
        ('analyst', 'Analyst'),
    )

    email = models.EmailField(_('email address'), unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='editor')
    linkedin_token = models.CharField(max_length=255, blank=True, null=True)
    linkedin_token_expires_at = models.DateTimeField(null=True, blank=True)
    linkedin_profile_id = models.CharField(max_length=100, blank=True, null=True)
    linkedin_profile_url = models.URLField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    bio = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def __str__(self):
        return self.email

    @property
    def is_admin(self):
        return self.role == 'admin'

    @property
    def is_editor(self):
        return self.role == 'editor'

    @property
    def is_publisher(self):
        return self.role == 'publisher'

    @property
    def is_analyst(self):
        return self.role == 'analyst'

    def has_article_permission(self, article, action):
        if self.is_admin:
            return True
        
        if action == 'view':
            return True
        
        if action == 'create':
            return self.is_editor or self.is_publisher
        
        if action == 'edit':
            return (self.is_editor and article.author == self) or self.is_publisher
        
        if action == 'publish':
            return self.is_publisher
        
        return False

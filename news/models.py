from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from django.utils import timezone
from django.core.exceptions import ValidationError

def validate_image_size(image):
    file_size = image.size
    max_size = 50 * 1024  # 50KB
    if file_size > max_size:
        raise ValidationError(f"Maximum file size allowed is 50KB. Current file size is {file_size/1024:.1f}KB")

User = get_user_model()

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class Article(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('review', 'In Review'),
        ('published', 'Published'),
    )

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    content = models.TextField()
    excerpt = models.TextField(blank=True)
    featured_image = models.ImageField(
        upload_to='articles/images/%Y/%m/',
        validators=[validate_image_size],
        help_text='Maximum file size allowed is 50KB',
        blank=True,
        null=True
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='articles')
    categories = models.ManyToManyField(Category, related_name='articles')
    tags = models.ManyToManyField(Tag, related_name='articles', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)
    ai_enhanced = models.BooleanField(default=False)
    linkedin_published = models.BooleanField(default=False)
    linkedin_post_id = models.CharField(max_length=100, blank=True, null=True)
    view_count = models.PositiveIntegerField(default=0)
    likes = models.ManyToManyField(User, through='ArticleLike', related_name='liked_articles')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        if self.status == 'published' and not self.published_at:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)

    @property
    def like_count(self):
        return self.article_likes.count()

class ArticleLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='article_likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'article')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} likes {self.article.title}"

class ContentVersion(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='versions')
    content = models.TextField()
    version_number = models.PositiveIntegerField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_ai_enhanced = models.BooleanField(default=False)
    ai_parameters = models.JSONField(blank=True, null=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ['article', 'version_number']

    def __str__(self):
        return f"{self.article.title} - Version {self.version_number}"

class ArticleAnalytics(models.Model):
    article = models.OneToOneField(Article, on_delete=models.CASCADE, related_name='analytics')
    views = models.PositiveIntegerField(default=0)
    linkedin_views = models.PositiveIntegerField(default=0)
    linkedin_likes = models.PositiveIntegerField(default=0)
    linkedin_comments = models.PositiveIntegerField(default=0)
    linkedin_shares = models.PositiveIntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Analytics for {self.article.title}"

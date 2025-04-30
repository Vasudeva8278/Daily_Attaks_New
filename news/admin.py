from django.contrib import admin
from .models import Article, Category, Tag, ContentVersion, ArticleAnalytics

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'created_at')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'created_at')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}

class ContentVersionInline(admin.TabularInline):
    model = ContentVersion
    extra = 0
    readonly_fields = ('version_number', 'created_by', 'created_at', 'is_ai_enhanced')
    can_delete = False

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'status', 'created_at', 'published_at', 'ai_enhanced')
    list_filter = ('status', 'ai_enhanced', 'categories', 'tags', 'created_at')
    search_fields = ('title', 'content', 'excerpt')
    prepopulated_fields = {'slug': ('title',)}
    raw_id_fields = ('author', 'categories', 'tags')
    date_hierarchy = 'created_at'
    inlines = [ContentVersionInline]
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing an existing object
            return ('created_at', 'updated_at', 'published_at')
        return ()

@admin.register(ArticleAnalytics)
class ArticleAnalyticsAdmin(admin.ModelAdmin):
    list_display = ('article', 'views', 'linkedin_views', 'linkedin_likes', 'last_updated')
    readonly_fields = ('article', 'views', 'linkedin_views', 'linkedin_likes',
                      'linkedin_comments', 'linkedin_shares', 'last_updated')
    search_fields = ('article__title',)

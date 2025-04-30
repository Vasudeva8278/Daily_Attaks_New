from rest_framework import serializers
from news.models import Article, Category, Tag, ContentVersion, ArticleAnalytics
from users.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'role', 'first_name', 'last_name', 
                 'profile_picture', 'bio', 'linkedin_profile_url']
        read_only_fields = ['id', 'role']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description']
        read_only_fields = ['id', 'slug']

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug']
        read_only_fields = ['id', 'slug']

class ContentVersionSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)

    class Meta:
        model = ContentVersion
        fields = ['id', 'content', 'version_number', 'created_by', 
                 'created_at', 'is_ai_enhanced', 'ai_parameters']
        read_only_fields = ['id', 'version_number', 'created_by', 'created_at']

class ArticleAnalyticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArticleAnalytics
        fields = ['views', 'linkedin_views', 'linkedin_likes', 
                 'linkedin_comments', 'linkedin_shares', 'last_updated']
        read_only_fields = fields

class AIEnhancementParametersSerializer(serializers.Serializer):
    tone = serializers.ChoiceField(
        choices=['professional', 'casual', 'formal', 'technical', 'conversational'],
        required=False,
        default='professional'
    )
    length = serializers.ChoiceField(
        choices=['short', 'medium', 'long'],
        required=False,
        default='medium'
    )
    target_audience = serializers.ChoiceField(
        choices=['general', 'technical', 'business', 'academic'],
        required=False,
        default='general'
    )
    style = serializers.ChoiceField(
        choices=['news', 'blog', 'report', 'analysis'],
        required=False,
        default='news'
    )

class HeadlineGenerationParametersSerializer(serializers.Serializer):
    style = serializers.ChoiceField(
        choices=['news', 'blog', 'social', 'seo'],
        required=False,
        default='news'
    )

class ArticleSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    categories = CategorySerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    versions = ContentVersionSerializer(many=True, read_only=True)
    analytics = ArticleAnalyticsSerializer(read_only=True)
    category_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    tag_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )

    class Meta:
        model = Article
        fields = ['id', 'title', 'slug', 'content', 'excerpt', 'featured_image',
                 'status', 'author', 'categories', 'tags', 'created_at', 'updated_at',
                 'published_at', 'ai_enhanced', 'linkedin_published', 'linkedin_post_id',
                 'versions', 'analytics', 'category_ids', 'tag_ids']
        read_only_fields = ['id', 'slug', 'author', 'created_at', 'updated_at',
                          'published_at', 'linkedin_post_id']

    def create(self, validated_data):
        category_ids = validated_data.pop('category_ids', [])
        tag_ids = validated_data.pop('tag_ids', [])
        
        article = Article.objects.create(**validated_data)
        
        if category_ids:
            article.categories.set(category_ids)
        if tag_ids:
            article.tags.set(tag_ids)
        
        return article

    def update(self, instance, validated_data):
        category_ids = validated_data.pop('category_ids', None)
        tag_ids = validated_data.pop('tag_ids', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        if category_ids is not None:
            instance.categories.set(category_ids)
        if tag_ids is not None:
            instance.tags.set(tag_ids)
        
        instance.save()
        return instance

class ArticleListSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    categories = CategorySerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)

    class Meta:
        model = Article
        fields = ['id', 'title', 'slug', 'excerpt', 'featured_image', 'status',
                 'author', 'categories', 'tags', 'created_at', 'published_at'] 
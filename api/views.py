from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from news.models import Article, Category, Tag, ContentVersion, ArticleAnalytics
from users.models import User
from .serializers import (
    ArticleSerializer, ArticleListSerializer, CategorySerializer,
    TagSerializer, UserSerializer, ContentVersionSerializer
)
from news.ai_integration import GeminiIntegration
from django.utils import timezone

class ArticleViewSet(viewsets.ModelViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'author', 'categories', 'tags', 'ai_enhanced']
    search_fields = ['title', 'content', 'excerpt']
    ordering_fields = ['created_at', 'updated_at', 'published_at']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return ArticleListSerializer
        return ArticleSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        article = self.get_object()
        if not request.user.has_article_permission(article, 'publish'):
            return Response(
                {'error': 'You do not have permission to publish this article'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        article.status = 'published'
        article.save()
        return Response({'status': 'published'})

    @action(detail=True, methods=['post'])
    def enhance_with_ai(self, request, pk=None):
        article = self.get_object()
        if not request.user.has_article_permission(article, 'edit'):
            return Response(
                {'error': 'You do not have permission to edit this article'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            gemini = GeminiIntegration()
            
            # Get enhancement parameters from request
            parameters = request.data.get('parameters', {})
            
            # Enhance content
            result = gemini.enhance_content(article.content, parameters)
            
            if not result['success']:
                return Response(
                    {'error': result['error']},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            # Create new content version
            version_number = article.versions.count() + 1
            ContentVersion.objects.create(
                article=article,
                content=result['content'],
                version_number=version_number,
                created_by=request.user,
                is_ai_enhanced=True,
                ai_parameters=parameters
            )
            
            # Update article
            article.content = result['content']
            article.ai_enhanced = True
            article.updated_at = timezone.now()
            article.save()
            
            return Response({
                'status': 'enhanced',
                'version_number': version_number,
                'parameters': parameters,
                'original_length': result['original_length'],
                'enhanced_length': result['enhanced_length']
            })
            
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': f'AI enhancement failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'])
    def generate_headline(self, request, pk=None):
        article = self.get_object()
        if not request.user.has_article_permission(article, 'edit'):
            return Response(
                {'error': 'You do not have permission to edit this article'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            gemini = GeminiIntegration()
            style = request.data.get('style', 'news')
            
            result = gemini.generate_headline(article.content, style)
            
            if not result['success']:
                return Response(
                    {'error': result['error']},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            return Response({
                'headline': result['headline'],
                'style': style
            })
            
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': f'Headline generation failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'])
    def publish_to_linkedin(self, request, pk=None):
        article = self.get_object()
        if not request.user.has_article_permission(article, 'publish'):
            return Response(
                {'error': 'You do not have permission to publish this article'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # TODO: Implement LinkedIn API integration
        return Response({'status': 'LinkedIn publishing not implemented yet'})

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]

class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.IsAuthenticated]

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.action in ['create', 'retrieve']:
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_object(self):
        if self.kwargs.get('pk') == 'me':
            return self.request.user
        return super().get_object()

    @action(detail=False, methods=['get'])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

class ContentVersionViewSet(viewsets.ModelViewSet):
    queryset = ContentVersion.objects.all()
    serializer_class = ContentVersionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        article_id = self.kwargs.get('article_pk')
        if article_id:
            return ContentVersion.objects.filter(article_id=article_id)
        return ContentVersion.objects.none()

    def perform_create(self, serializer):
        article = get_object_or_404(Article, pk=self.kwargs.get('article_pk'))
        serializer.save(article=article, created_by=self.request.user)

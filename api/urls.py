from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .views import (
    ArticleViewSet, CategoryViewSet, TagViewSet,
    UserViewSet, ContentVersionViewSet
)
from .serializers import (
    AIEnhancementParametersSerializer,
    HeadlineGenerationParametersSerializer
)

# Swagger documentation for AI enhancement endpoints
enhance_with_ai_schema = swagger_auto_schema(
    method='post',
    request_body=AIEnhancementParametersSerializer,
    responses={
        200: openapi.Response(
            description='Content enhanced successfully',
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'status': openapi.Schema(type=openapi.TYPE_STRING),
                    'version_number': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'parameters': openapi.Schema(type=openapi.TYPE_OBJECT),
                    'original_length': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'enhanced_length': openapi.Schema(type=openapi.TYPE_INTEGER),
                }
            )
        ),
        400: 'Invalid parameters',
        403: 'Permission denied',
        500: 'AI enhancement failed'
    }
)

generate_headline_schema = swagger_auto_schema(
    method='post',
    request_body=HeadlineGenerationParametersSerializer,
    responses={
        200: openapi.Response(
            description='Headline generated successfully',
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'headline': openapi.Schema(type=openapi.TYPE_STRING),
                    'style': openapi.Schema(type=openapi.TYPE_STRING),
                }
            )
        ),
        400: 'Invalid parameters',
        403: 'Permission denied',
        500: 'Headline generation failed'
    }
)

# Apply schemas to view methods
ArticleViewSet.enhance_with_ai = enhance_with_ai_schema(ArticleViewSet.enhance_with_ai)
ArticleViewSet.generate_headline = generate_headline_schema(ArticleViewSet.generate_headline)

router = DefaultRouter()
router.register(r'articles', ArticleViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'tags', TagViewSet)
router.register(r'users', UserViewSet)

# Nested router for content versions
articles_router = DefaultRouter()
articles_router.register(r'versions', ContentVersionViewSet, basename='article-versions')

urlpatterns = [
    path('', include(router.urls)),
    path('articles/<int:article_pk>/', include(articles_router.urls)),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
] 
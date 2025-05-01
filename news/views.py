from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q, F
from django.http import JsonResponse
from django.urls import reverse
from django.views.decorators.http import require_POST
from .models import Article, Category, Tag, ArticleLike
from .forms import ArticleForm

def home(request):
    featured_articles = Article.objects.filter(status='published').order_by('-created_at')[:3]
    return render(request, 'home.html', {'featured_articles': featured_articles})

def article_list(request):
    # Get filters from request
    category_slug = request.GET.get('category')
    tag_slug = request.GET.get('tag')
    search_query = request.GET.get('search')
    
    # Start with published articles
    articles = Article.objects.filter(status='published').order_by('-created_at')
    
    # Apply filters
    if category_slug:
        articles = articles.filter(categories__slug=category_slug)
    if tag_slug:
        articles = articles.filter(tags__slug=tag_slug)
    if search_query:
        articles = articles.filter(
            Q(title__icontains=search_query) |
            Q(content__icontains=search_query) |
            Q(excerpt__icontains=search_query)
        )
    
    # Get liked articles for the current user
    user_liked_articles = []
    if request.user.is_authenticated:
        user_liked_articles = ArticleLike.objects.filter(
            user=request.user,
            article__in=articles
        ).values_list('article_id', flat=True)
    
    # Pagination
    paginator = Paginator(articles, 10)  # 10 articles per page
    page = request.GET.get('page')
    articles = paginator.get_page(page)
    
    # Get all categories and tags for filters
    categories = Category.objects.all()
    tags = Tag.objects.all()
    
    context = {
        'articles': articles,
        'categories': categories,
        'tags': tags,
        'user_liked_articles': user_liked_articles,
        'selected_category': category_slug,
        'selected_tag': tag_slug,
        'search_query': search_query,
    }
    return render(request, 'articles/list.html', context)

def article_detail(request, pk):
    article = get_object_or_404(Article, pk=pk)
    
    # Increment view count
    Article.objects.filter(pk=pk).update(view_count=F('view_count') + 1)
    article.refresh_from_db()  # Refresh to get updated view count
    
    # Check if user has liked the article
    user_has_liked = False
    if request.user.is_authenticated:
        user_has_liked = ArticleLike.objects.filter(
            user=request.user,
            article=article
        ).exists()
    
    context = {
        'article': article,
        'user_has_liked': user_has_liked,
    }
    return render(request, 'articles/detail.html', context)

@login_required
@require_POST
def like_article(request, pk):
    article = get_object_or_404(Article, pk=pk)
    like, created = ArticleLike.objects.get_or_create(
        user=request.user,
        article=article
    )
    
    if not created:
        # User already liked, so unlike
        like.delete()
        liked = False
    else:
        liked = True
    
    # Get updated like count
    article.refresh_from_db()
    
    return JsonResponse({
        'success': True,
        'liked': liked,
        'like_count': article.like_count
    })

@login_required
def article_create(request):
    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                article = form.save(commit=False)
                article.author = request.user
                article.save()
                form.save_m2m()  # Save many-to-many relationships
                
                # Use reverse to generate the correct URL
                redirect_url = reverse('article_detail', kwargs={'pk': article.pk})
                
                return JsonResponse({
                    'success': True,
                    'message': 'Article created successfully!',
                    'redirect_url': redirect_url
                })
            except Exception as e:
                print(f"Error creating article: {str(e)}")  # Debug print
                return JsonResponse({
                    'success': False,
                    'error': 'Error creating article. Please try again.'
                }, status=500)
        else:
            print(f"Form errors: {form.errors}")  # Debug print
            errors = {field: str(error[0]) for field, error in form.errors.items()}
            return JsonResponse({
                'success': False,
                'error': 'Please correct the form errors.',
                'field_errors': errors
            }, status=400)
    
    form = ArticleForm()
    context = {
        'form': form,
        'categories': Category.objects.all(),
        'tags': Tag.objects.all(),
    }
    return render(request, 'articles/form.html', context)

@login_required
def article_edit(request, pk):
    article = get_object_or_404(Article, pk=pk)
    
    # Check if user has permission to edit
    if not request.user.is_staff and article.author != request.user:
        return redirect('article_detail', pk=article.pk)
    
    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES, instance=article)
        if form.is_valid():
            article = form.save()
            form.save_m2m()  # Save many-to-many relationships
            return redirect('article_detail', pk=article.pk)
    else:
        form = ArticleForm(instance=article)
    
    categories = Category.objects.all()
    tags = Tag.objects.all()
    
    context = {
        'article': article,
        'form': form,
        'categories': categories,
        'tags': tags,
    }
    return render(request, 'articles/form.html', context)

def category_list(request):
    categories = Category.objects.all().order_by('name')
    for category in categories:
        category.article_count = category.articles.count()
    
    context = {
        'categories': categories,
    }
    return render(request, 'articles/categories.html', context)

def tag_list(request):
    tags = Tag.objects.all().order_by('name')
    
    # Calculate tag weights based on article count
    max_count = max((tag.articles.count() for tag in tags), default=1)
    min_count = min((tag.articles.count() for tag in tags), default=1)
    
    for tag in tags:
        count = tag.articles.count()
        # Calculate weight between 0.8 and 2.0 based on article count
        if max_count == min_count:
            tag.weight = 1.0
        else:
            tag.weight = 0.8 + (count - min_count) * 1.2 / (max_count - min_count)
    
    context = {
        'tags': tags,
    }
    return render(request, 'articles/tags.html', context)
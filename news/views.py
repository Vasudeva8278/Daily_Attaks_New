from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Article, Category, Tag
from .forms import ArticleForm

def home(request):
    """Render the home page with featured content."""
    featured_articles = Article.objects.filter(status='published').order_by('-created_at')[:3]
    categories = Category.objects.all()[:6]
    tags = Tag.objects.all()[:10]
    
    context = {
        'featured_articles': featured_articles,
        'categories': categories,
        'tags': tags,
    }
    return render(request, 'news/home.html', context)

def article_list(request):
    # Get filter parameters
    category_slug = request.GET.get('category')
    tag_id = request.GET.get('tag')
    search = request.GET.get('search')
    sort = request.GET.get('sort', '-created_at')
    
    # Get all articles
    articles = Article.objects.all()
    
    # Apply filters
    if category_slug:
        articles = articles.filter(categories__slug=category_slug)
    if tag_id:
        articles = articles.filter(tags__id=tag_id)
    if search:
        articles = articles.filter(
            Q(title__icontains=search) |
            Q(content__icontains=search) |
            Q(excerpt__icontains=search)
        )
    
    # Apply sorting
    articles = articles.order_by(sort)
    
    # Pagination
    paginator = Paginator(articles, 10)
    page = request.GET.get('page')
    articles = paginator.get_page(page)
    
    # Get all categories and tags for filters
    categories = Category.objects.all()
    tags = Tag.objects.all()
    
    context = {
        'articles': articles,
        'categories': categories,
        'tags': tags,
    }
    return render(request, 'articles/list.html', context)

def article_detail(request, pk):
    article = get_object_or_404(Article, pk=pk)
    context = {
        'article': article,
    }
    return render(request, 'articles/detail.html', context)

@login_required
def article_create(request):
    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES)
        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user
            article.save()
            form.save_m2m()  # Save many-to-many relationships
            return redirect('article_detail', pk=article.pk)
    else:
        form = ArticleForm()
    
    categories = Category.objects.all()
    tags = Tag.objects.all()
    
    context = {
        'form': form,
        'categories': categories,
        'tags': tags,
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
    """Render the categories page."""
    categories = Category.objects.all().order_by('name')
    for category in categories:
        category.article_count = category.articles.count()
    
    context = {
        'categories': categories,
    }
    return render(request, 'articles/categories.html', context)

def tag_list(request):
    """Render the tags page."""
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
from django.shortcuts import get_object_or_404, render, redirect
from django.core.paginator import Paginator
from .models import Group, Post, User, Follow
from .forms import PostForm, CommentForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page


POSTS_PER_PAGE = 10  # Number of posts per page


@cache_page(20, key_prefix='index_page')
def index(request):
    '''главная страница,
    кеш 20 сек
    '''
    template = 'posts/index.html'
    post_list = Post.objects.all()
    paginator = Paginator(post_list, POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, template, context)


def group_posts(request, slug):
    '''страница группы'''
    group = get_object_or_404(Group, slug=slug)
    template = 'posts/group_list.html'
    post_list = Post.objects.filter(group=group)
    paginator = Paginator(post_list, POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def profile(request, username):
    '''страница автора'''
    profile = get_object_or_404(User, username=username)
    template = 'posts/profile.html'
    post = Post.objects.filter(author=profile)
    paginator = Paginator(post, POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    following = (request.user.is_authenticated and profile != request.user
                 and Follow.objects.filter(
                     user=request.user, author=profile).exists())
    context = {
        'profile': profile,
        'page_obj': page_obj,
        'following': following,
    }
    return render(request, template, context)


def post_detail(request, post_id):
    '''страница поста'''
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm()
    comments = post.comments.all()

    context = {
        'post': post,
        'form': form,
        'comments': comments,
    }
    template = 'posts/post_detail.html'
    return render(request, template, context)


@login_required
def post_create(request):
    '''Добавить пост'''
    template = 'posts/create_post.html'
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
    )
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', request.user)
    context = {
        'form': form,
    }
    return render(request, template, context)


@login_required
def post_edit(request, post_id):
    '''редактировать пост'''
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect(
            'posts:post_detail', post_id
        )
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        form.save()
        return redirect(
            'posts:post_detail', post_id
        )
    template = 'posts/create_post.html'
    context = {
        'form': form,
        'is_edit': True,
        'post': post,
    }
    return render(request, template, context)


@login_required
def add_comment(request, post_id):
    '''Добавить комментарий'''
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    template = 'posts:post_detail'
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect(template, post_id=post_id)


@login_required
def follow_index(request):
    '''Просмотр подписок(лента)'''
    post_list = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(post_list, POSTS_PER_PAGE)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    template = 'posts/follow.html'
    context = {
        'page_obj': page_obj,
    }
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    """Подписаться на автора"""
    author = get_object_or_404(User, username=username)
    is_folower = Follow.objects.filter(user=request.user, author=author)
    if request.user != author and not is_folower.exists():
        Follow.objects.create(user=request.user, author=author)
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    """Отписаться от автора"""
    author = get_object_or_404(User, username=username)
    Follow.objects.filter(user=request.user, author=author).delete()

    return redirect('posts:follow_index')

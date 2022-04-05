from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from yatube.settings import ENTRIES_PER_PAGE

from .forms import CommentForm, PostForm
from .models import Comment, Follow, Group, Post


def get_page_context(queryset, request):
    paginator = Paginator(queryset, ENTRIES_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return {
        'page_obj': page_obj,
    }


def index(request):
    context = get_page_context(Post.objects.all(), request)
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    context = {
        'group': group,
    }
    context.update(get_page_context(group.posts.all(), request))
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    # Здесь код запроса к модели и создание словаря контекста
    profile = get_object_or_404(User, username=username)
    posts_count = profile.posts.count()
    following = False
    if request.user.is_authenticated:
        following = Follow.objects.filter(
            user=request.user, author=profile).exists()
    context = {
        'posts_count': posts_count,
        'profile': profile,
        'following': following
    }
    context.update(get_page_context(profile.posts.all(), request))
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    # Здесь код запроса к модели и создание словаря контекста
    post = get_object_or_404(Post, pk=post_id)
    posts_count = post.author.posts.count()
    form = CommentForm()
    context = {
        'posts_count': posts_count,
        'post': post,
        'post_id': post_id,
        'form': form,
    }
    context.update(get_page_context(
        post.comments.select_related('author'),
        request
    ))
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_delete(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.user == post.author:
        post.delete()
    return redirect('posts:profile', username=request.user.username)


@login_required
def post_create(request):
    form = PostForm(
        request.POST or None,
        files=request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', username=request.user.username)
    return render(request, 'posts/create_post.html', {'form': form})


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.user != post.author:
        return redirect('posts:post_detail', post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id=post_id)
    return render(request, 'posts/create_post.html',
                  {'form': form, 'is_edit': True})


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id)


@login_required
def delete_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    if request.user == comment.author:
        comment.delete()
    return redirect('posts:post_detail', post_id)


@login_required
def follow_index(request):
    context = get_page_context(Post.objects.filter(
        author__following__user=request.user),
        request
    )
    return render(request, 'posts/follow.html', context)


@login_required
def profile_to_follow(request, username):
    following_user = get_object_or_404(User, username=username)
    user = request.user
    if user != following_user:
        Follow.objects.get_or_create(
            user=user,
            author=following_user
        )
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    user = request.user
    author = get_object_or_404(User, username=username)
    check_follow = Follow.objects.filter(user=user, author=author)
    if check_follow.exists():
        check_follow.delete()
    return redirect('posts:profile', username=username)

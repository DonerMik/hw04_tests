from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required

from .forms import PostForm
from .models import Group, Post

User = get_user_model()


def paginator_post(posts_list, request):
    paginator = Paginator(posts_list, settings.COUNT_IN_PAGES)
    page_number = request.GET.get('page')
    # Получаем набор записей для страницы с запрошенным номером
    page_obj = paginator.get_page(page_number)
    return page_obj


def index(request):
    post_list = Post.objects.all()
    page_obj = paginator_post(post_list, request)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts_list = group.posts.all()
    page_obj = paginator_post(posts_list, request)
    template = 'posts/group_list.html'
    context = {
        'posts': posts_list,
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def profile(request, username):
    user = get_object_or_404(User, username=username)
    all_posts_user = user.posts.all()
    page_obj = paginator_post(all_posts_user, request)
    template = 'posts/profile.html'
    context = {
        'page_obj': page_obj,
        'author': user,
        'all_posts_user': all_posts_user,
    }
    return render(request, template, context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    count_post = post.author.posts.all().count()
    context = {
        'post': post,
        'count_post': count_post,
    }
    return render(request, 'posts/post_detail.html', context)

@login_required()
def post_create(request):
    form = PostForm(request.POST or None)
    if form.is_valid():
        instance = form.save(commit=False)
        instance.author = request.user
        instance.save()
        return redirect('posts:profile', instance.author)
    context = {
        'form': form,
        'is_edit': False
    }
    return render(request, 'posts/create_post.html', context)


def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    user = request.user
    if post.author != user:
        return redirect('posts:post_detail', post_id)

    form = PostForm(request.POST or None, instance=post)
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id)

    context = {
        'form': form,
        'is_edit': True,
        'post_id': post_id
    }
    return render(request, 'posts/create_post.html', context)

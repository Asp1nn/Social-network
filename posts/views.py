from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from posts import setting
from .models import Post, Group, User, Follow
from .forms import CommentForm, PostForm


def index(request):
    post_list = Post.objects.all()
    paginator = Paginator(post_list, setting.POST_COUNT)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request,
        'index.html',
        {'page': page, }
    )


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    paginator = Paginator(post_list, setting.POST_COUNT)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'group.html', {
        'group': group,
        'page': page,
    })


@login_required
def new_post(request):
    form = PostForm(request.POST or None)
    if not form.is_valid():
        return render(request, "new.html", {
            "form": form,
        })
    post = form.save(commit=False)
    post.author = request.user
    post.save()
    return redirect(reverse('posts:index'))


def profile(request, username):
    post_count_five = 5
    author = get_object_or_404(User, username=username)
    posts = author.posts.all()
    following = False
    if request.user.is_authenticated:
        following = Follow.objects.filter(
            user=request.user, author=author).exists()
    paginator = Paginator(posts, post_count_five)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'profile.html',
                  {'page': page,
                   'author': author,
                   'following': following,
                   }
                  )


def post_view(request, username, post_id):
    post = get_object_or_404(Post, author__username=username, id=post_id)
    form = CommentForm()
    return render(request, 'post.html', {
        'post': post,
        'author': post.author,
        'form': form,
        'comments': post.comments.all()
    })


@login_required
def post_edit(request, username, post_id):
    if username != request.user.username:
        return redirect('posts:post', username=username, post_id=post_id)
    post = get_object_or_404(Post, pk=post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    context = {
        'form': form,
        'post': post
    }
    if not form.is_valid():
        return render(request, 'new.html', context=context)
    form.save()
    return redirect('posts:post', username=username, post_id=post_id)


@login_required
def add_comment(request, username, post_id):
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post_id = post_id
        comment.author = request.user
        comment.save()
        return redirect('posts:post', username, post_id)
    return redirect('posts:post', username, post_id)


@login_required
def follow_index(request):
    follow = Follow.objects.filter(user=request.user)
    authors = []
    for obj in follow:
        authors.append(obj.author)
    post_list = Post.objects.filter(author__in=authors)
    paginator = Paginator(post_list, setting.POST_COUNT)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, "follow.html", {'page': page})


@login_required
def profile_follow(request, username):
    user = get_object_or_404(User, username=username)
    if (request.user != user and not Follow.objects.filter(
                user=request.user, author=user).exists()):
        Follow.objects.create(user=request.user, author=user)
        return redirect('posts:profile', username=username)
    return redirect('posts:follow_index')


@login_required
def profile_unfollow(request, username):
    user = get_object_or_404(User, username=username)
    if (request.user != user and Follow.objects.filter(
            user=request.user, author=user).exists()):
        Follow.objects.filter(user=request.user, author=user).delete()
        return redirect('posts:profile', username=username)
    return redirect('posts:follow_index')


def page_not_found(request, exception):
    return render(
        request,
        "misc/404.html",
        {"path": request.path},
        status=404
    )


def server_error(request):
    return render(request, "misc/500.html", status=500)

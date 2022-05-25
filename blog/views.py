from os import execv
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from blog.models import BlogPost, Category, EditRequest, Notification, Comment
from blog.forms import CreateBlogPostForm, UpdateBlogPostForm, CreateCommentForm, CreateEditRequestForm, CreateReportForm
from account.models import Account
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from operator import attrgetter

POSTS_PER_PAGE = 10

def create_blog_view(request):
    context = {}

    user = request.user
    if not user.is_authenticated:
        return redirect('must-authenticate')
    
    if request.POST:
        form = CreateBlogPostForm(request.POST, request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            author = user
            obj.author = author
            obj.save()
            user.loyalty_points = user.loyalty_points + 10
            user.save()
            return redirect('home')
        else:
            print("asdasdasd")
    else:
        form = CreateBlogPostForm()
              
    context['form'] = form
    return render(request, 'blog/create_post.html', context)


def delete_post_view(request,slug):
    post = BlogPost.objects.get(slug=slug)
    post.delete()

    return redirect('home')


def detail_post_view(request, slug):
    context = {}
    
    if not request.user.is_authenticated:
        return redirect('must-authenticate')

    blog_post = get_object_or_404(BlogPost, slug=slug)
    blog_post.views = blog_post.views + 1
    blog_post.save()
    likes_count = blog_post.total_likes
    unlikes_count = blog_post.total_unlikes
    context['blog_post'] = blog_post
    context['likes_count'] = likes_count
    context['unlikes_count'] = unlikes_count
    

    return render(request, 'blog/detail_post.html', context)


def edit_blog_view(request, slug):
    context = {}

    user = request.user
    if not user.is_authenticated:
        return redirect('must-authenticate')

    blog_post = get_object_or_404(BlogPost, slug=slug)

    if blog_post.author != user:
        return HttpResponse("<h1 class='display-2'>You are not the author of that post.</h1>")

    if request.POST:
        form = UpdateBlogPostForm(request.POST or None, instance=blog_post)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.save()
            context['success_message'] = "Successfully Updated"
            blog_post = obj
            return redirect('detail-post', blog_post.slug)

    form = UpdateBlogPostForm(
        initial= {
            "title" : blog_post.title,
            "body" : blog_post.body,
            "category" : blog_post.category,
            "header_image" : blog_post.header_image,
            "video" : blog_post.video
        }
    )            

    context['form'] = form
    return render(request, 'blog/edit_post.html', context)


def get_blog_queryset(query=None):
    queryset = []
    queries = query.split(" ")
    for q in queries:
        posts = BlogPost.objects.filter(
            Q(title__icontains=q),
            Q(body__icontains=q),
        ).distinct()

        for post in posts:
            queryset.append(post)

    return list(set(queryset))


def like_post_view(request, slug):
    if not request.user.is_authenticated:
        return redirect('must-authenticate')
    
    post = get_object_or_404(BlogPost, slug=slug)
    author = post.author
    post.likes.add(request.user)
    post.unlikes.remove(request.user)
    author.loyalty_points = author.loyalty_points + 10
    author.save()

    note = Notification()
    note.notification_type = 1
    note.to_user = post.author
    note.from_user = request.user
    note.post = post
    note.save()
    return HttpResponseRedirect(reverse('detail-post', args=[str(slug)]))


def remove_like_post_view(request, slug):
    if not request.user.is_authenticated:
        return redirect('must-authenticate')
    
    post = get_object_or_404(BlogPost, slug=slug)
    post.likes.remove(request.user)
    author = post.author
    author.loyalty_points = author.loyalty_points - 10
    author.save()
    return HttpResponseRedirect(reverse('detail-post', args=[str(slug)]))


def unlike_post_view(request, slug):
    if not request.user.is_authenticated:
        return redirect('must-authenticate')
    
    post = get_object_or_404(BlogPost, slug=slug)
    post.likes.remove(request.user)
    post.unlikes.add(request.user)
    author = post.author
    author.loyalty_points = author.loyalty_points - 10
    author.save()
    return HttpResponseRedirect(reverse('detail-post', args=[str(slug)]))


def remove_unlike_post_view(request, slug):
    if not request.user.is_authenticated:
        return redirect('must-authenticate')
    
    post = get_object_or_404(BlogPost, slug=slug)
    post.unlikes.remove(request.user)
    author = post.author
    author.loyalty_points = author.loyalty_points + 10
    author.save()
    return HttpResponseRedirect(reverse('detail-post', args=[str(slug)]))


def all_categories_view(request):
    context = {}

    categories = Category.objects.all()

    context['categories'] = categories

    return render(request, 'blog/all_categories.html', context)


def show_category_page_view(request, category_name):
    context = {}

    user = request.user
    if not user.is_authenticated:
        return redirect('must-authenticate')

    query = ""
    if request.GET:
        query = request.GET.get('q', '')
        context['query'] = str(query)

    posts = BlogPost.objects.all().filter(category__name = category_name)
    
    # Pagination
    page = request.GET.get('page', 1)
    posts_paginator = Paginator(posts, POSTS_PER_PAGE)

    try:
        posts = posts_paginator.page(page)
    except PageNotAnInteger:
        posts = posts_paginator.page(POSTS_PER_PAGE)
    except EmptyPage:
        posts = posts_paginator.page(posts_paginator.num_pages)

    context['posts'] = posts
    context['category_name'] = category_name

    return render(request, 'blog/category_page.html', context)


def create_comment_view(request,slug):
    context = {}

    user = request.user
    if not user.is_authenticated:
        return redirect('must-authenticate')
    
    post = get_object_or_404(BlogPost, slug=slug)
    
    form = CreateCommentForm(request.POST or None)
    if form.is_valid():
        obj = form.save(commit=False)
        author = Account.objects.get(email=user.email)
        obj.author = author
        obj.post = post
        obj.save()

        note = Notification()
        note.notification_type = 2
        note.to_user = post.author
        note.from_user = user
        note.post = post
        note.save()

        return redirect('detail-post', slug)
    
    form = CreateCommentForm(
        initial= {
            "author" : user,
            "post" : post
        }
    ) 

    context['form'] = form


    return render(request, 'blog/create_comment.html', context)


def like_comment_view(request, slug, comment_id):
    if not request.user.is_authenticated:
        return redirect('must-authenticate')
    
    post = get_object_or_404(BlogPost, slug=slug)
    comment = get_object_or_404(Comment, pk=comment_id)
    comment.likes.add(request.user)
    comment.unlikes.remove(request.user)
    comment_author = comment.author
    comment_author.loyalty_points = comment_author.loyalty_points + 10
    comment_author.save()

    note = Notification()
    note.notification_type = 1
    note.to_user = comment.author
    note.from_user = request.user
    note.comment = comment
    note.save()

    return redirect('detail-post', slug)


def unlike_comment_view(request,slug, comment_id):
    if not request.user.is_authenticated:
        return redirect('must-authenticate')
    
    post = get_object_or_404(BlogPost, slug=slug)
    comment = get_object_or_404(Comment, pk=comment_id)
    comment.likes.remove(request.user)
    comment.unlikes.add(request.user)
    comment_author = comment.author
    comment_author.loyalty_points = comment_author.loyalty_points - 10
    comment_author.save()

    return HttpResponseRedirect(reverse('detail-post', args=[str(slug)]))


def remove_like_comment_view(request,slug, comment_id):
    if not request.user.is_authenticated:
        return redirect('must-authenticate')
    
    post = get_object_or_404(BlogPost, slug=slug)
    comment = get_object_or_404(Comment, pk=comment_id)
    comment.likes.remove(request.user)
    comment_author = comment.author
    comment_author.loyalty_points = comment_author.loyalty_points - 10
    comment_author.save()
    return HttpResponseRedirect(reverse('detail-post', args=[str(slug)]))


def remove_unlike_comment_view(request, slug, comment_id):
    if not request.user.is_authenticated:
        return redirect('must-authenticate')
    
    post = get_object_or_404(BlogPost, slug=slug)
    comment = get_object_or_404(Comment, pk=comment_id)
    comment.unlikes.remove(request.user)
    comment_author = comment.author
    comment_author.loyalty_points = comment_author.loyalty_points + 10
    comment_author.save()
    return HttpResponseRedirect(reverse('detail-post', args=[str(slug)]))


def post_notification(request, notification_pk, post_pk):
    context = {}

    notification = Notification.objects.get(pk=notification_pk)
    post = BlogPost.objects.get(pk=post_pk)

    notification.user_has_seen = True
    notification.save()

    return redirect('detail-post', post.slug)


def edit_request_view(request, blog_post_id):
    context = {}

    user = request.user
    if not user.is_authenticated:
        return redirect('must-authenticate')

    blog_post = get_object_or_404(BlogPost, pk=blog_post_id)


    if request.POST:
        form = CreateEditRequestForm(request.POST, request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            author = blog_post.author
            editor = user
            obj.author = author
            obj.editor = editor
            obj.post_id = blog_post_id
            obj.save()

            note = Notification()
            note.notification_type = 3
            note.to_user = blog_post.author
            note.from_user = request.user
            note.edit = obj
            note.save()
            return redirect('home')
        else:
            print("asdasdasd")

    form = CreateEditRequestForm(
        initial= {
            "title" : blog_post.title,
            "body" : blog_post.body,
            "category" : blog_post.category,
            "header_image" : blog_post.header_image,
            "video" : blog_post.video
        }
    )            

    context['form'] = form
    return render(request, 'blog/edit_request.html', context)


def show_edit_request_notification_view(request, notification_pk, edit_request_id):
    context = {}

    notification = Notification.objects.get(pk=notification_pk)
    edit_request = EditRequest.objects.get(pk=edit_request_id)

    context['editted_post'] = edit_request
    context['notification'] = notification


    notification.user_has_seen = True
    notification.save()

    return render(request, 'blog/show_editted_post.html', context)


def remove_edit_request_view(request, edit_request_id):
    edit = EditRequest.objects.get(pk=edit_request_id)
    edit.delete()

    return redirect('home')


def accept_edit_request_view(request, edit_request_id):
    try:
        editted_post = EditRequest.objects.get(pk=edit_request_id)
    except:
        return HttpResponse('Something went wrong!')
    
    post = BlogPost.objects.get(pk=editted_post.post_id)

    post.title = editted_post.title
    post.body = editted_post.body
    post.category = editted_post.category
    post.header_image = editted_post.header_image
    post.video = editted_post.video
    post.number_of_edits = post.number_of_edits + 1

    post.save()

    editor = editted_post.editor
    editor.loyalty_points = editor.loyalty_points + 10
    editor.save()
    editted_post.delete()

    return redirect('home')


def report_post_view(request, to_user_id, post_slug):
    context = {}

    user = request.user
    if not user.is_authenticated:
        return redirect('must-authenticate')
    

    form = CreateReportForm(request.POST or None)
    if form.is_valid():
        obj = form.save(commit=False)
        obj.from_user = user
        obj.to_user = Account.objects.get(pk=to_user_id)
        obj.post = BlogPost.objects.get(slug=post_slug)

        obj.save()

        return redirect('home')
    form = CreateReportForm()

    context['form'] = form
    return render(request, 'blog/report_post.html', context)


def report_comment_view(request, to_user_id, comment_id):
    context = {}

    user = request.user
    if not user.is_authenticated:
        return redirect('must-authenticate')
    
    form = CreateReportForm(request.POST or None)
    if form.is_valid():
        obj = form.save(commit=False)
        obj.from_user = user
        obj.to_user = Account.objects.get(pk=to_user_id)
        obj.comment = Comment.objects.get(pk=comment_id)

        obj.save()

        return redirect('home')
    form = CreateReportForm()

    context['form'] = form
    return render(request, 'blog/report_comment.html', context)



















































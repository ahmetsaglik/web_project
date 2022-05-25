from django.shortcuts import render
from blog.models import BlogPost, Category

def home_page_view(request):
    context = {}

    posts = BlogPost.objects.all()
    categories = Category.objects.all()
    post_to_send= []

    for cat in categories:
        for post in posts:
            if post.category.name == cat.name:
                post_to_send.append(post)
                print(len(post_to_send))
                if len(post_to_send) % 4 == 0:
                    break

    context['categories'] = categories
    context['posts'] = post_to_send

    return render(request, 'home.html', context)


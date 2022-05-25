from django.contrib import admin

from blog.models import BlogPost, Category, Comment, Notification, EditRequest, Report

admin.site.register(BlogPost)
admin.site.register(Category)
admin.site.register(Comment)
admin.site.register(Notification)
admin.site.register(EditRequest)
admin.site.register(Report)


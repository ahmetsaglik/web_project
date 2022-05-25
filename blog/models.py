from pyexpat import model
from django.db import models
from django.utils import timezone
from django.db.models.signals import pre_save
from django.utils.text import slugify
from django.conf import settings

from ckeditor.fields import RichTextField


def get_header_image_filepath(self, filename):
    return f'header_images/{self.pk}/{filename}'



class Category(models.Model):
    name                    = models.CharField(max_length=35, unique=True)

    def __str__(self):
        return self.name
    


class BlogPost(models.Model):
    title                   = models.CharField(max_length=50, null=False, blank=False)
    body                    = RichTextField(blank=True, null=True)
    category                = models.ForeignKey(Category, on_delete=models.CASCADE)
    header_image            = models.ImageField(max_length=255, upload_to=get_header_image_filepath, null=True, blank=True)
    video                   = models.FileField(null=True, blank=True, upload_to="videos/%y")
    date_published          = models.DateTimeField(auto_now_add=True, verbose_name='date published')
    date_updated            = models.DateTimeField(auto_now=True, verbose_name='date updated')
    author                  = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    slug                    = models.SlugField(blank=True, unique=True)
    likes                   = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='likes_post', blank=True, null=True)
    unlikes                 = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='unlikes_post', blank=True, null=True)
    views                   = models.PositiveIntegerField(default=0)
    number_of_edits         = models.PositiveIntegerField(default=0)

    

    def total_likes(self):
        return self.likes.count()
    
    def total_unlikes(self):
        return self.unlikes.count()

    def __str__(self):
        return self.title


def pre_save_blog_post_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = slugify(instance.author.username + "-" + instance.title)

pre_save.connect(pre_save_blog_post_receiver, sender=BlogPost)


class Comment(models.Model):
    post                    = models.ForeignKey(BlogPost, related_name='comments', on_delete=models.CASCADE)
    author                  = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='comment_author', on_delete=models.CASCADE)
    body                    = models.TextField()
    date_added              = models.DateTimeField(auto_now_add=True)
    likes                   = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='likes_comment', blank=True)
    unlikes                 = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='unlikes_comment', blank=True)


    def total_likes(self):
        return self.likes.count()
    
    def total_unlikes(self):
        return self.unlikes.count()

    def __str__(self):
        return f"{self.post.title} - {self.author.username}"
    

class EditRequest(models.Model):
    title                   = models.CharField(max_length=50, null=False, blank=False)
    body                    = RichTextField(blank=True, null=True)
    category                = models.ForeignKey(Category, on_delete=models.CASCADE)
    header_image            = models.ImageField(max_length=255, upload_to=get_header_image_filepath, null=True, blank=True)
    video                   = models.FileField(null=True, blank=True, upload_to="videos/%y")
    date_published          = models.DateTimeField(auto_now_add=True, verbose_name='date published')
    date_updated            = models.DateTimeField(auto_now=True, verbose_name='date updated')
    author                  = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='post_owner')
    editor                  = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='editor')
    post_id                 = models.CharField(max_length=10, blank=True, null=True)

    def __str__(self):
        return self.title + "edit_request"
    

class Notification(models.Model):
    ## 1-Like 2-Comment 3-Edit Request
    notification_type       = models.SmallIntegerField()
    to_user                 = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='notification_to', on_delete=models.CASCADE, null=True)
    from_user               = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='notification_from', on_delete=models.CASCADE, null=True)
    post                    = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name="+", blank=True, null=True)
    comment                 = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name="+", blank=True, null=True)
    edit                    = models.ForeignKey(EditRequest, on_delete=models.CASCADE, related_name="+", blank=True, null=True)
    date                    = models.DateTimeField(default=timezone.now)
    user_has_seen           = models.BooleanField(default=False)


REPORT_TYPES = [
    ('Slang Word Choice', 'Slang Word Choice'),
    ('Racist Discourse', 'Racist Discourse'),
    ('Wrong Category Selection', 'Wrong Category Selection')
]

class Report(models.Model):
    from_user                   = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='report_from', on_delete=models.CASCADE)
    to_user                     = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='report_to', on_delete=models.CASCADE)
    post                        = models.ForeignKey(BlogPost, related_name='reported_post', on_delete=models.CASCADE, null=True, blank=True)
    comment                     = models.ForeignKey(Comment, related_name='reported_comment', on_delete=models.CASCADE, null=True, blank=True)
    report_type                 = models.CharField(max_length=50, choices=REPORT_TYPES)
    report_date                 = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.from_user} -> {self.to_user}'
    







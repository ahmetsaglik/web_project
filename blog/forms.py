from django import forms
from blog.models import BlogPost, Comment, EditRequest, Report

class CreateBlogPostForm(forms.ModelForm):

    class Meta:
        model = BlogPost
        fields = ('title', 'body', 'category', 'header_image', 'video')



class UpdateBlogPostForm(forms.ModelForm):

    class Meta:
        model = BlogPost
        fields = ('title', 'body', 'category', 'header_image', 'video')
    
    def save(self, commit=True):
        blog_post = self.instance
        blog_post.title = self.cleaned_data['title']
        blog_post.body = self.cleaned_data['body']

        if commit:
            blog_post.save()
        
        return blog_post


class CreateCommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('body',)


class CreateEditRequestForm(forms.ModelForm):

    class Meta:
        model = EditRequest
        fields = ('title', 'body', 'category', 'header_image', 'video')



class CreateReportForm(forms.ModelForm):

    class Meta:
        model = Report
        fields = ('report_type',)












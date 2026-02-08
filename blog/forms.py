import os
from django import forms
from django.conf import settings
from .models import Post, Category

def get_blog_image_choices():
    """Helper to list images in static/images/blog"""
    choices = [('', '---------')]  # Empty choice
    blog_images_dir = os.path.join(settings.BASE_DIR, 'static', 'images', 'blog')
    
    if os.path.exists(blog_images_dir):
        for filename in os.listdir(blog_images_dir):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                path = f'images/blog/{filename}'
                choices.append((path, filename))
    return choices

class PostForm(forms.ModelForm):
    static_image = forms.ChoiceField(
        choices=[], 
        required=False,
        widget=forms.Select(attrs={'class': 'form-select bg-dark text-white border-secondary'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['static_image'].choices = get_blog_image_choices()

    class Meta:
        model = Post
        fields = [
            'title', 'title_it', 
            'category', 
            'content', 'content_it', 
            'status', 
            'meta_description', 'meta_description_it',
            'static_image', 'image'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control bg-dark text-white border-secondary'}),
            'title_it': forms.TextInput(attrs={'class': 'form-control bg-dark text-white border-secondary'}),
            'category': forms.Select(attrs={'class': 'form-select bg-dark text-white border-secondary'}),
            'content': forms.Textarea(attrs={'class': 'form-control bg-dark text-white border-secondary', 'rows': 10}),
            'content_it': forms.Textarea(attrs={'class': 'form-control bg-dark text-white border-secondary', 'rows': 10}),
            'status': forms.Select(attrs={'class': 'form-select bg-dark text-white border-secondary'}),
            'meta_description': forms.TextInput(attrs={'class': 'form-control bg-dark text-white border-secondary'}),
            'meta_description_it': forms.TextInput(attrs={'class': 'form-control bg-dark text-white border-secondary'}),
            'image': forms.FileInput(attrs={'class': 'form-control bg-dark text-white border-secondary'}),
        }

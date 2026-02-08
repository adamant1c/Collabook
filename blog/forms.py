from django import forms
from .models import Post, Category

class PostForm(forms.ModelForm):
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
            'static_image': forms.TextInput(attrs={'class': 'form-control bg-dark text-white border-secondary'}),
            'image': forms.FileInput(attrs={'class': 'form-control bg-dark text-white border-secondary'}),
        }

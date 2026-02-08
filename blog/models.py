from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify

STATUS = (
    (0, "Draft"),
    (1, "Published")
)

class Category(models.Model):
    name = models.CharField(max_length=200, unique=True)
    name_it = models.CharField(max_length=200, unique=True, blank=True, null=True)
    
    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

class Post(models.Model):
    title = models.CharField(max_length=200, unique=True)
    title_it = models.CharField(max_length=200, unique=True, blank=True, null=True)
    slug = models.SlugField(max_length=200, unique=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blog_posts')
    updated_on = models.DateTimeField(auto_now=True)
    content = models.TextField()
    content_it = models.TextField(blank=True, null=True)
    created_on = models.DateTimeField(auto_now_add=True)
    status = models.IntegerField(choices=STATUS, default=0)
    meta_description = models.CharField(max_length=160, blank=True, help_text="A short description for SEO (160 characters max).")
    meta_description_it = models.CharField(max_length=160, blank=True, null=True)
    image = models.ImageField(upload_to='blog_images/', blank=True, null=True)
    static_image = models.CharField(max_length=500, blank=True, null=True, help_text="Path to a static image (e.g., 'images/blog/thumb.jpg').")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='posts')

    class Meta:
        ordering = ['-created_on']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

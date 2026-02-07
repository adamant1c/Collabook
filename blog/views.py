from django.views import generic
from .models import Post

class PostList(generic.ListView):
    queryset = Post.objects.filter(status=1).order_by('-created_on')
    template_name = 'blog/post_list.html'
    paginate_by = 6  # Pagination for better UX/AdSense norms

class PostDetail(generic.DetailView):
    model = Post
    template_name = 'blog/post_detail.html'
    
    def get_queryset(self):
        # Allow viewing only published posts unless user is staff (handled implicitly or via custom permission if needed, 
        # but filter(status=1) is safest for public view).
        # Admin can view via standard admin interface.
        return Post.objects.filter(status=1)

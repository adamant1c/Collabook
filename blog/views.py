from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.shortcuts import redirect
from .models import Post
from .forms import PostForm

class PostList(generic.ListView):
    queryset = Post.objects.filter(status=1).order_by('-created_on')
    template_name = 'blog/post_list.html'
    paginate_by = 6

class PostDetail(generic.DetailView):
    model = Post
    template_name = 'blog/post_detail.html'
    
    def get_queryset(self):
        return Post.objects.filter(status=1)

class StaffDashboard(LoginRequiredMixin, UserPassesTestMixin, generic.ListView):
    model = Post
    template_name = 'blog/staff_dashboard.html'
    context_object_name = 'posts'

    def test_func(self):
        return self.request.user.is_staff

    def get_queryset(self):
        return Post.objects.filter(author=self.request.user).order_by('-created_on')

class PostCreate(LoginRequiredMixin, UserPassesTestMixin, generic.CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/post_form.html'
    success_url = reverse_lazy('blog:dashboard')

    def test_func(self):
        return self.request.user.is_staff

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

class PostUpdate(LoginRequiredMixin, UserPassesTestMixin, generic.UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/post_form.html'
    success_url = reverse_lazy('blog:dashboard')

    def test_func(self):
        post = self.get_object()
        return self.request.user.is_staff and post.author == self.request.user

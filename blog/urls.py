from . import views
from django.urls import path

app_name = 'blog'

urlpatterns = [
    path('', views.PostList.as_view(), name='home'),
    path('dashboard/', views.StaffDashboard.as_view(), name='dashboard'),
    path('create/', views.PostCreate.as_view(), name='post_create'),
    path('edit/<slug:slug>/', views.PostUpdate.as_view(), name='post_edit'),
    path('<slug:slug>/', views.PostDetail.as_view(), name='post_detail'),
]

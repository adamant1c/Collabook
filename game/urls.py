from django.urls import path
from . import views

app_name = 'game'

urlpatterns = [
    path('rules/', views.RulesView.as_view(), name='rules'),
]

from django.urls import path
from . import views

app_name = 'character'

urlpatterns = [
    path('create/', views.CharacterCreationView.as_view(), name='create'),
    path('sheet/', views.CharacterSheetView.as_view(), name='sheet'),
]

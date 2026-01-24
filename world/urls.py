from django.urls import path
from . import views

app_name = 'world'

urlpatterns = [
    path('selection/', views.WorldSelectionView.as_view(), name='selection'),
    path('journey/', views.JourneyView.as_view(), name='journey'),
    path('adventure_summary/', views.AdventureSummaryView.as_view(), name='adventure_summary'),
]

# scraper/discovery/urls.py

from django.urls import path
from .views import add_company

urlpatterns = [
    # POST /api/discover/  → add_company
    path('', add_company, name='add_company'),
]

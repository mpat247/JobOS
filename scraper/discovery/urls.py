from django.urls import path
from .views import discover_view

urlpatterns = [
    path('', discover_view),
]

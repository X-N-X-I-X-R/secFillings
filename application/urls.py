from django.urls import path
from . import views

urlpatterns = [
    path('fetch-sec-filings/', views.fetch_sec_filings_view, name='fetch_sec_filings'),
               path('dashboard/', views.dashboard_view, name='dashboard'),
]


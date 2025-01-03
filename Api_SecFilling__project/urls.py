# Api_SecFilling__project/urls.py

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('django_plotly_dash/', include('django_plotly_dash.urls')),
    path('accounts/', include('django.contrib.auth.urls')),  # הוסף שורה זו
    path('', include('application.urls')),  # הוסף את האפליקציה שלך
]

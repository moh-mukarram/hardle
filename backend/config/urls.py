from django.contrib import admin
from django.urls import path, include
from hardle.api import api

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', api.urls),
    path('accounts/', include('allauth.urls')),  # Google OAuth callback lives here
]

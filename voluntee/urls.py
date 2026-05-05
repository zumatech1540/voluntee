from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),

    # All auth + user system inside accounts app
    path('accounts/', include('accounts.urls')),

    # Home should ALSO come from app or dashboard view
    path('', include('accounts.urls')),
]
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from accounts import views as account_views

urlpatterns = [
    path('admin/', admin.site.urls),

    # HOME
    path('', account_views.home_page, name='home'),

    # ADD THESE (IMPORTANT)
    path('login/', account_views.login_view, name='login'),
    path('logout/', account_views.logout_view, name='logout'),
    path('register/', account_views.register_view, name='register'),
    path('dashboard/', account_views.dashboard, name='dashboard'),

    # ACCOUNTS APP
    path('accounts/', include('accounts.urls')),

    # PROJECTS
    path('projects/', include('projects.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
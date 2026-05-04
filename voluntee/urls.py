from django.contrib import admin
from django.urls import path, include
from accounts import views as account_views

urlpatterns = [
    path('admin/', admin.site.urls),

    # ================= ACCOUNTS APP =================
    path('accounts/', include('accounts.urls')),

    # ================= AUTH PAGES =================
    path('login/', account_views.login_view, name='login'),
    path('logout/', account_views.logout_view, name='logout'),

    # ⚠️ THIS FIXES YOUR ERROR (register was missing)
    path('register/', account_views.register_view, name='register'),

    # ================= HOME =================
    path('', account_views.home, name='home'),
]
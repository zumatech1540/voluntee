from django.urls import path
from . import views

urlpatterns = [

    # HOME
    path('', views.home_page, name='home'),

    # AUTH
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # DASHBOARD
    path('dashboard/', views.dashboard, name='dashboard'),

    # VOLUNTEERS
    path('volunteers/', views.volunteers_page, name='volunteers'),

    # DOWNLOAD USERS
    path('download-users/', views.download_users_excel, name='download_users_excel'),

]
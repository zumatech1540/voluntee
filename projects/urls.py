from django.urls import path
from . import views

urlpatterns = [

    # dashboard (main projects page)
    path('', views.dashboard, name='projects_home'),

    path('dashboard/', views.dashboard, name='dashboard'),

    path('create-project/', views.create_project, name='create_project'),

    path('project/<int:project_id>/', views.project_detail, name='project_detail'),

    path('project/<int:project_id>/join/', views.join_project, name='join_project'),

    # gallery (CORRECT)
    path('gallery/', views.gallery, name='gallery'),
]
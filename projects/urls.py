from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('create-project/', views.create_project),
    path('project/<int:project_id>/', views.project_detail),
    path('join/<int:project_id>/', views.join_project),
]
from django.urls import path
from . import views

urlpatterns = [

    # ================= AUTH =================
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # ================= DASHBOARD =================
    path('dashboard/', views.dashboard, name='dashboard'),

    # ================= USERS =================
    path('download-users/', views.download_users_excel, name='download_users_excel'),

    # ================= STATIC PAGES =================
    path('about/', views.about_page, name='about'),
    path('volunteers/', views.volunteers_page, name='volunteers'),
    path('gallery/', views.gallery_page, name='gallery'),
    path('blogs/', views.blogs_page, name='blogs'),
    path('contact/', views.contact_page, name='contact'),
    path('donate/', views.donate, name='donate'),
    # ================= EVENTS =================
    path('events/', views.events_page, name='events'),
    path('events/create/', views.create_event, name='create_event'),

    path('events/<int:id>/', views.event_detail, name='event_detail'),

    path('events/<int:id>/join/', views.join_event, name='join_event'),
    path('events/<int:id>/leave/', views.leave_event, name='leave_event'),

    path('events/<int:id>/edit/', views.edit_event, name='edit_event'),
    path('events/<int:id>/approve/', views.approve_event, name='approve_event'),
    path('events/<int:id>/reject/', views.reject_event, name='reject_event'),
    path('events/<int:id>/delete/', views.delete_event, name='delete_event'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
 

    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),

    path('events/review/', views.admin_events_review, name='admin_events_review'),

    # EXPORT + WHATSAPP
    path('events/<int:id>/export/', views.export_attendees, name='export_attendees'),
    path('events/<int:id>/whatsapp/', views.whatsapp_attendees, name='whatsapp_attendees'),

    # ================= AJAX =================
    path('ajax/load-wards/', views.load_wards, name='load_wards'),
    path('ajax/load-polling/', views.load_polling, name='load_polling'),
]
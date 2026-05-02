from django.urls import path
from . import views
from .admin_views import admin_dashboard_view

urlpatterns = [

    # ================= AUTH =================
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # ================= DASHBOARD =================
    path('leader/dashboard/', views.leader_dashboard, name='leader_dashboard'),

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

    # ================= ADMIN =================
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path("campaign-dashboard/", admin_dashboard_view, name="campaign_dashboard"),

    # ================= VOLUNTEER =================
    path("volunteer-assignment/", views.volunteer_assignment, name="volunteer_assignment"),
    path("volunteer-performance/", views.volunteer_performance, name="volunteer_performance"),

    # ================= ANALYTICS =================
    path("ward-strength/", views.ward_strength, name="ward_strength"),
    path("polling-strength/", views.polling_strength, name="polling_strength"),
    path("heatmap/", views.heat_map, name="heat_map"),

    # ================= VOTERS =================
    path("register-voter/", views.register_voter, name="register_voter"),
    path("voters/", views.voter_list, name="voter_list"),
    path("voters/add/", views.add_voter, name="add_voter"),
    path("voters/whatsapp/", views.whatsapp_voters, name="whatsapp_voters"),
    path("voters/sms/", views.sms_broadcast, name="sms_broadcast"),

    # ================= EVENTS EXTRA =================
    path('events/review/', views.admin_events_review, name='admin_events_review'),
    path('events/<int:id>/export/', views.export_attendees, name='export_attendees'),
    path('events/<int:id>/whatsapp/', views.whatsapp_attendees, name='whatsapp_attendees'),
    path("event/<int:id>/attendance/", views.event_attendance, name="event_attendance"),

    # ================= USER MANAGEMENT =================
    path("manage-users/", views.manage_users, name="manage_users"),
    path("delete-user/<int:id>/", views.delete_user, name="delete_user"),
    path("make-leader/<int:id>/", views.make_leader, name="make_leader"),
    path("make-volunteer/<int:id>/", views.make_volunteer, name="make_volunteer"),
    path("make-admin/<int:id>/", views.make_admin, name="make_admin"),
    path("remove-admin/<int:id>/", views.remove_admin, name="remove_admin"),
    path("tasks/assign/", views.assign_task, name="assign_task"),
    path("tasks/my/", views.my_tasks, name="my_tasks"),
    path("tasks/", views.my_tasks, name="my_tasks"),
    path("tasks/update/<int:id>/", views.update_task_status, name="update_task_status"),
    path("tasks/leader/", views.leader_tasks, name="leader_tasks"),
    path('user-tasks/<int:user_id>/', views.user_tasks_admin, name='user_tasks_admin'),
    path('tasks/assign/<int:user_id>/', views.assign_task_admin, name='assign_task_admin'),
    path("tasks/assign/<int:id>/", views.assign_task_admin, name="assign_task_admin"),
    path("volunteer-home/", views.volunteer_home, name="volunteer_home"),
    path("complete-task/<int:id>/", views.complete_task, name="complete_task"),
    # ================= AJAX =================
    path('ajax/load-wards/', views.load_wards, name='load_wards'),
    path('ajax/load-polling/', views.load_polling, name='load_polling'),
]
from django.urls import path
from . import views

urlpatterns = [
    path("dashboard/", views.dashboard, name="dashboard"),
    path("questionnaire/", views.questionnaire, name="questionnaire"),
    path("find/", views.find_roommate, name="find_roommate"),
    path("match/<int:user_id>/", views.match_detail, name="match_detail"),
    path("request/send/<int:user_id>/", views.send_request, name="send_request"),
    path("request/<int:request_id>/<str:action>/", views.respond_request, name="respond_request"),
    path("request/<int:request_id>/cancel/", views.cancel_request, name="cancel_request"),
    path("requests/", views.requests_view, name="requests"),
]

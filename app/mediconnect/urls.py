from django.urls import path
from django.contrib.auth import views as auth_views
from .views import (
    landing_page,
    dashboard_redirect,
    user_dashboard,
    doctor_dashboard,
    hospital_dashboard,
    register,
    custom_logout,
    upload_medical_document,
    user_documents,
    request_access,
    approve_access,
    deny_access,
    view_patient_documents,
    doctor_access_requests,
    doctor_documents,
    revoke_access,
    user_complete_summary
)
from django.contrib.auth.views import LogoutView
from .views import CustomLoginView

urlpatterns = [
    path("", landing_page, name="landing_page"),
    path("dashboard/", dashboard_redirect, name="dashboard_redirect"),
    path("register/", register, name="register"),
    path("login/", CustomLoginView.as_view(), name="login"),
    path("logout/", custom_logout, name="logout"),
    path("dashboard/user/", user_dashboard, name="user_dashboard"),
    path("dashboard/doctor/", doctor_dashboard, name="doctor_dashboard"),
    path("dashboard/hospital/", hospital_dashboard, name="hospital_dashboard"),
    path(
        "upload-document/<uuid:user_id>/",
        upload_medical_document,
        name="upload_document",
    ),
    path("user-documents/<uuid:user_id>/", user_documents, name="user_documents"),
    path("request-access/<uuid:patient_id>/", request_access, name="request_access"),
    path("approve-access/<str:hash_link>/", approve_access, name="approve_access"),
    path("deny-access/<int:request_id>/", deny_access, name="deny_access"),
    path(
        "doctor/access-requests/", doctor_access_requests, name="doctor_access_requests"
    ),
    path(
        "view-documents/<uuid:patient_id>/",
        view_patient_documents,
        name="view_patient_documents",
    ),
    path("revoke-access/<int:request_id>/", revoke_access, name="revoke_access"),
    path(
        "doctor/documents/<uuid:patient_id>/", doctor_documents, name="doctor_documents"
    ),

    # complete_summary_link
    path("user-complete-summary/<uuid:user_id>/", user_complete_summary, name="user_complete_summary")
]

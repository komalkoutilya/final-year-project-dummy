from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from .models import User, MedicalDocument, DoctorAccessRequest
from .forms import RegisterForm
from django.contrib.auth.views import LoginView
from django.utils.decorators import method_decorator
from django.http import HttpResponseForbidden
from django.contrib.auth import logout

from django.shortcuts import get_object_or_404
from .forms import MedicalDocumentForm
from django.core.mail import send_mail
import random
from django.contrib import messages

import hashlib
import random
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.utils.crypto import get_random_string




def landing_page(request):
    if request.user.is_authenticated:  # Check if the user is logged in
        return redirect_to_correct_dashboard(request.user)
    return render(request, "mediconnect/landing.html")


def redirect_to_correct_dashboard(user):
    if user.role == "user":
        return redirect("user_dashboard")
    elif user.role == "doctor":
        return redirect("doctor_dashboard")
    elif user.role == "hospital":
        return redirect("hospital_dashboard")
    return redirect("login")  # Default fallback if role is missing


def custom_logout(request):
    logout(request)
    return redirect("landing_page")  # Redirect to the landing page


def generate_access_hash(doctor, patient):
    """Generate a secure hash for access approval."""
    raw_string = f"{doctor.id}{patient.id}{random.randint(1000,9999)}"
    return hashlib.sha256(raw_string.encode()).hexdigest()


@login_required
def user_dashboard(request):
    if request.user.role != "user":
        return redirect("dashboard_redirect")

    documents = MedicalDocument.objects.filter(user=request.user)

    # Fetch both pending and approved requests
    access_requests = DoctorAccessRequest.objects.filter(patient=request.user).only(
        "id", "doctor", "hash_link", "approved"
    )

    return render(
        request,
        "mediconnect/user_dashboard.html",
        {"documents": documents, "access_requests": access_requests},
    )


@login_required
def doctor_dashboard(request):
    if request.user.role != "doctor":  # Ensure only doctors can access
        return redirect("dashboard_redirect")

    search_query = request.GET.get("search", "")

    # Fetch all patients
    patients = User.objects.filter(role="user").select_related("hospital")

    # Search by UUID or username
    if search_query:
        patients = patients.filter(unique_id__icontains=search_query) | patients.filter(
            username__icontains=search_query
        )

    # Check if the doctor has approved access for each patient
    for patient in patients:
        patient.has_access = DoctorAccessRequest.objects.filter(
            doctor=request.user, patient=patient, approved=True
        ).exists()

    return render(request, "mediconnect/doctor_dashboard.html", {"patients": patients})


@login_required
def doctor_access_requests(request):
    if request.user.role != "doctor":
        return redirect("dashboard_redirect")

    access_requests = DoctorAccessRequest.objects.filter(doctor=request.user)

    return render(
        request,
        "mediconnect/doctor_access_requests.html",
        {"access_requests": access_requests},
    )


def is_hospital(user):
    return user.role == "hospital"  # Ensure only hospitals can access this


@login_required
@user_passes_test(is_hospital)  # Restrict access to hospitals only
def user_documents(request, user_id):
    patient = get_object_or_404(User, unique_id=user_id)  # Get user
    documents = MedicalDocument.objects.filter(user=patient)  # Fetch all docs

    if request.method == "POST":  # Handling document deletion
        doc_id = request.POST.get("doc_id")
        doc = get_object_or_404(MedicalDocument, id=doc_id)
        doc.document.delete()  # Delete the file
        doc.delete()  # Delete from database
        return redirect("user_documents", user_id=user_id)

    return render(
        request,
        "mediconnect/user_documents.html",
        {"patient": patient, "documents": documents},
    )


@login_required
def hospital_dashboard(request):
    if request.user.role != "hospital":
        return redirect("dashboard_redirect")  # Prevent unauthorized access

    search_query = request.GET.get("search", "")
    users = User.objects.filter(role="user")  # Fetch only patients

    if search_query:
        users = users.filter(unique_id__icontains=search_query) | users.filter(
            username__icontains=search_query
        )

    return render(request, "mediconnect/hospital_dashboard.html", {"users": users})


@login_required
def upload_medical_document(request, user_id):
    if request.user.role != "hospital":
        return HttpResponseForbidden("You are not authorized to upload documents.")

    user = get_object_or_404(User, unique_id=user_id)
    if request.method == "POST":
        form = MedicalDocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.user = user
            document.hospital = request.user
            document.document_summary = form.cleaned_data["document_summary"]
            document.save()
            return redirect("hospital_dashboard")

    else:
        form = MedicalDocumentForm()

    return render(
        request, "mediconnect/upload_document.html", {"form": form, "user": user}
    )


# Helper function to redirect users to the correct dashboard
def redirect_to_correct_dashboard(user):
    if user.role == "user":
        return redirect("user_dashboard")
    elif user.role == "doctor":
        return redirect("doctor_dashboard")
    elif user.role == "hospital":
        return redirect("hospital_dashboard")
    return redirect("login")  # Default fallback


class CustomLoginView(LoginView):
    template_name = "mediconnect/login.html"

    def get_success_url(self):
        user = self.request.user
        if user.role == "user":
            return "/dashboard/user/"
        elif user.role == "doctor":
            return "/dashboard/doctor/"
        elif user.role == "hospital":
            return "/dashboard/hospital/"
        return "/"


@login_required
def dashboard_redirect(request):
    if request.user.role == "user":
        return redirect("user_dashboard")
    elif request.user.role == "doctor":
        return redirect("doctor_dashboard")
    elif request.user.role == "hospital":
        return redirect("hospital_dashboard")
    else:
        return redirect("landing_page")


def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = form.cleaned_data["role"]
            user.save()
            login(request, user)
            return redirect("dashboard_redirect")  # Redirect based on role
    else:
        form = RegisterForm()

    return render(request, "mediconnect/register.html", {"form": form})


@login_required
def request_access(request, patient_id):
    if request.user.role != "doctor":
        return redirect("dashboard_redirect")

    patient = get_object_or_404(User, unique_id=patient_id, role="user")

    # Generate a persistent hash based on doctor ID + patient ID
    hash_input = f"{request.user.id}{patient.id}".encode()
    hash_link = hashlib.sha256(hash_input).hexdigest()[:10]  # Shortened hash

    # Store access request
    access_request, created = DoctorAccessRequest.objects.get_or_create(
        doctor=request.user,
        patient=patient,
        defaults={"hash_link": hash_link},  # Ensure hash is saved
    )

    messages.success(request, "Access request sent.")
    return redirect("doctor_dashboard")


@login_required
def approve_access(request, hash_link):
    if request.user.role != "user":
        return redirect("dashboard_redirect")

    access_request = get_object_or_404(
        DoctorAccessRequest, hash_link=hash_link, patient=request.user
    )

    if not access_request.hash_link:
        access_request.hash_link = urlsafe_base64_encode(force_bytes(access_request.id))

    access_request.approved = True
    access_request.save()

    messages.success(request, "Access granted to doctor.")
    return redirect("user_dashboard")


@login_required
def deny_access(request, request_id):
    if request.user.role != "user":
        return redirect("dashboard_redirect")

    access_request = get_object_or_404(
        DoctorAccessRequest, id=request_id, patient=request.user
    )
    access_request.delete()

    messages.success(request, "Access request denied.")
    return redirect("user_dashboard")


@login_required
def view_patient_documents(request, patient_id):
    if request.user.role != "doctor":
        return redirect("dashboard_redirect")

    patient = get_object_or_404(User, unique_id=patient_id, role="user")
    access_request = DoctorAccessRequest.objects.filter(
        doctor=request.user, patient=patient, approved=True
    ).first()

    if not access_request:
        messages.error(request, "You do not have permission to view these documents.")
        return redirect("doctor_dashboard")

    documents = MedicalDocument.objects.filter(user=patient)
    return render(
        request,
        "mediconnect/doctor_documents.html",
        {"patient": patient, "documents": documents},
    )


@login_required
def doctor_documents(request, patient_id):
    if request.user.role != "doctor":  # Only doctors can access
        return redirect("dashboard_redirect")

    patient = get_object_or_404(User, unique_id=patient_id, role="user")

    # Check if the doctor has approved access to this patient
    has_access = DoctorAccessRequest.objects.filter(
        doctor=request.user, patient=patient, approved=True
    ).exists()

    if not has_access:
        messages.error(request, "You do not have access to this patient's records.")
        return redirect("doctor_dashboard")

    # Fetch patient's medical documents
    documents = MedicalDocument.objects.filter(user=patient)

    return render(
        request,
        "mediconnect/doctor_documents.html",
        {"patient": patient, "documents": documents},
    )


@login_required
def revoke_access(request, request_id):
    access_request = get_object_or_404(
        DoctorAccessRequest, id=request_id, patient=request.user
    )

    if access_request.approved:
        access_request.approved = False
        access_request.revoked = True  # Mark as revoked
        access_request.save()
        messages.success(
            request,
            f"Access for Dr. {access_request.doctor.username} has been revoked.",
        )
    else:
        messages.error(
            request, "This access request is not approved or already revoked."
        )

    return redirect("user_dashboard")

# user-complete-summary... {new feature added by @komalkoutilya}
@login_required
def user_complete_summary(request, user_id):
    patient = get_object_or_404(User, unique_id=user_id) # Get user
    documents = MedicalDocument.objects.filter(user=patient) #Fetch all docs

    document_summary_list=[str(i.document_summary) for i in documents]
    document_severity_list=[int(i.document_severity) for i in documents]

    final_summary="".join(document_summary_list)
    return render(request, "mediconnect/user_complete_summary.html", {"summary":final_summary, "patient_id":patient.unique_id})




# def user_documents(request, user_id):
#     patient = get_object_or_404(User, unique_id=user_id)  # Get user
#     documents = MedicalDocument.objects.filter(user=patient)  # Fetch all docs

#     if request.method == "POST":  # Handling document deletion
#         doc_id = request.POST.get("doc_id")
#         doc = get_object_or_404(MedicalDocument, id=doc_id)
#         doc.document.delete()  # Delete the file
#         doc.delete()  # Delete from database
#         return redirect("user_documents", user_id=user_id)

#     return render(
#         request,
#         "mediconnect/user_documents.html",
#         {"patient": patient, "documents": documents},
#     )
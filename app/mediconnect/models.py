from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid
import hashlib


class User(AbstractUser):
    ROLE_CHOICES = (
        ("user", "User"),
        ("doctor", "Doctor"),
        ("hospital", "Hospital"),
    )
    unique_id = models.UUIDField(
        default=uuid.uuid4, editable=False, unique=True
    )  # Unique ID for each user
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

    hospital = models.ForeignKey(
        "User",  # Change "Hospital" to "User"
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={"role": "hospital"},  # Only allow hospital users
    )

    def __str__(self):
        return f"{self.username} ({self.role})"


def user_directory_path(instance, filename):
    return f"medical_documents/{instance.user.unique_id}/{filename}"


class MedicalDocument(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="documents")
    hospital = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="uploaded_documents",
        limit_choices_to={"role": "hospital"},
    )
    document = models.FileField(upload_to=user_directory_path)
    document_summary=models.TextField(default="") #new updated by __
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Document for {self.user.username} uploaded by {self.hospital.username}"


class DoctorAccessRequest(models.Model):
    doctor = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="access_requests"
    )
    patient = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="access_requests_received"
    )
    hash_link = models.CharField(
        max_length=255, unique=True
    )  # Unique link for approval
    approved = models.BooleanField(default=False)
    revoked = models.BooleanField(default=False)  # Track revoked access
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Request from {self.doctor.username} to {self.patient.username} - Approved: {self.approved} - Revoked: {self.revoked}"

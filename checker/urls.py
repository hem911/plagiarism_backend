# plagiarism_backend/checker/urls.py
from django.urls import path
from .views import CheckPlagiarismView

urlpatterns = [
    path("check/", CheckPlagiarismView.as_view(), name="check-plagiarism"),
]

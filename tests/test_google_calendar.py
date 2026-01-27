import pytest
from django.utils import timezone
from task_manager.models import google_calendar_url
from datetime import datetime, timedelta

@pytest.mark.django_db
def test_google_calendar_url_timezone_aware():
    name = "Test Task"
    # Deadline: 2026-01-27 15:00 UTC+2
    local_dt = timezone.make_aware(datetime(2026, 1, 27, 15, 0), timezone.get_fixed_timezone(120))
    url = google_calendar_url(name, local_dt, duration_minutes=30, details="Details")
    # Should convert to UTC: start=12:30, end=13:00
    assert "action=TEMPLATE" in url
    assert "text=Test+Task" in url
    assert "details=Details" in url
    assert "dates=20260127T123000Z/20260127T130000Z" in url

from django.test import Client
from django.urls import reverse
from task_manager.models import Task

@pytest.mark.django_db
def test_add_to_google_calendar_view(client):
    # Create a task with aware deadline
    deadline = timezone.make_aware(datetime(2026, 1, 27, 15, 0), timezone.get_fixed_timezone(120))
    task = Task.objects.create(name="Test Task", description="desc", deadline=deadline, is_completed=False, priority="low", task_type_id=1)
    url = reverse("task_manager:task-google-calendar", args=[task.pk])
    response = client.get(url)
    assert response.status_code == 302
    location = response.headers["Location"]
    assert "action=TEMPLATE" in location
    assert "text=Test+Task" in location
    assert "dates=20260127T123000Z/20260127T130000Z" in location

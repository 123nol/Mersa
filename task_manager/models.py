from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.utils import timezone
from urllib.parse import urlencode

def google_calendar_url(task_name, deadline_dt, duration_minutes=30, details=None):
    """
    Returns a Google Calendar event creation URL for the given task.
    deadline_dt: timezone-aware datetime (event ends at this time)
    duration_minutes: event duration in minutes (default 30)
    details: optional event description
    """
    import datetime
    if deadline_dt is None or not timezone.is_aware(deadline_dt):
        raise ValueError("Deadline must be a timezone-aware datetime.")
    end_utc = deadline_dt.astimezone(datetime.timezone.utc)
    start_utc = end_utc - datetime.timedelta(minutes=duration_minutes)
    fmt = "%Y%m%dT%H%M%SZ"
    dates = f"{start_utc.strftime(fmt)}/{end_utc.strftime(fmt)}"
    params = {
        "action": "TEMPLATE",
        "text": task_name,
        "dates": dates,
    }
    if details:
        params["details"] = details
    url = "https://www.google.com/calendar/render?" + urlencode(params)
    return url


# --- Workspace and Membership Models ---
class Workspace(models.Model):
    name = models.CharField(max_length=255)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="created_workspaces")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class WorkspaceMembership(models.Model):
    ROLE_CHOICES = [
        ("ADMIN", "Admin"),
        ("MANAGER", "Manager"),
        ("MEMBER", "Member"),
        ("VIEWER", "Viewer"),
    ]
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name="memberships")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="workspace_memberships")
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("workspace", "user")

    def __str__(self):
        return f"{self.user} in {self.workspace} as {self.role}"

# --- Task Model (now with workspace FK) ---
class Task(models.Model):
    PRIORITY_CHOICES = {
        "urgent": "Urgent",
        "high": "High",
        "medium": "Medium",
        "low": "Low",
    }
    name = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    deadline = models.DateField()
    is_completed = models.BooleanField()
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default="low")
    task_type = models.ForeignKey("TaskType", on_delete=models.CASCADE)
    assignees = models.ManyToManyField("Worker", related_name="tasks")
    # Make workspace nullable for initial migration/backfill, then set null=False after data is fixed
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name="tasks", null=False, blank=False)
# --- RBAC Helpers ---
ROLE_HIERARCHY = {
    'VIEWER': 0,
    'MEMBER': 1,
    'MANAGER': 2,
    'ADMIN': 3,
}

def get_membership(user, workspace):
    try:
        return WorkspaceMembership.objects.get(user=user, workspace=workspace)
    except WorkspaceMembership.DoesNotExist:
        return None

def require_role(user, workspace, min_role):
    membership = get_membership(user, workspace)
    if not membership or ROLE_HIERARCHY[membership.role] < ROLE_HIERARCHY[min_role]:
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied(f"Requires role {min_role} or higher")
    return membership

def can_edit_task(user, task):
    membership = get_membership(user, task.workspace)
    if not membership:
        return False
    if membership.role in ['ADMIN', 'MANAGER']:
        return True
    if membership.role == 'MEMBER' and task.assignees.filter(pk=user.pk).exists():
        return True
    return False

    def __str__(self):
        return self.name


# Attachment model for file uploads
class Attachment(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="attachments")
    file = models.FileField(upload_to="attachments/")
    uploaded_at = models.DateTimeField(auto_now_add=True)


class TaskType(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Worker(AbstractUser):
    user = models.OneToOneField(User, on_delete=models.CASCADE)


class Position(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

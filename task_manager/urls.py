from django.urls import path

from task_manager.views import (
    index,
    WorkerListView,
    WorkerCreateView,
    WorkerDetailView,
    WorkerUpdateView,
    WorkerDeleteView,
    TaskListView,
    TaskCreateView,
    TaskDetailView,
    TaskUpdateView,
    TaskDeleteView,
    TaskTypeListView,
    TaskTypeCreateView,
    TaskTypeDetailView,
    TaskTypeUpdateView,
    TaskTypeDeleteView,
    PositionCreateView,
    PositionListView,
    PositionDetailView,
    PositionUpdateView,
    PositionDeleteView,
    task_completed,
    task_not_completed,
    complete_task,
    registration,
    TaskCompletedView,
)
from task_manager.views import add_to_google_calendar
from task_manager import workspace_views

urlpatterns = [
    path("", index, name="index"),
    # worker list removed (access via workspaces)
    path("workers/create/", WorkerCreateView.as_view(), name="worker-create"),
    path("workers/<int:pk>/", WorkerDetailView.as_view(), name="worker-detail"),
    path("workers/<int:pk>/update/", WorkerUpdateView.as_view(), name="worker-update"),
    path("workers/<int:pk>/delete/", WorkerDeleteView.as_view(), name="worker-delete"),
    path("tasks/", TaskListView.as_view(), name="task-list"),
    path("tasks/create/", TaskCreateView.as_view(), name="task-create"),
    path("tasks/<int:pk>/", TaskDetailView.as_view(), name="task-detail"),
    path("tasks/<int:pk>/update/", TaskUpdateView.as_view(), name="task-update"),
    path("tasks/<int:pk>/delete/", TaskDeleteView.as_view(), name="task-delete"),
    path("tasks/completed/", TaskCompletedView.as_view(), name="task-completed"),
    path("tasks/not-completed/", task_not_completed, name="task-not-completed"),
    path("task/<int:pk>/complete/", complete_task, name="task-complete"),
    path("task_types/", TaskTypeListView.as_view(), name="task_type-list"),
    path("task_types/create/", TaskTypeCreateView.as_view(), name="task_type-create"),
    path("task_types/<int:pk>/", TaskTypeDetailView.as_view(), name="task_type-detail"),
    path(
        "task_types/<int:pk>/update/",
        TaskTypeUpdateView.as_view(),
        name="task_type-update",
    ),
    path(
        "task_types/<int:pk>/delete/",
        TaskTypeDeleteView.as_view(),
        name="task_type-delete",
    ),
    # positions list removed (managed via admin or workspace roles)
    path("positions/create/", PositionCreateView.as_view(), name="position-create"),
    path("positions/<int:pk>/", PositionDetailView.as_view(), name="position-detail"),
    path(
        "positions/<int:pk>/update/",
        PositionUpdateView.as_view(),
        name="position-update",
    ),
    path(
        "positions/<int:pk>/delete/",
        PositionDeleteView.as_view(),
        name="position-delete",
    ),
    path("accounts/register/", registration, name="register"),
    path("tasks/<int:task_id>/google-calendar/", add_to_google_calendar, name="task-google-calendar"),
    # Workspace URLs
    path('workspaces/', workspace_views.workspace_list, name='workspace-list'),
    path('workspaces/create/', workspace_views.workspace_create, name='workspace-create'),
    path('workspaces/<int:ws_id>/', workspace_views.workspace_detail, name='workspace-detail'),
    path('workspaces/<int:ws_id>/add-member/', workspace_views.workspace_add_member, name='workspace-add-member'),
    path('workspaces/<int:ws_id>/remove-member/<int:user_id>/', workspace_views.workspace_remove_member, name='workspace-remove-member'),
    path('workspaces/<int:ws_id>/change-role/<int:user_id>/', workspace_views.workspace_change_role, name='workspace-change-role'),
    path('workspaces/<int:ws_id>/delete/', workspace_views.workspace_delete, name='workspace-delete'),
]

app_name = "task_manager"

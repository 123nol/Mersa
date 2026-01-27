from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.views import generic

from task_manager.forms import (
    WorkerCreationForm,
    TaskForm,
    RegistrationForm,
    TaskSearchForm,
    WorkerSearchForm,
)
from task_manager.models import Worker, Task, TaskType, Position, google_calendar_url
from django.http import HttpResponseBadRequest
from django.utils import timezone
def add_to_google_calendar(request, task_id):
    task = Task.objects.filter(pk=task_id).first()
    deadline = getattr(task, 'deadline', None)
    # If deadline is a date, convert to datetime (assume 17:00 local)
    if deadline and not hasattr(deadline, 'hour'):
        deadline = timezone.make_aware(timezone.datetime.combine(deadline, timezone.datetime.min.time().replace(hour=17)))
    if not deadline or not timezone.is_aware(deadline):
        return HttpResponseBadRequest("Task deadline must be set and timezone-aware.")
    url = google_calendar_url(task.name, deadline, details=getattr(task, 'description', None))
    return redirect(url)


def index(request):
    # basic user and visit tracking
    res = Worker.objects.count()
    num_visits = request.session.get("num_visits", 0)
    request.session["num_visits"] = num_visits + 1
    # persist per-user visits for cross-user comparisons
    if request.user.is_authenticated:
        try:
            user_obj = Worker.objects.get(pk=request.user.pk)
            user_obj.visit_count = (user_obj.visit_count or 0) + 1
            user_obj.save(update_fields=['visit_count'])
        except Worker.DoesNotExist:
            pass

    name = request.GET.get("name", "")

    # Determine workspaces the current user can act on (memberships: ADMIN/MANAGER/MEMBER/VIEWER)
    from task_manager.models import Workspace
    if request.user.is_authenticated:
        user_workspaces = Workspace.objects.filter(memberships__user=request.user).distinct()
    else:
        user_workspaces = Workspace.objects.none()

    # Core task metrics scoped to user's workspaces
    total_tasks = Task.objects.filter(workspace__in=user_workspaces).count()
    closed_task_counter = Task.objects.filter(workspace__in=user_workspaces, is_completed=True).count()
    open_tasks = Task.objects.filter(workspace__in=user_workspaces, is_completed=False).count()
    # overdue: has deadline before today and not completed
    today = timezone.now().date()
    overdue_count = Task.objects.filter(workspace__in=user_workspaces, is_completed=False, deadline__lt=today).count()

    # Performance chart: tasks created and tasks closed per day (last 14 days)
    from datetime import timedelta
    days = 7
    labels = []
    created_series = []
    closed_series = []
    for i in range(days - 1, -1, -1):
        day = timezone.now().date() - timedelta(days=i)
        labels.append(day.strftime("%Y-%m-%d"))
        created = Task.objects.filter(workspace__in=user_workspaces, created_at__date=day).count()
        closed = Task.objects.filter(workspace__in=user_workspaces, is_completed=True, created_at__date=day).count()
        created_series.append(created)
        closed_series.append(closed)

    # Status distribution for small chart
    status_distribution = {
        'closed': closed_task_counter,
        'open': open_tasks,
        'overdue': overdue_count,
    }

    # Visitors percentage: compare this user's visit_count to sum of visit_count of users in same workspaces
    visitors_percentage = 0
    if request.user.is_authenticated and user_workspaces.exists():
        from django.db.models import Sum
        users_in_ws = Worker.objects.filter(workspace_memberships__workspace__in=user_workspaces).distinct()
        total_visits_ws = users_in_ws.aggregate(total=Sum('visit_count'))['total'] or 0
        try:
            my_visits = Worker.objects.get(pk=request.user.pk).visit_count or 0
        except Worker.DoesNotExist:
            my_visits = 0
        if total_visits_ws > 0:
            visitors_percentage = int(my_visits * 100.0 / total_visits_ws)

    # Todo list: tasks assigned to the user, incomplete, upcoming
    if request.user.is_authenticated:
        todo_items = Task.objects.filter(workspace__in=user_workspaces, assignees=request.user, is_completed=False).order_by('deadline')[:6]
    else:
        todo_items = Task.objects.none()

    # last task for preview
    last_task = Task.objects.filter(workspace__in=user_workspaces).order_by('-created_at').first()

    context = {
        "ind": res,
        "num_visits": num_visits + 1,
        "total_tasks": total_tasks,
        "closed_task_counter": closed_task_counter,
        "open_tasks": open_tasks,
        "overdue_count": overdue_count,
        "performance_labels": labels,
        "performance_created": created_series,
        "performance_closed": closed_series,
        "status_distribution": status_distribution,
        "todo_items": todo_items,
            "today": today,
        "performance_labels_json": __import__('json').dumps(labels),
        "performance_created_json": __import__('json').dumps(created_series),
        "performance_closed_json": __import__('json').dumps(closed_series),
        "status_distribution_json": __import__('json').dumps(status_distribution),
        "visitors_percentage": visitors_percentage,
        "visitors_total": total_visits_ws if request.user.is_authenticated and user_workspaces.exists() else 0,
        "my_visits": my_visits if request.user.is_authenticated else 0,
        "search_form": TaskSearchForm(initial={"name": name}),
        "last_task": last_task,
    }

    if name:
        queryset = Task.objects.all()
        task_list = queryset.filter(name__icontains=name)

        context["task_list"] = task_list
        return render(
            request, template_name="task_manager/task_list.html", context=context
        )

    return render(request, template_name="task_manager/index.html", context=context)


class WorkerListView(LoginRequiredMixin, generic.ListView):
    model = Worker
    paginate_by = 5

    # add search form to the page
    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(WorkerListView, self).get_context_data(**kwargs)
        username = self.request.GET.get("username", "")
        context["search_form_worker"] = WorkerSearchForm(initial={"username": username})
        return context

    # update data in the page after searching
    def get_queryset(self):
        queryset = Worker.objects.select_related("position")
        username = self.request.GET.get("username")
        if username:
            return queryset.filter(username__icontains=username)
        return queryset


class WorkerCreateView(LoginRequiredMixin, generic.CreateView):
    model = Worker
    form_class = WorkerCreationForm
    success_url = reverse_lazy("task_manager:index")


class WorkerDetailView(LoginRequiredMixin, generic.DetailView):
    model = Worker
    queryset = Worker.objects.select_related("position")


class WorkerUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Worker
    fields = (
        "username",
        "first_name",
        "last_name",
        "email",
        "date_joined",
        "position",
    )
    success_url = reverse_lazy("task_manager:index")
    queryset = Worker.objects.select_related("position")  # not help


class WorkerDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Worker
    success_url = reverse_lazy("task_manager:index")
    queryset = Worker.objects.select_related("position")


class TaskListView(LoginRequiredMixin, generic.ListView):
    model = Task
    paginate_by = 10

    def get_context_data(self, *, object_list=None, **kwargs):
        """Add search form to the page"""
        context = super(TaskListView, self).get_context_data(**kwargs)
        name = self.request.GET.get("name", "")
        context["search_form"] = TaskSearchForm(initial={"name": name})
        return context

    def get_queryset(self):
        """update data in the page after searching"""
        queryset = Task.objects.all()
        name = self.request.GET.get("name")
        if name:
            return queryset.filter(name__icontains=name)
        return queryset


class TaskCreateView(LoginRequiredMixin, generic.CreateView):
    model = Task
    form_class = TaskForm
    success_url = reverse_lazy("task_manager:task-list")

    def form_valid(self, form):
        # enforce that request.user has role >= MEMBER in selected workspace
        workspace = form.cleaned_data.get('workspace')
        from task_manager.models import get_membership, ROLE_HIERARCHY
        membership = get_membership(self.request.user, workspace)
        if not membership or ROLE_HIERARCHY.get(membership.role, 0) < ROLE_HIERARCHY['MEMBER']:
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied('You do not have permission to create tasks in this workspace.')
        response = super().form_valid(form)
        files = self.request.FILES.getlist("attachments")
        for f in files:
            if f.content_type == "application/pdf":
                from task_manager.models import Attachment
                Attachment.objects.create(task=self.object, file=f)
        return response

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs


class TaskDetailView(LoginRequiredMixin, generic.DetailView):
    model = Task
    queryset = Task.objects.select_related("task_type").prefetch_related("assignees", "attachments")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["attachments"] = self.object.attachments.all()
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs

    def form_valid(self, form):
        # enforce edit permission
        from task_manager.models import can_edit_task
        if not can_edit_task(self.request.user, self.object):
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied('You do not have permission to edit this task.')
        return super().form_valid(form)


class TaskUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Task
    form_class = TaskForm
    success_url = reverse_lazy("task_manager:task-list")

    def form_valid(self, form):
        response = super().form_valid(form)
        files = self.request.FILES.getlist("attachments")
        for f in files:
            if f.content_type == "application/pdf":
                from task_manager.models import Attachment
                Attachment.objects.create(task=self.object, file=f)
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["attachments"] = self.object.attachments.all()
        return context


class TaskDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Task
    success_url = reverse_lazy("task_manager:task-list")


class TaskTypeListView(LoginRequiredMixin, generic.ListView):
    model = TaskType
    context_object_name = "task_type_list"
    paginate_by = 8


class TaskTypeCreateView(LoginRequiredMixin, generic.CreateView):
    model = TaskType
    fields = "__all__"
    success_url = reverse_lazy("task_manager:task_type-list")


class TaskTypeDetailView(LoginRequiredMixin, generic.DetailView):
    model = TaskType
    queryset = TaskType.objects.all()


class TaskTypeUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = TaskType
    fields = "__all__"
    success_url = reverse_lazy("task_manager:task_type-list")


class TaskTypeDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = TaskType
    success_url = reverse_lazy("task_manager:task_type-list")


class PositionListView(LoginRequiredMixin, generic.ListView):
    model = Position
    paginate_by = 8


class PositionCreateView(LoginRequiredMixin, generic.CreateView):
    model = Position
    fields = "__all__"
    success_url = reverse_lazy("task_manager:index")


class PositionDetailView(LoginRequiredMixin, generic.DetailView):
    model = Position
    queryset = Position.objects.all()


class PositionUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Position
    fields = "__all__"
    success_url = reverse_lazy("task_manager:index")


class PositionDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Position
    success_url = reverse_lazy("task_manager:index")


class TaskCompletedView(LoginRequiredMixin, generic.ListView):
    # queryset = Task.objects.filter(is_completed=True)
    paginate_by = 10

    # add search form to the page
    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(TaskCompletedView, self).get_context_data(**kwargs)
        name = self.request.GET.get("name", "")
        context["search_form"] = TaskSearchForm(initial={"name": name})
        return context

    # update data in the page after searching
    def get_queryset(self):
        queryset = Task.objects.filter(is_completed=True)
        name = self.request.GET.get("name")
        if name:
            return queryset.filter(name__icontains=name)
        return queryset


@login_required
def task_completed(request):
    completed_tasks = Task.objects.filter(is_completed=True)

    query_name = request.GET.get("name", "")
    if query_name:
        filtered_completed_tasks = completed_tasks.filter(name__icontains=query_name)
        context = {"filtered_completed_tasks": filtered_completed_tasks}
        return render(request, "task_manager/task_completed.html", context)

    context = {
        "completed_tasks": completed_tasks,
    }
    return render(request, "task_manager/task_completed.html", context)


@login_required()
def task_not_completed(request):
    not_completed_tasks = Task.objects.filter(is_completed=False)
    context = {
        "not_completed_tasks": not_completed_tasks,
    }
    return render(request, "task_manager/task_not_completed.html", context)


@login_required()
def complete_task(request, pk):
    task_complete = Task.objects.get(pk=pk)
    if not Task.objects.get(pk=pk).is_completed:
        task_complete.is_completed = True
    else:
        task_complete.is_completed = False
    task_complete.save()

    return HttpResponseRedirect(reverse("task_manager:task-not-completed"))


def registration(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            print("Account created successfully!")
            return redirect("/accounts/login/")
        else:
            print("Registration failed!")
    else:
        form = RegistrationForm()

    context = {"form": form}
    return render(request, "accounts/register.html", context)

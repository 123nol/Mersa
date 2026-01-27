from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from .models import Workspace, WorkspaceMembership, Task, require_role, get_membership, can_edit_task
from django.contrib.auth import get_user_model
from django.urls import reverse

@login_required
def workspace_list(request):
    memberships = WorkspaceMembership.objects.filter(user=request.user)
    return render(request, 'task_manager/workspace_list.html', {'memberships': memberships})

@login_required
def workspace_create(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        ws = Workspace.objects.create(name=name, created_by=request.user)
        WorkspaceMembership.objects.create(workspace=ws, user=request.user, role='ADMIN')
        return redirect('task_manager:workspace-detail', ws.id)
    return render(request, 'task_manager/workspace_create.html')

@login_required
def workspace_detail(request, ws_id):
    ws = get_object_or_404(Workspace, id=ws_id)
    # Personal workspace special-case: allow everyone to view, but only creator can manage
    is_personal = ws.name.endswith("'s Personal Workspace") and ws.created_by is not None
    if is_personal:
        tasks = ws.tasks.all()
        # show members only to owner
        members = ws.memberships.select_related('user') if request.user == ws.created_by else []
        return render(request, 'task_manager/workspace_detail.html', {'workspace': ws, 'tasks': tasks, 'members': members, 'is_personal': True})

    # Non-personal workspace: enforce membership for viewing
    require_role(request.user, ws, 'VIEWER')
    tasks = ws.tasks.all()
    members = ws.memberships.select_related('user')
    return render(request, 'task_manager/workspace_detail.html', {'workspace': ws, 'tasks': tasks, 'members': members, 'is_personal': False})

@login_required
def workspace_add_member(request, ws_id):
    ws = get_object_or_404(Workspace, id=ws_id)
    # Prevent adding members to personal workspaces (only owner manages)
    if ws.name.endswith("'s Personal Workspace") and request.user != ws.created_by:
        raise PermissionDenied('Cannot manage members of a personal workspace.')
    require_role(request.user, ws, 'ADMIN')
    User = get_user_model()
    if request.method == 'POST':
        username = request.POST.get('username')
        role = request.POST.get('role')
        user = get_object_or_404(User, username=username)
        WorkspaceMembership.objects.update_or_create(workspace=ws, user=user, defaults={'role': role})
        return redirect('task_manager:workspace-detail', ws.id)
    users = User.objects.exclude(workspace_memberships__workspace=ws)
    return render(request, 'task_manager/workspace_add_member.html', {'workspace': ws, 'users': users})

@login_required
def workspace_remove_member(request, ws_id, user_id):
    ws = get_object_or_404(Workspace, id=ws_id)
    # Prevent removing members from personal workspaces by non-owner
    if ws.name.endswith("'s Personal Workspace") and request.user != ws.created_by:
        raise PermissionDenied('Cannot manage members of a personal workspace.')
    require_role(request.user, ws, 'ADMIN')
    member = get_object_or_404(WorkspaceMembership, workspace=ws, user_id=user_id)
    if member.user == ws.created_by:
        raise PermissionDenied('Cannot remove workspace creator.')
    member.delete()
    return redirect('task_manager:workspace-detail', ws.id)

@login_required
def workspace_change_role(request, ws_id, user_id):
    ws = get_object_or_404(Workspace, id=ws_id)
    # Prevent role changes in personal workspaces by non-owner
    if ws.name.endswith("'s Personal Workspace") and request.user != ws.created_by:
        raise PermissionDenied('Cannot manage members of a personal workspace.')
    require_role(request.user, ws, 'ADMIN')
    member = get_object_or_404(WorkspaceMembership, workspace=ws, user_id=user_id)
    if request.method == 'POST':
        role = request.POST.get('role')
        member.role = role
        member.save()
        return redirect('task_manager:workspace-detail', ws.id)
    return render(request, 'task_manager/workspace_change_role.html', {'workspace': ws, 'member': member})


@login_required
def workspace_delete(request, ws_id):
    ws = get_object_or_404(Workspace, id=ws_id)
    # Only workspace creator can delete
    if request.user != ws.created_by:
        raise PermissionDenied('Only workspace creator can delete this workspace.')
    if request.method == 'POST':
        ws.delete()
        return redirect('task_manager:workspace-list')
    return render(request, 'task_manager/workspace_confirm_delete.html', {'workspace': ws})

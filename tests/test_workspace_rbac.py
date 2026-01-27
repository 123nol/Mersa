import pytest
from django.urls import reverse
from task_manager.models import Workspace, WorkspaceMembership, Task

@pytest.mark.django_db
def test_workspace_creator_is_admin(client, django_user_model):
    user = django_user_model.objects.create_user(username='alice', password='pw')
    client.force_login(user)
    resp = client.post(reverse('task_manager:workspace-create'), {'name': 'TestWS'})
    ws = Workspace.objects.get(name='TestWS')
    assert WorkspaceMembership.objects.filter(workspace=ws, user=user, role='ADMIN').exists()

@pytest.mark.django_db
def test_non_member_cannot_view_workspace(client, django_user_model):
    user = django_user_model.objects.create_user(username='bob', password='pw')
    ws = Workspace.objects.create(name='Hidden', created_by=user)
    url = reverse('task_manager:workspace-detail', args=[ws.id])
    other = django_user_model.objects.create_user(username='eve', password='pw')
    client.force_login(other)
    resp = client.get(url)
    assert resp.status_code == 403 or resp.status_code == 302

@pytest.mark.django_db
def test_member_can_view_workspace(client, django_user_model):
    user = django_user_model.objects.create_user(username='bob', password='pw')
    ws = Workspace.objects.create(name='Visible', created_by=user)
    WorkspaceMembership.objects.create(workspace=ws, user=user, role='MEMBER')
    url = reverse('task_manager:workspace-detail', args=[ws.id])
    client.force_login(user)
    resp = client.get(url)
    assert resp.status_code == 200

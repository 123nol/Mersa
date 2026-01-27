from django.db import migrations

def backfill_workspaces(apps, schema_editor):
    User = apps.get_model('task_manager', 'Worker')
    Task = apps.get_model('task_manager', 'Task')
    Workspace = apps.get_model('task_manager', 'Workspace')
    WorkspaceMembership = apps.get_model('task_manager', 'WorkspaceMembership')

    for user in User.objects.all():
        user_tasks = Task.objects.filter(assignees=user, workspace__isnull=True)
        if user_tasks.exists():
            ws = Workspace.objects.create(name=f"{user.username}'s Personal Workspace", created_by=user)
            WorkspaceMembership.objects.create(workspace=ws, user=user, role='ADMIN')
            user_tasks.update(workspace=ws)

class Migration(migrations.Migration):
    dependencies = [
        ('task_manager', '0004_workspace_rbac'),
    ]
    operations = [
        migrations.RunPython(backfill_workspaces),
    ]

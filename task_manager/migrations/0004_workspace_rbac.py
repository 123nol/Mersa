from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings

def backfill_workspaces(apps, schema_editor):
    User = apps.get_model(settings.AUTH_USER_MODEL)
    Task = apps.get_model('task_manager', 'Task')
    Workspace = apps.get_model('task_manager', 'Workspace')
    WorkspaceMembership = apps.get_model('task_manager', 'WorkspaceMembership')

    # Create a personal workspace per user and assign tasks that list them as assignee.
    user_workspace = {}
    for user in User.objects.all():
        ws = Workspace.objects.create(name=f"{user.username}'s Personal Workspace", created_by=user)
        WorkspaceMembership.objects.create(workspace=ws, user=user, role='ADMIN')
        user_workspace[user.pk] = ws

    # Assign tasks that have assignees to the first assignee's personal workspace
    for task in Task.objects.filter(workspace__isnull=True):
        assignees = list(task.assignees.all())
        if assignees:
            first = assignees[0]
            ws = user_workspace.get(first.pk)
            if not ws:
                ws = Workspace.objects.create(name=f"{first.username}'s Personal Workspace", created_by=first)
                WorkspaceMembership.objects.create(workspace=ws, user=first, role='ADMIN')
                user_workspace[first.pk] = ws
            task.workspace = ws
            task.save()

    # Any remaining tasks without assignees: assign to first user workspace if exists
    fallback_user = User.objects.first()
    if fallback_user:
        fallback_ws = user_workspace.get(fallback_user.pk)
        if not fallback_ws:
            fallback_ws = Workspace.objects.create(name=f"{fallback_user.username}'s Personal Workspace", created_by=fallback_user)
            WorkspaceMembership.objects.create(workspace=fallback_ws, user=fallback_user, role='ADMIN')
            user_workspace[fallback_user.pk] = fallback_ws
        Task.objects.filter(workspace__isnull=True).update(workspace=fallback_ws)

class Migration(migrations.Migration):
    dependencies = [
        ('task_manager', '0003_task_created_at_alter_task_deadline'),
    ]

    operations = [
        migrations.CreateModel(
            name='Workspace',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='created_workspaces', to=settings.AUTH_USER_MODEL)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='WorkspaceMembership',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(choices=[('ADMIN', 'Admin'), ('MANAGER', 'Manager'), ('MEMBER', 'Member'), ('VIEWER', 'Viewer')], max_length=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('workspace', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='memberships', to='task_manager.Workspace')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='workspace_memberships', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('workspace', 'user')},
            },
        ),
        migrations.AddField(
            model_name='task',
            name='workspace',
            field=models.ForeignKey(null=True, blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='tasks', to='task_manager.Workspace'),
        ),
        migrations.RunPython(backfill_workspaces),
        migrations.AlterField(
            model_name='task',
            name='workspace',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tasks', to='task_manager.Workspace'),
        ),
    ]

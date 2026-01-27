from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('task_manager', '0007_merge_20260127_1645'),
    ]

    operations = [
        migrations.AddField(
            model_name='worker',
            name='visit_count',
            field=models.PositiveIntegerField(default=0),
        ),
    ]

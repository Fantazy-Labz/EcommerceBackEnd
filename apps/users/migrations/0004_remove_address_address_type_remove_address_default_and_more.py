# Generated by Django 5.2 on 2025-04-29 02:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_user_username_alter_user_first_name'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='address',
            name='address_type',
        ),
        migrations.RemoveField(
            model_name='address',
            name='default',
        ),
        migrations.AddField(
            model_name='user',
            name='created_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]

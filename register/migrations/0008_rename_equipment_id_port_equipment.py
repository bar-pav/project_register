# Generated by Django 4.2.2 on 2023-06-27 13:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('register', '0007_communication_service_status'),
    ]

    operations = [
        migrations.RenameField(
            model_name='port',
            old_name='equipment_id',
            new_name='equipment',
        ),
    ]

# Generated by Django 4.2.4 on 2023-09-03 13:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('register', '0032_port_frame'),
    ]

    operations = [
        migrations.AddField(
            model_name='port',
            name='frame_name',
            field=models.CharField(blank=True, max_length=30),
        ),
    ]

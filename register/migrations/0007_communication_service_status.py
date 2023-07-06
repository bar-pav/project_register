# Generated by Django 4.2.2 on 2023-06-27 09:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('register', '0006_alter_connection_line_alter_connection_station'),
    ]

    operations = [
        migrations.AddField(
            model_name='communication',
            name='service_status',
            field=models.CharField(choices=[('E', 'enabled'), ('D', 'disabled')], default='E', max_length=1),
        ),
    ]
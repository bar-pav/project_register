# Generated by Django 4.2.2 on 2023-07-03 22:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('register', '0012_communication_create_date_connection_create_date_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='connection',
            name='communication',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, related_name='connection', to='register.communication'),
        ),
    ]
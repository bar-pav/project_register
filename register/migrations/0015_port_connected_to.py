# Generated by Django 4.2.2 on 2023-07-17 21:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('register', '0014_alter_port_equipment_alter_port_port_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='port',
            name='connected_to',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, related_name='to_port', to='register.port'),
        ),
    ]

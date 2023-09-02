# Generated by Django 4.2.4 on 2023-09-01 11:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('register', '0029_alter_equipment_name_alter_equipment_unique_together'),
    ]

    operations = [
        migrations.AlterField(
            model_name='communication',
            name='direction_from',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.RESTRICT, related_name='direction_from', to='register.endpoint'),
        ),
        migrations.AlterField(
            model_name='communication',
            name='direction_to',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.RESTRICT, related_name='direction_to', to='register.endpoint'),
        ),
    ]

# Generated by Django 4.2.4 on 2023-09-03 08:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('register', '0031_alter_communication_unique_together'),
    ]

    operations = [
        migrations.AddField(
            model_name='port',
            name='frame',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, related_name='port', to='register.port'),
        ),
    ]
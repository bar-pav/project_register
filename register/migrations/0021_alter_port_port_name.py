# Generated by Django 4.2.2 on 2023-08-11 11:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('register', '0020_alter_endpoint_unique_together'),
    ]

    operations = [
        migrations.AlterField(
            model_name='port',
            name='port_name',
            field=models.CharField(blank=True, max_length=30),
        ),
    ]
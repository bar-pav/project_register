# Generated by Django 4.2.2 on 2023-07-03 21:44

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('register', '0011_remove_connection_connect'),
    ]

    operations = [
        migrations.AddField(
            model_name='communication',
            name='create_date',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='connection',
            name='create_date',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='communication',
            name='consumer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='communications', to='register.consumer'),
        ),
    ]

# Generated by Django 4.2.2 on 2023-06-25 19:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Equipment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('location', models.CharField(max_length=30)),
                ('note', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='InterfaceType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(help_text='Enter interface type or his speed.', max_length=15, unique=True)),
                ('note', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Port',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('media_type', models.CharField(choices=[('E', 'electrical'), ('O', 'optical')], max_length=1)),
                ('port_name', models.CharField(max_length=15)),
                ('note', models.TextField()),
                ('equipment_id', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='ports', to='register.equipment')),
                ('interface_type', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='ports', to='register.interfacetype')),
            ],
        ),
    ]

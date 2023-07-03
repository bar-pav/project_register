# Generated by Django 4.2.2 on 2023-06-26 15:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('register', '0002_alter_equipment_note_alter_interfacetype_note_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Communication',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150)),
                ('note', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Consumer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('telephone', models.TextField(blank=True, max_length=1000, null=True)),
                ('note', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='EndPoint',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('code', models.CharField(blank=True, max_length=100, null=True)),
                ('note', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.AlterField(
            model_name='equipment',
            name='note',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='interfacetype',
            name='note',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='port',
            name='note',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.CreateModel(
            name='Connection',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('note', models.TextField(blank=True, null=True)),
                ('communication', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='connection', to='register.communication')),
                ('line', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='line', to='register.port')),
                ('station', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='station', to='register.port')),
            ],
        ),
        migrations.AddField(
            model_name='communication',
            name='consumer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='communication', to='register.consumer'),
        ),
        migrations.AddField(
            model_name='communication',
            name='direction_from',
            field=models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='direction_from', to='register.endpoint'),
        ),
        migrations.AddField(
            model_name='communication',
            name='direction_to',
            field=models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='direction_to', to='register.endpoint'),
        ),
        migrations.AddField(
            model_name='port',
            name='opposite_side',
            field=models.ManyToManyField(through='register.Connection', to='register.port'),
        ),
    ]

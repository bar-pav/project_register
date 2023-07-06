# Generated by Django 4.2.2 on 2023-06-26 16:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('register', '0003_communication_consumer_endpoint_alter_equipment_note_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='equipment',
            name='type',
            field=models.CharField(choices=[('A', 'active'), ('P', 'passive')], default='active', max_length=1),
        ),
        migrations.AlterField(
            model_name='port',
            name='media_type',
            field=models.CharField(choices=[('E', 'electrical'), ('O', 'optical')], default='E', max_length=1),
        ),
    ]
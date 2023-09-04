# Generated by Django 4.2.4 on 2023-08-31 07:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('register', '0026_equipment_endpoint_opposite_alter_equipment_location'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='endpoint',
            unique_together=set(),
        ),
        migrations.AlterField(
            model_name='endpoint',
            name='code',
            field=models.CharField(default=1, max_length=100, unique=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='endpoint',
            name='name',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
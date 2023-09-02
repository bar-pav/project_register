# Generated by Django 4.2.2 on 2023-08-30 11:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('register', '0023_alter_equipment_name_alter_equipment_unique_together'),
    ]

    operations = [
        migrations.AlterField(
            model_name='consumer',
            name='name',
            field=models.CharField(max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='equipment',
            name='type',
            field=models.CharField(choices=[('', '---------'), ('-', 'other'), ('E', 'equipment'), ('O', 'optical frame'), ('F', 'electrical frame'), ('V', 'virtual object'), ('S', 'system')], default='-', max_length=1),
        ),
    ]

# Generated by Django 4.2.4 on 2023-09-01 07:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('register', '0028_alter_equipment_unique_together_alter_equipment_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='equipment',
            name='name',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterUniqueTogether(
            name='equipment',
            unique_together={('name', 'type')},
        ),
    ]

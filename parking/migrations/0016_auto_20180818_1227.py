# Generated by Django 2.1 on 2018-08-18 19:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parking', '0015_auto_20180816_2340'),
    ]

    operations = [
        migrations.AlterField(
            model_name='parkingspace',
            name='instructions',
            field=models.CharField(blank=True, help_text='Any instructions that will help customers find the parking spot', max_length=1000),
        ),
    ]

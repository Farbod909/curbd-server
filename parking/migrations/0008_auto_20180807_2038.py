# Generated by Django 2.1 on 2018-08-08 03:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parking', '0007_repeatingavailability_all_day'),
    ]

    operations = [
        migrations.AddField(
            model_name='reservation',
            name='payment_method_info',
            field=models.CharField(max_length=30, null=True),
        ),
        migrations.AlterField(
            model_name='repeatingavailability',
            name='end_time',
            field=models.TimeField(null=True),
        ),
        migrations.AlterField(
            model_name='repeatingavailability',
            name='start_time',
            field=models.TimeField(null=True),
        ),
    ]

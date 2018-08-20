# Generated by Django 2.1 on 2018-08-16 08:18

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('parking', '0012_auto_20180811_1623'),
    ]

    operations = [
        migrations.CreateModel(
            name='ParkingSpaceImage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='images')),
                ('parking_space', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='parking.ParkingSpace')),
            ],
        ),
        migrations.AddField(
            model_name='reservation',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=datetime.datetime(2018, 8, 16, 1, 18, 48, 656256)),
            preserve_default=False,
        ),
    ]
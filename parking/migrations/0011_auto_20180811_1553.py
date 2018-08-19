# Generated by Django 2.1 on 2018-08-11 22:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('parking', '0010_parkingspace_address'),
    ]

    operations = [
        migrations.AlterField(
            model_name='parkingspace',
            name='address',
            field=models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, to='accounts.Address'),
        ),
    ]
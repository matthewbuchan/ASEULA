# Generated by Django 3.0.8 on 2020-09-03 09:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('processing', '0002_restrictionterm_filename'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='restrictionterm',
            name='filename',
        ),
    ]
# Generated by Django 3.0.8 on 2020-10-29 20:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('processing', '0007_auto_20201020_0440'),
    ]

    operations = [
        migrations.AlterField(
            model_name='infofieldarray',
            name='listvalue',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='restrictionterm',
            name='restrictionterm',
            field=models.CharField(max_length=40, null=True),
        ),
        migrations.AlterField(
            model_name='restrictiontitle',
            name='postname',
            field=models.CharField(default=1, max_length=40),
            preserve_default=False,
        ),
    ]

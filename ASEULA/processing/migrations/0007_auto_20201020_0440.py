# Generated by Django 3.0.8 on 2020-10-20 04:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('processing', '0006_restrictiontitle_postname'),
    ]

    operations = [
        migrations.AlterField(
            model_name='restrictiontitle',
            name='postname',
            field=models.CharField(max_length=40, null=True),
        ),
        migrations.AlterField(
            model_name='restrictiontitle',
            name='restriction',
            field=models.CharField(max_length=40),
        ),
    ]
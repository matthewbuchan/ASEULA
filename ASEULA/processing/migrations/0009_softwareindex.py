# Generated by Django 3.0.8 on 2020-11-10 03:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('processing', '0008_auto_20201029_2007'),
    ]

    operations = [
        migrations.CreateModel(
            name='softwareIndex',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('softwarename', models.CharField(max_length=30)),
                ('publishername', models.CharField(blank=True, max_length=30, null=True)),
                ('informationurl', models.CharField(blank=True, max_length=50, null=True)),
                ('flaggedrestrictions', models.TextField(blank=True, null=True)),
                ('checkdate', models.DateTimeField(blank=True, null=True)),
                ('checkby', models.CharField(blank=True, max_length=50, null=True)),
            ],
        ),
    ]
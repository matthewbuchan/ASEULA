# Generated by Django 3.0.8 on 2020-09-03 09:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('processing', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='restrictionterm',
            name='filename',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='processing.processingData'),
            preserve_default=False,
        ),
    ]

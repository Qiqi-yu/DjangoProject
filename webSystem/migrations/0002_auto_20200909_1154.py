# Generated by Django 3.1.1 on 2020-09-09 03:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webSystem', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='equipment',
            name='status',
            field=models.CharField(default='exist', max_length=20),
        ),
        migrations.AlterField(
            model_name='loanapplication',
            name='status',
            field=models.CharField(default='sented', max_length=20),
        ),
        migrations.AlterField(
            model_name='systemuser',
            name='examining_status',
            field=models.CharField(default='Normal', max_length=20),
        ),
    ]
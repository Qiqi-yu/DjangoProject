# Generated by Django 3.1.1 on 2020-09-12 07:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webSystem', '0013_auto_20200912_1543'),
    ]

    operations = [
        migrations.AlterField(
            model_name='systemlog',
            name='operate_time',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]

# Generated by Django 3.1.1 on 2020-09-12 10:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webSystem', '0015_merge_20200912_1803'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mail',
            name='send_time',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]

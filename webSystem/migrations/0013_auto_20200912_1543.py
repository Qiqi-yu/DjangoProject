# Generated by Django 3.1.1 on 2020-09-12 07:43

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('webSystem', '0012_auto_20200912_1541'),
    ]

    operations = [
        migrations.AlterField(
            model_name='systemlog',
            name='operator',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='log_operator', to=settings.AUTH_USER_MODEL),
        ),
    ]

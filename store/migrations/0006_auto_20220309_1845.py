# Generated by Django 3.1 on 2022-03-09 13:15

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('store', '0005_auto_20220309_1845'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='ReviewRatin',
            new_name='ReviewRating',
        ),
    ]

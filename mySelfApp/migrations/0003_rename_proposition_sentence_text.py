# Generated by Django 4.2.7 on 2023-12-24 01:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mySelfApp', '0002_sentence'),
    ]

    operations = [
        migrations.RenameField(
            model_name='sentence',
            old_name='proposition',
            new_name='text',
        ),
    ]

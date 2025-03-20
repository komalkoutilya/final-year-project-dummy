# Generated by Django 5.1.7 on 2025-03-20 06:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mediconnect', '0002_medicaldocument_document_summary'),
    ]

    operations = [
        migrations.AddField(
            model_name='medicaldocument',
            name='document_severity',
            field=models.IntegerField(choices=[(0, '0'), (1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5'), (6, '6'), (7, '7'), (8, '8'), (9, '9')], default=0),
        ),
    ]

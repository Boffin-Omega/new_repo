# Generated by Django 5.1.1 on 2024-10-11 11:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0010_bids_comments_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='bids',
            name='item_id',
            field=models.IntegerField(default=-1),
        ),
    ]

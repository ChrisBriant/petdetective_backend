# Generated by Django 3.1.3 on 2021-10-08 17:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_auto_20211007_0419'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='hash',
            field=models.CharField(default='0xa031992d8c4a943209701340f2249126', max_length=128),
        ),
    ]

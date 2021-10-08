# Generated by Django 3.1.3 on 2021-10-08 17:08

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('pets', '0003_pet_animal'),
    ]

    operations = [
        migrations.CreateModel(
            name='Request',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('accepted', models.BooleanField(default=True)),
                ('description', models.CharField(max_length=500)),
            ],
        ),
        migrations.AddConstraint(
            model_name='case',
            constraint=models.UniqueConstraint(fields=('pet', 'detective'), name='unique_case_pet_detective'),
        ),
        migrations.AddConstraint(
            model_name='petlocation',
            constraint=models.UniqueConstraint(fields=('pet', 'location_type'), name='unique_pet_locationtype'),
        ),
        migrations.AddField(
            model_name='request',
            name='detective',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='request',
            name='pet',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pets.pet'),
        ),
        migrations.AddField(
            model_name='case',
            name='request',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='pets.request'),
            preserve_default=False,
        ),
        migrations.AddConstraint(
            model_name='request',
            constraint=models.UniqueConstraint(fields=('pet', 'detective'), name='unique_request_pet_detective'),
        ),
    ]

# Generated by Django 4.1.2 on 2022-10-25 07:36

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('Hackathon_users', '0001_initial'),
        ('Hackathon_app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='reviews',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_review', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='bookingspace',
            name='parking_space',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='parking_space', to='Hackathon_app.parkingspace'),
        ),
        migrations.AddField(
            model_name='bookingspace',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_booking', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='bookingspace',
            name='vehicle',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='vehicle', to='Hackathon_users.vehicle'),
        ),
    ]

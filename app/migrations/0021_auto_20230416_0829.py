# Generated by Django 2.2 on 2023-04-15 23:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0020_auto_20221227_0236'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='highlight',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='highlight', to='app.Creator'),
        ),
    ]

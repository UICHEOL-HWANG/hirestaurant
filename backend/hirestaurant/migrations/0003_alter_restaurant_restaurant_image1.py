# Generated by Django 4.2.4 on 2024-01-10 15:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hirestaurant', '0002_alter_restaurant_restaurant_image2_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='restaurant',
            name='restaurant_image1',
            field=models.ImageField(upload_to=''),
        ),
    ]

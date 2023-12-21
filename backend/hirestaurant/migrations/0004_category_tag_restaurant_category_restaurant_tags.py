# Generated by Django 4.2.4 on 2023-12-14 15:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('hirestaurant', '0003_restaurant_latitude_restaurant_longitude'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.AddField(
            model_name='restaurant',
            name='category',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='hirestaurant.category'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='restaurant',
            name='tags',
            field=models.ManyToManyField(to='hirestaurant.tag'),
        ),
    ]

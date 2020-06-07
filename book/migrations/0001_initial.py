# Generated by Django 3.0.7 on 2020-06-06 17:42

import book.models
import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Book',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subtitle', models.CharField(max_length=25)),
                ('title', models.CharField(max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='Chapter',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('english', models.TextField(blank=True, default='')),
                ('hanzi', models.TextField(blank=True, default='')),
                ('last_english_update', models.DateField(default=datetime.date.today)),
                ('last_hanzi_update', models.DateField(default=datetime.date.today)),
                ('notes', models.TextField(blank=True, default='')),
                ('number', models.IntegerField(validators=[book.models.validate_chapter_number])),
                ('published', models.BooleanField()),
                ('publish_notes', models.BooleanField()),
                ('title', models.CharField(blank=True, default='', max_length=100)),
                ('book', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='book.Book')),
            ],
        ),
    ]

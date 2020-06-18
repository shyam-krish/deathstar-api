# Generated by Django 3.0.6 on 2020-06-16 21:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0006_artist_insta_followers'),
    ]

    operations = [
        migrations.CreateModel(
            name='Genre',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
            ],
        ),
        migrations.AddField(
            model_name='album',
            name='genre',
            field=models.ManyToManyField(to='api.Genre'),
        ),
        migrations.AddField(
            model_name='artist',
            name='genre',
            field=models.ManyToManyField(to='api.Genre'),
        ),
        migrations.AddField(
            model_name='track',
            name='genre',
            field=models.ManyToManyField(to='api.Genre'),
        ),
    ]

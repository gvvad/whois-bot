# Generated by Django 2.0.4 on 2018-04-26 17:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('whoisbot', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TbotAwaitModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.CharField(max_length=32)),
                ('await', models.CharField(max_length=32)),
            ],
        ),
    ]
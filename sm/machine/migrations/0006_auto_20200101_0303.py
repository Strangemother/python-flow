# Generated by Django 3.0.1 on 2020-01-01 03:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('machine', '0005_auto_20191231_0011'),
    ]

    operations = [
        migrations.CreateModel(
            name='TaskError',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('task_id', models.CharField(max_length=255)),
                ('result', models.TextField()),
            ],
        ),
        migrations.AddField(
            model_name='flow',
            name='errors',
            field=models.ManyToManyField(blank=True, to='machine.TaskError'),
        ),
    ]

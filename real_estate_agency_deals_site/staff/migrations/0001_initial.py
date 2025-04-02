# Generated by Django 5.1.7 on 2025-04-02 06:19

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Appeal',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.CharField(max_length=256, verbose_name='Апелляции')),
                ('date_write', models.DateTimeField(auto_now_add=True)),
                ('verdict', models.CharField(max_length=256, null=True, verbose_name='Вердикт')),
            ],
            options={
                'verbose_name': 'Апелляция',
                'verbose_name_plural': 'Апелляции',
            },
        ),
        migrations.CreateModel(
            name='Complaint',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('feedback_email', models.EmailField(max_length=254, null=True, verbose_name='Почта обратной связи')),
                ('message', models.CharField(max_length=256, verbose_name='Жалоба')),
                ('date_write', models.DateTimeField(auto_now_add=True)),
                ('verdict', models.CharField(max_length=256, null=True, verbose_name='Вердикт')),
            ],
            options={
                'verbose_name': 'Жалоба',
                'verbose_name_plural': 'Жалобы',
                'ordering': ('-date_write',),
            },
        ),
    ]

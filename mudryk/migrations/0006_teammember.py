# Generated by Django 4.2.7 on 2023-12-08 13:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mudryk', '0005_rename_reason_to_choose_reasontochoose_reason_to_choose_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='TeamMember',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='ПІБ')),
                ('photo', models.ImageField(upload_to='team_members')),
                ('description', models.TextField(verbose_name='Опис')),
            ],
            options={
                'verbose_name': 'Член команди',
                'verbose_name_plural': 'Члени команди',
                'ordering': ['id'],
            },
        ),
    ]

# Generated by Django 4.2.7 on 2023-12-27 14:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mudryk', '0019_contact_alter_lesson_options_alter_record_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='price',
            field=models.CharField(max_length=255, verbose_name='Опис вартості курсу чи уроку курсу'),
        ),
    ]

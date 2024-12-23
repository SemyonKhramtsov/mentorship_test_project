# Generated by Django 5.1.3 on 2024-11-27 19:28

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_user_mentor'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='phone_number',
            field=models.CharField(blank=True, max_length=16, null=True, validators=[django.core.validators.RegexValidator(message="Номер должен быть введен в формате: '+999999999'. Допускается до 15 цифр.", regex='^\\+?1?\\d{9,15}$')]),
        ),
    ]

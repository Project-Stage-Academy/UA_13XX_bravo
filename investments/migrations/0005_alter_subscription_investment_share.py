# Generated by Django 5.1.6 on 2025-04-03 12:02

import django.core.validators
from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('investments', '0004_alter_subscription_investment_share'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subscription',
            name='investment_share',
            field=models.DecimalField(decimal_places=2, help_text='Percentage of total investment (e.g., 25.50 for 25.5%)', max_digits=5, validators=[django.core.validators.MinValueValidator(Decimal('0.01')), django.core.validators.MaxValueValidator(Decimal('100.00'))]),
        ),
    ]

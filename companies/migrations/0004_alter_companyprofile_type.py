# Generated by Django 5.1.6 on 2025-03-26 18:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0003_merge_20250324_1202'),
    ]

    operations = [
        migrations.AlterField(
            model_name='companyprofile',
            name='type',
            field=models.CharField(blank=True, choices=[('startup', 'Startup'), ('enterprise', 'Enterprise'), ('nonprofit', 'Non-Profit')], max_length=255, null=True),
        ),
    ]

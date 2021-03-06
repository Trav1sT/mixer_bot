# Generated by Django 3.1.4 on 2021-03-17 18:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('abcd', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='node',
            name='name',
            field=models.TextField(),
        ),
        migrations.AlterUniqueTogether(
            name='node',
            unique_together={('name', 'owner')},
        ),
    ]

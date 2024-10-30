# Generated by Django 5.0.2 on 2024-10-06 18:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exam', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='test',
            name='duration',
            field=models.IntegerField(default=95, verbose_name='Duración de Cada Pregunta (segundos)'),
        ),
        migrations.AddField(
            model_name='test',
            name='start_time',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Hora de Inicio'),
        ),
    ]


from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='data',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('institute', models.CharField(max_length=300)),
                ('program', models.CharField(max_length=500)),
                ('seat_type', models.CharField(max_length=300)),
                ('gender', models.CharField(max_length=300)),
                ('opening_rank', models.IntegerField()),
                ('closing_rank', models.IntegerField()),
                ('year', models.IntegerField()),
                ('roundNo', models.IntegerField()),
                ('preparatory', models.BooleanField(default=False)),
                ('institute_type', models.CharField(default='GFTI', max_length=300)),
            ],
        ),
    ]

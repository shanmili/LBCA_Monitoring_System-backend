from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='SchoolYear',
            fields=[
                ('school_year_id', models.AutoField(primary_key=True, serialize=False)),
                ('year', models.CharField(max_length=20, unique=True)),
                ('is_current', models.BooleanField(default=False)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
            ],
            options={
                'ordering': ['-school_year_id'],
            },
        ),
    ]

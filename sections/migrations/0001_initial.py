import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('grade_levels', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Section',
            fields=[
                ('section_id', models.AutoField(primary_key=True, serialize=False)),
                ('section_code', models.CharField(max_length=20, unique=True)),
                ('name', models.CharField(max_length=30)),
                ('grade_level', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='sections',
                    to='grade_levels.gradelevel'
                )),
            ],
            options={
                'ordering': ['grade_level', 'section_id'],
            },
        ),
    ]

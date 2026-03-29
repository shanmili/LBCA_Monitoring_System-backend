from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='GradeLevel',
            fields=[
                ('grade_level_id', models.AutoField(primary_key=True, serialize=False)),
                ('level', models.CharField(max_length=10, unique=True)),
                ('name', models.CharField(max_length=20)),
            ],
            options={
                'ordering': ['grade_level_id'],
            },
        ),
    ]

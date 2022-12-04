# Generated by Django 4.1.3 on 2022-12-04 21:58

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import game.models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Board',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('height', models.IntegerField(default=15)),
                ('width', models.IntegerField(default=15)),
                ('height_offset', models.IntegerField(default=0)),
                ('width_offset', models.IntegerField(default=0)),
                ('started_tz', models.DateTimeField(default=game.models.default_started_tz)),
                ('closed_tz', models.DateTimeField(default=game.models.default_closed_tz)),
            ],
        ),
        migrations.CreateModel(
            name='Letter',
            fields=[
                ('symbol', models.CharField(max_length=1, primary_key=True, serialize=False)),
                ('value', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Word',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('word', models.CharField(max_length=12)),
                ('start_x', models.IntegerField()),
                ('start_y', models.IntegerField()),
                ('vertical', models.BooleanField(default=False)),
                ('points', models.IntegerField()),
                ('fetched_info', models.JSONField(blank=True, default=None, null=True)),
                ('board', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='game.board')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='UserLetter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('used', models.BooleanField(default=False)),
                ('board', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='game.board')),
                ('letter', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='game.letter')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Cell',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('x', models.IntegerField()),
                ('y', models.IntegerField()),
                ('multiplier', models.IntegerField(default=1)),
                ('word_multiplier', models.BooleanField(default=False)),
                ('board', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='game.board')),
                ('symbol', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.RESTRICT, to='game.letter')),
            ],
        ),
        migrations.AddConstraint(
            model_name='cell',
            constraint=models.UniqueConstraint(fields=('board', 'x', 'y'), name='unique_cell_per_board'),
        ),
    ]

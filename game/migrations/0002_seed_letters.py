# Generated by Django 4.1.3 on 2022-12-03 20:16
import itertools
from django.db import migrations
from game.models import Letter


# Seeds the database with initial values
def sneed(apps, schema_editor):
    #  Populate letter table
    letters = [
        *zip(itertools.repeat(1), ['A', 'E', 'I', 'L', 'N', 'O', 'R', 'S', 'T', 'U']),
        *zip(itertools.repeat(2), ['D', 'G']),
        *zip(itertools.repeat(3), ['B', 'C', 'M', 'P']),
        *zip(itertools.repeat(4), ['F', 'H', 'V', 'W', 'Y']),
        *zip(itertools.repeat(5), ['K']),
        *zip(itertools.repeat(8), ['J', 'X']),
        *zip(itertools.repeat(10), ['Q', 'Z']),
    ]

    for letter in letters:
        letter = Letter(value=letter[0], symbol=letter[1])
        letter.save()


class Migration(migrations.Migration):
    dependencies = [
        ('game', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(sneed),
    ]
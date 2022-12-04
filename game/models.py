from __future__ import annotations

import datetime
import uuid

from django.contrib.auth.models import User
from django.db import models

from game.constants import MAX_WORD_LENGTH, MAX_USER_LETTERS, INIT_BOARD_DIMENSION, GAME_LENGTH_HOURS
from game.exceptions import NoUserLetterException


def default_started_tz():
    return datetime.datetime.now(datetime.timezone.utc)


def default_closed_tz():
    return default_started_tz() + datetime.timedelta(hours=GAME_LENGTH_HOURS)


# Represents a single game board
class Board(models.Model):
    # The Board number
    id = models.AutoField(primary_key=True)

    # The size of the board
    height = models.IntegerField(default=INIT_BOARD_DIMENSION)
    width = models.IntegerField(default=INIT_BOARD_DIMENSION)

    # Offsets when tiles are placed below 0
    height_offset = models.IntegerField(default=0)
    width_offset = models.IntegerField(default=0)

    # The timestamp the board started
    started_tz = models.DateTimeField(default=default_started_tz)

    # The timestamp the board closed
    closed_tz = models.DateTimeField(default=default_closed_tz)

    @staticmethod
    def create() -> Board:
        board = Board()
        board.save()

        for x in range(INIT_BOARD_DIMENSION):
            for y in range(INIT_BOARD_DIMENSION):
                cell = Cell(board=board, x=x, y=y)
                cell.save()
        return board

    @staticmethod
    def get_current() -> Board | None:
        time = datetime.datetime.now(datetime.timezone.utc)
        return Board.objects.filter(started_tz__lt=time, closed_tz__gt=time).first()

    # conditionally widens the board if end position is within border threshold
    def widen_from_placement(self, start: list[int], end: list[int]):
        min_x = MAX_USER_LETTERS
        max_x = self.width - MAX_USER_LETTERS - 1 - self.width_offset

        width_widen = 0
        if start[0] < min_x:
            width_widen = start[0] - min_x
        elif end[0] > max_x:
            width_widen = end[0] - max_x

        min_y = MAX_USER_LETTERS
        max_y = self.height - MAX_USER_LETTERS - 1 - self.height_offset

        height_widen = 0
        if start[1] < min_y:
            height_widen = start[1] - min_y
        elif end[1] > max_y:
            height_widen = end[1] - max_y

        self.widen(width_widen, height_widen)

    # Widen board by set amount
    def widen(self, width: int, height: int):
        print('expand,', width, height)

        # How many cells are being added in each dimension
        mag_x = abs(width)
        mag_y = abs(height)

        # Where to begin adding cells
        #   If dim is less than 0, we're expanding negative, else add to last
        start_x = -self.width_offset + width if width < 0 else self.width
        start_y = -self.height_offset + height if height < 0 else self.height

        # For each new cell in x direction
        for i in range(mag_x):
            x = start_x + i
            # For each cell in height, add a cell for the added width
            for y in range(self.height):
                try:
                    cell = Cell(board=self, x=x, y=y - self.height_offset)
                    print(f'Expanding X: ({x},{y})')
                    cell.save()
                except Exception:
                    # todo something?
                    print(f'Cell ({x}, {y}) already exists')

        # Update the width
        self.width += mag_x
        if width < 0:
            self.width_offset += mag_x

        # For each new cell in y direction
        for i in range(mag_y):
            y = start_y + i
            # For each cell in width, add a cell for the added height
            for x in range(self.width):
                try:
                    cell = Cell(board=self, x=x - self.width_offset, y=y)
                    print(f'Expanding Y: ({x},{y})')
                    cell.save()
                except Exception:
                    # todo something?
                    print(f'Cell ({x}, {y}) already exists')

        # Update the width
        self.height += mag_y
        if height < 0:
            self.height_offset += mag_y

        self.save()


# Model to hold all the words
class Word(models.Model):
    # ID of the user the word belongs to
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)

    # ID of the board the word belongs to
    board = models.ForeignKey(Board, on_delete=models.CASCADE)

    # The word itself
    word = models.CharField(max_length=MAX_WORD_LENGTH)

    # The position of the first letter of the word
    start_x = models.IntegerField()
    start_y = models.IntegerField()

    # The direction of the word
    vertical = models.BooleanField(default=False)

    # The number of points awarded
    points = models.IntegerField()

    # The JSON result from dictionary api
    fetched_info = models.JSONField(default=None, blank=True, null=True)

    def __str__(self):
        return self.word


# Model to hold value for each letter
class Letter(models.Model):
    symbol = models.CharField(max_length=1, primary_key=True)
    value = models.IntegerField()

    def __str__(self):
        return self.symbol


# Cell of the board
class Cell(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    board = models.ForeignKey(Board, on_delete=models.CASCADE)
    x = models.IntegerField()
    y = models.IntegerField()

    # Multiplier to apply to letter value
    # If multiplier & word applies to word, else if multiplier it applies to letter
    multiplier = models.IntegerField(default=1)
    word_multiplier = models.BooleanField(default=False)

    # Letter that is placed in the cell
    symbol = models.ForeignKey(Letter, on_delete=models.RESTRICT, default=None, blank=True, null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['board', 'x', 'y'], name='unique_cell_per_board'
            )
        ]

    def save(self, *args, **kwargs):
        # x = abs(self.x)
        # y = abs(self.y)
        # triple_word = any([
        #     x % 7 == 0 and y % 7 == 0
        # ])
        # double_word = any([
        #     x == y
        # ])
        # triple_letter = any([
        #     (x == 1) and (y != 0 and (y % 5 == 0 or y % 9 == 0 or y % 13 == 0)),
        #     (y == 1) and (x != 0 and (x % 5 == 0 or x % 9 == 0 or x % 13 == 0)),
        #     (x != 0 and (x % 5 == 0 or x % 9 == 0 or x % 13 == 0)) and (
        #                 y != 0 and (y % 5 == 0 or y % 9 == 0 or y % 13 == 0))
        # ])
        # double_letter = any([
        #
        # ])
        # if triple_word:
        #     self.multiplier = 3
        #     self.word_multiplier = True
        # elif double_word:
        #     self.multiplier = 2
        #     self.word_multiplier = True
        # elif triple_letter:
        #     self.multiplier = 3
        #
        # elif double_letter:
        #     self.multiplier = 2

        super(Cell, self).save(args, kwargs)

    def __str__(self):
        return str(self.__dict__)

    @staticmethod
    def find_cell(cells: list[Cell], x: int, y: int) -> Cell | None:
        cell_candidates = list(filter(lambda c: c.x == x and c.y == y, cells))
        if len(cell_candidates) != 1:
            return None
        return cell_candidates[0]


# Association of user to letters per game
# TODO: restrict letters per user at db level
class UserLetter(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_index=True)
    board = models.ForeignKey(Board, on_delete=models.CASCADE)
    letter = models.ForeignKey(Letter, on_delete=models.RESTRICT)
    used = models.BooleanField(default=False)

    def __str__(self):
        return str(self.letter)

    @staticmethod
    def create_user_letters(board: Board, user: User, num: int):
        user_letters = []

        # give the user at least one vowel
        while len(user_letters) < MAX_USER_LETTERS or not any(
                ul.letter.symbol in ['A', 'E', 'I', 'O', 'U'] for ul in user_letters):
            user_letters = list(UserLetter.objects.filter(board=board, user=user, used=False))
            for i in range(num):
                letter = Letter.objects.order_by('?').first()
                user_letter = UserLetter(user=user, board=board, letter=letter)
                user_letters.append(user_letter)

        for ul in user_letters:
            ul.save()
        return user_letters

    @staticmethod
    def get_user_letters(board: Board, user: User):
        user_letters = list(UserLetter.objects.filter(board=board, user=user, used=False))
        # If we don't have letters, create some for the user
        if len(user_letters) < MAX_USER_LETTERS:
            create_num = MAX_USER_LETTERS - len(user_letters)
            user_letters = UserLetter.create_user_letters(board, user, create_num)
        return user_letters

    @staticmethod
    def use_letters(board: Board, user: User, letters: list[Letter]):
        for l in letters:
            user_letter = UserLetter.objects.filter(board=board, user=user, used=False, letter=l).first()
            user_letter.used = True
            user_letter.save()

    @staticmethod
    def validate_letters(board: Board, user: User, letters: list[Letter]):
        for l in letters:
            user_letters = UserLetter.objects.filter(board=board, user=user, used=False)
            user_letter = user_letters.filter(letter=l).first()
            if not user_letter:
                raise NoUserLetterException()
            user_letter.used = True

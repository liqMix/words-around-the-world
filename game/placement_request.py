from __future__ import annotations

from game.models import Letter, UserLetter, Board, Word, User, Cell
from game.constants import DICTIONARY_API, API_WORD_TOKEN
from game.exceptions import *
import requests


class PlacementRequest:
    user_letter: UserLetter
    letter: Letter
    x: int
    y: int

    def __init__(self, board: Board, place_req, user: User):
        self.user_letter = UserLetter.objects.filter(user=user, id=place_req['id']).first()
        if not self.user_letter:
            raise Exception('User letter not found')
        self.letter = Letter.objects.filter(symbol=self.user_letter.letter.symbol).first()
        if not self.letter:
            raise Exception('Letter not found')
        self.x = place_req['placed_x'] - board.width_offset
        self.y = place_req['placed_y'] - board.height_offset

    def __str__(self):
        return str(self.__dict__)

    @staticmethod
    def determine_direction(place_reqs: list[PlacementRequest]):
        if len(place_reqs) < 1:
            raise Exception("Can't determine direction")

    @staticmethod
    def validate_placements(place_reqs: list[PlacementRequest], board: Board):
        # Must be placing something
        if len(place_reqs) < 1:
            raise NoPlacementException()

        num_words = board.word_set.count()
        # Must place at center if first word
        if num_words == 0:
            center_x = board.width // 2
            center_y = board.height // 2
            if not any(p.x == center_x and p.y == center_y for p in place_reqs):
                raise FirstPlacementException()
        else:
            # Must attach to a word if not first word
            attach = False
            for p in place_reqs:
                if attach:
                    break
                for i in [-1, 0, 1]:
                    for j in [-1, 0, 1]:
                        cell = Cell.objects.filter(board=board, x=p.x + i, y=p.y + j).first()
                        print(cell)
                        if cell and cell.symbol:
                            attach = True
            if not attach:
                raise WordAttachException()

        x = place_reqs[0].x
        y = place_reqs[0].y
        for p in place_reqs:
            # All placed cells are unoccupied
            cell = Cell.objects.filter(board=board, x=p.x, y=p.y).first()
            if cell.symbol:
                raise OccupiedTileException()

            # Placed cells are sequential either vertically or horizontally
            # This means all placements must either have matching X or Y values
            if p.x != x and p.y != y:
                raise TileDirectionException()

    @staticmethod
    def find_words(p: PlacementRequest, cells):
        words = []

        # if cell above or below is occupied, find vertical word
        up_cell = Cell.find_cell(cells, p.x, p.y - 1)
        down_cell = Cell.find_cell(cells, p.x, p.y + 1)
        vertical = (up_cell and up_cell.symbol) or (down_cell and down_cell.symbol)
        if vertical:
            word = p.letter.symbol
            start = [p.x, p.y]
            while up_cell and up_cell.symbol:
                start = [up_cell.x, up_cell.y]
                word = up_cell.symbol.symbol + word
                up_cell = Cell.find_cell(cells, start[0], start[1] - 1)
            while down_cell and down_cell.symbol:
                end = [down_cell.x, down_cell.y]
                word = word + down_cell.symbol.symbol
                down_cell = Cell.find_cell(cells, end[0], end[1] + 1)
            words.append([start, word, True])

        left_cell = Cell.find_cell(cells, p.x - 1, p.y)
        right_cell = Cell.find_cell(cells, p.x + 1, p.y)
        horizontal = (left_cell and left_cell.symbol) or (right_cell and right_cell.symbol)
        if horizontal:
            word = p.letter.symbol
            start = [p.x, p.y]
            while left_cell and left_cell.symbol:
                start = [left_cell.x, left_cell.y]
                word = left_cell.symbol.symbol + word
                left_cell = Cell.find_cell(cells, start[0] - 1, start[1])
            while right_cell and right_cell.symbol:
                end = [right_cell.x, right_cell.y]
                word = word + right_cell.symbol.symbol
                right_cell = Cell.find_cell(cells, end[0] + 1, end[1])
            words.append([start, word, False])
        print(words)
        return words

    @staticmethod
    def get_placed_words(place_reqs: list[PlacementRequest], board: Board, cells: list[Cell], user: User) -> list[Word]:
        # place requested letters in cells
        for p in place_reqs:
            cell = Cell.find_cell(cells, p.x, p.y)
            if not cell.symbol:
                cell.symbol = p.letter

        # find start and end of placed letters
        start = None
        end = None
        for p in place_reqs:
            if not start or p.x < start[0] or p.y < start[1]:
                start = [p.x, p.y]
            if not end or p.x > end[0] or p.y > end[1]:
                end = [p.x, p.y]

        # no spaces allowed between placed letters
        if len(place_reqs) > 1:
            temp = [*start]
            while temp[0] < end[0]:
                c = Cell.find_cell(cells, temp[0], temp[1])
                if not c or not c.symbol:
                    raise EmptySpaceException(c)
                temp[0] += 1
            while temp[1] < end[1]:
                c = Cell.find_cell(cells, temp[0], temp[1])
                if not c or not c.symbol:
                    raise EmptySpaceException(c)
                temp[1] += 1

        words = []
        for p in place_reqs:
            new_words = PlacementRequest.find_words(p, cells)
            for w in new_words:
                if w not in words:
                    words.append(w)
        added_words = []
        for w in words:
            start = w[0]
            word = w[1]
            vertical = w[2]
            word_json = PlacementRequest.validate_word(word)
            word = Word(word=word, start_x=start[0], start_y=start[1], user=user, board=board, vertical=vertical,
                        points=0, fetched_info=word_json)
            word.save()
            added_words.append(word)
        for c in cells:
            c.save()
        board.widen_from_placement(start, end)
        return added_words

    @staticmethod
    def validate_word(word: str):
        req = requests.get(
            url=DICTIONARY_API.replace(API_WORD_TOKEN, word),
            verify=False,
        )
        if not req.ok:
            raise Exception(f'"{word}" is not a word (about this to your mother)')
        return req.json()

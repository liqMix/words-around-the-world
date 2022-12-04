class NoCurrentBoardException(Exception):
    def __str__(self):
        return 'No current board available'


class EmptySpaceException(Exception):

    def __init__(self, cell):
        super(EmptySpaceException, self).__init__()
        self.violating_cell = cell

    def __str__(self):
        return f'All placed letters must be a part of a contiguous word. ({self.violating_cell.x}, {self.violating_cell.y}) is empty.'


class NoUserLetterException(Exception):
    def __str__(self):
        return 'Attempted to use a letter the user does not have'


class NoPlacementException(Exception):
    def __str__(self):
        return 'No tile placement requests'


class FirstPlacementException(Exception):
    def __str__(self):
        return 'First word must place tile in center cell'


class TileDirectionException(Exception):
    def __str__(self):
        return 'Tiles must be placed in one direction'


class OccupiedTileException(Exception):
    def __str__(self):
        return 'Cell already has a tile'


class WordAttachException(Exception):
    def __str__(self):
        return 'New word must attach to existing word'

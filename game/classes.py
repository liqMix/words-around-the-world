from game.models import User as UserModel, Board, Cell, Word
from game.exceptions import NoCurrentBoardException


class User:
    user: UserModel

    def __init__(self, email: str):
        self.user = UserModel.objects.filter(email=email).first()

    def has_played(self, board: Board) -> bool:
        # noot noot
        return not not Word.objects.filter(board=board, user=self.user).first()


class Game:
    board: Board
    cells: list[Cell]

    @staticmethod
    def expect_current_board() -> Board:
        board = Board.get_current()
        if not board:
            raise NoCurrentBoardException()
        return board

    def get_user_words(self, user: UserModel) -> list[Word]:
        return Word.objects.filter(board=self.board, user=user).first()

    def cells_as_grid(self) -> list[list[Cell]]:
        cells_copy = [*self.cells]
        for cell in cells_copy:
            cell.x += self.board.width_offset
            cell.y += self.board.height_offset
        cells = [[] for _ in range(self.board.height + self.board.height_offset + 1)]
        for cell in cells_copy:
            try:
                cells[cell.y].append(cell)
            except Exception as e:
                print(self.board.height)
                print(self.board.height_offset)
                print(cell)
                raise e
        return cells

    def __init__(self):
        self.board = self.expect_current_board()
        self.cells = Cell.objects.filter(board=self.board).order_by('y', 'x')

    def __str__(self):
        string = 'Board: ' + str(self.board) + '\n' + 'Cells: \n'
        for i in self.cells:
            string += '\t' + str(i) + '\n'
        return string

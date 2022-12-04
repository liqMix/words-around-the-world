from django.shortcuts import render
from django.views import View
from django.http import HttpResponse, HttpRequest, HttpResponseForbidden
from game.classes import Game
from game.models import Board, UserLetter
from game.placement_request import PlacementRequest
from game.exceptions import NoCurrentBoardException
import json


class GameView(View):

    # Displays current game view, user tiles, etc
    @staticmethod
    def get(request: HttpRequest):
        try:
            game = Game()
        except NoCurrentBoardException:
            Board.create()
            game = Game()
        cell_grid = game.cells_as_grid()
        letters = []
        if not request.user.is_anonymous:
            letters = UserLetter.get_user_letters(board=game.board, user=request.user)
        print(letters)
        context = {
            'board': game.board,
            'cells': cell_grid,
            'user': request.user,
            'letters': letters
        }
        return render(request, 'game/index.html', context)

    # Recieve a request to add a word from a user
    @staticmethod
    def post(request: HttpRequest):
        if request.user.is_anonymous:
            return HttpResponseForbidden()

        game = Game()
        placed_body = json.loads(request.body)
        placement_requests = []
        for i in placed_body['placed']:
            place_req = PlacementRequest(game.board, i, request.user)
            placement_requests.append(place_req)

        game = Game()
        PlacementRequest.validate_placements(placement_requests, game.board)
        words = PlacementRequest.get_placed_words(placement_requests, game.board, game.cells, request.user)
        UserLetter.use_letters(game.board, request.user, [pr.letter for pr in placement_requests])
        for w in words:
            print(w.word)
        return HttpResponse("ye")

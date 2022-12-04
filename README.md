# words-around-the-world
It's like a word game but everyone plays at the same time

## install
### create venv
```
python -m venv venv
```

### activat ur veenv
wimdows
```
venv/Scripts/activate.bat
```

### run serber
```
python manage.py runserver
```

### add ur user (for now)
```
python manage.py createsuperuser
```

### clic loggin on game pag
```
http://127.0.0.1:8000/game/
```

## todo
- render board
  - multipliers
  - allow selecting placed letters -> display the words they are a part of
- render user
  - placed words and values and total score
- render scoreboard
  - top users in game
- add user page
  - shows all words placed per game
  - overall score
  - allow profile image
- replace http interaction with websockets
- fix board growth
- add twitter/google sso for user profile
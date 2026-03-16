def verify_game(game, lists):
    """
    Devuelve True si al menos 2 listas contienen el juego.
    """
    matches = 0
    game_title = game["title"].lower()
    for l in lists:
        for g in l:
            if game_title in g["title"].lower():
                matches += 1
                break
    return matches >= 2
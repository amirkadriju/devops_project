if __name__ == '__main__':

    game = Dog()
    idx_player_active = 0
    player = game.state.list_player[game.state.idx_player_active]
    player.list_card = [Card(suit='♣', rank='7'), Card(suit='♦', rank='7'), Card(suit='♥', rank='7'), Card(suit='♠', rank='7'), Card(suit='♠', rank='K')]
    print(player.list_card)
    player.list_marble[0] = Marble(pos=str(0), is_save=True)
    print(player.list_marble[0])
    print(game.state.idx_player_active)

    actions = game.get_list_action()
    print(actions)
    print(game.state.idx_player_active)

    print(actions[0])
    action = game.apply_action(actions[0])
    print(game.state.idx_player_active)
    print(player.list_marble[0])
    print(game.state.card_active)
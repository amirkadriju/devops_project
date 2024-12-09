# test file 


import pytest
from server.py.dog import Dog, GamePhase, Card, Marble, PlayerState, Action, GameState


def test_dog_initialization():
    """Test the initialization of the Dog game."""
    game = Dog()

    # Verify the number of players
    assert game.state.cnt_player == 4, "Number of players should be 4."

    # Verify the game phase is RUNNING
    assert game.state.phase == GamePhase.RUNNING, "Game phase should be 'RUNNING'."

    # Verify the round count is 1
    assert game.state.cnt_round == 1, "Round count should start at 1."

    # Verify the card exchange boolean is False
    assert not game.state.bool_card_exchanged, "Card exchange should be False at initialization."

    # Verify the active player index
    assert 0 <= game.state.idx_player_started < 4, "Starting player index should be valid."
    assert game.state.idx_player_active == game.state.idx_player_started, "Active player should match the starting player."

    # Verify each player has 6 cards
    for player in game.state.list_player:
        assert len(player.list_card) == 6, f"{player.name} should have 6 cards at the start."

    # Verify the draw pile has the correct number of cards
    expected_draw_count = len(game.state.LIST_CARD) - 4 * 6
    assert len(game.state.list_card_draw) == expected_draw_count, "Draw pile should have the correct number of cards."

    # Verify the discard pile is empty
    assert len(game.state.list_card_discard) == 0, "Discard pile should be empty at initialization."

    # Verify initial marble positions for each player
    positions = {
        "Blue": ["64", "65", "66", "67"],
        "Green": ["72", "73", "74", "75"],
        "Red": ["80", "81", "82", "83"],
        "Yellow": ["88", "89", "90", "91"]
    }

    for player in game.state.list_player:
        player_positions = [marble.pos for marble in player.list_marble]
        assert player_positions == positions[player.name], f"{player.name} marbles should be in the correct starting positions."

def test_card_steps():
    """Test the card steps calculation."""
    game = Dog()

    assert game.state.get_card_steps("2") == 2
    assert game.state.get_card_steps("Q") == 12
    assert game.state.get_card_steps("K") == 13


def test_apply_action():
    """Test applying an action."""
    game = Dog()
    initial_active_player = game.state.idx_player_active
    actions = game.get_list_action()
    if actions:
        game.apply_action(actions[0])
        assert game.state.idx_player_active != initial_active_player, "Active player should change after applying an action."


def test_exchange_cards():
    """Test the card exchange functionality."""
    game = Dog()
    game.state.bool_card_exchanged = False
    game.exchange_cards()
    assert game.state.bool_card_exchanged, "Card exchange flag should be set to True after exchange."




if __name__ == "__main__":
    pytest.main()

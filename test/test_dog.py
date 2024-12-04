# test file 


import pytest
from server.py.dog import Dog, GamePhase, Card


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

def test_move_with_ACE_from_start():
    """Test moving a marble with an Ace card from the start position."""

    # Initialize the game
    game = Dog()

    # Setup: Move the first marble of the active player to the start position (e.g., "0")
    active_player = game.state.list_player[game.state.idx_player_active]
    active_player.list_marble[0].pos = "0"

    # Verify the marble is at position "0"
    assert active_player.list_marble[0].pos == "0", "Marble should be at position 0."

    # Assign an Ace card (Ace of Spades) to the active player's hand
    ace_card = Card(suit='♠', rank='A')
    active_player.list_card = [ace_card]

    # Verify that the player has the Ace card
    assert active_player.list_card[0].rank == 'A' and active_player.list_card[0].suit == '♠', \
        "Player should have the Ace of Spades in hand."

    # Get valid actions for the Ace card
    valid_actions = game.get_list_action()

    # Debug: Print the valid actions for verification
    print(f"Valid actions: {[f'From {action.pos_from} to {action.pos_to}' for action in valid_actions]}")

    # Expected positions to move to with an Ace card from position "0" (1 and 11)
    expected_positions = ["1", "11"]

    # Verify that the valid actions include moving to positions 1 and 11
    for pos in expected_positions:
        action_found = any(action.pos_to == pos for action in valid_actions)
        assert action_found, f"Expected move to position {pos} not found for Ace card."

    # Verify that the move actions originate from position "0"
    assert all(action.pos_from == "0" for action in valid_actions if action.pos_to in expected_positions), \
        "All moves should originate from position 0 for the Ace card."


if __name__ == "__main__":
    pytest.main()

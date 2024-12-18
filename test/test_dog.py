# test file 


import pytest
from unittest.mock import MagicMock, patch
from server.py.dog import Dog, GamePhase, Card, Marble, PlayerState, Action, GameState, RandomPlayer


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
        "Blue": [64, 65, 66, 67],
        "Green": [72, 73, 74, 75],
        "Red": [80, 81, 82, 83],
        "Yellow": [88, 89, 90, 91]
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


def setup_game_with_cards():
    """Helper function to create a game with players and assigned cards, marbles, and teammates."""
    game = Dog()
    blue_marbles = [Marble(pos=i, is_save=False) for i in Dog.KENNEL["Blue"]]
    green_marbles = [Marble(pos=i, is_save=False) for i in Dog.KENNEL["Green"]]
    red_marbles = [Marble(pos=i, is_save=False) for i in Dog.KENNEL["Red"]]
    yellow_marbles = [Marble(pos=i, is_save=False) for i in Dog.KENNEL["Yellow"]]
    game.state.list_player = [
        PlayerState(name="Blue", list_card=[Card(suit='♠', rank='A')], list_marble=blue_marbles, teamMate="Green"),
        PlayerState(name="Yellow", list_card=[Card(suit='♥', rank='2')], list_marble=green_marbles, teamMate="Red"),
        PlayerState(name="Green", list_card=[Card(suit='♦', rank='3')], list_marble=red_marbles, teamMate="Blue"),
        PlayerState(name="Red", list_card=[Card(suit='♣', rank='4')], list_marble=yellow_marbles, teamMate="Yellow")
    ]
    
    return game

def test_card_exchange():
    game = setup_game_with_cards()
    # Save the initial cards to verify after exchange
    initial_cards = {player.name: player.list_card[0] for player in game.state.list_player}

    # Perform the card exchange
    game.exchange_cards()

    # Assertions to check if cards are correctly exchanged between teammates
    assert game.state.list_player[0].list_card[0] == initial_cards["Green"], "Blue did not receive Green's card."
    assert game.state.list_player[2].list_card[0] == initial_cards["Blue"], "Green did not receive Blue's card."
    assert game.state.list_player[1].list_card[0] == initial_cards["Red"], "Yellow did not receive Red's card."
    assert game.state.list_player[3].list_card[0] == initial_cards["Yellow"], "Red did not receive Yellow's card."

    # Check the boolean flag for card exchange is set to True
    assert game.state.bool_card_exchanged is True, "Card exchange flag should be set to True after exchange."

def test_distribute_cards():
    game = setup_game_with_cards()
    # Set a specific round for testing
    game.state.cnt_round = 1  # Expect 6 cards each this round

    # Mock reshuffle to just refill the draw deck if called
    game.reshuffle_if_empty = MagicMock(side_effect=lambda: game.state.list_card_draw.extend([Card(suit='♣', rank=str(num)) for num in range(1, 20)]))

    # Perform the card distribution
    game.distribute_cards()

    # Assert each player has the correct number of cards
    for player in game.state.list_player:
        assert len(player.list_card) == 6, f"{player.name} should have 6 cards."

    # Test subsequent rounds to ensure decrement works
    game.state.cnt_round = 2  # Expect 5 cards each this round
    game.distribute_cards()
    for player in game.state.list_player:
        assert len(player.list_card) == 5, f"{player.name} should have 5 cards."

    # Ensure reshuffle_if_empty is called if draw deck has insufficient cards
    game.state.list_card_draw = []  # Empty draw pile
    game.state.cnt_round = 5  # Expect 2 cards each, trigger reshuffle
    game.distribute_cards()
    assert len(game.state.list_card_draw) > 0, "Draw pile should be refilled after reshuffle."
    for player in game.state.list_player:
        assert len(player.list_card) == 2, f"{player.name} should have 2 cards."


def test_end_round():
    game = setup_game_with_cards()

    # Initial state conditions for verification
    initial_round = game.state.cnt_round
    initial_starter = game.state.idx_player_started
    initial_active = game.state.idx_player_active
    initial_card_exchange_status = game.state.bool_card_exchanged

    # Mock the distribute_cards method to check if it's called without modifying other game logic
    game.distribute_cards = MagicMock()

    # Ending the round
    game.end_round()

    # Check round number incremented
    assert game.state.cnt_round == initial_round + 1, "Round count should increment by 1."

    # Check next player starts new round
    expected_next_starter = (initial_starter + 1) % len(game.state.list_player)
    assert game.state.idx_player_started == expected_next_starter, "Next round should start with the correct player."

    # Check active player is set correctly
    expected_next_active = (expected_next_starter + 1) % len(game.state.list_player)
    assert game.state.idx_player_active == expected_next_active, "Active player should be set correctly for the new round."

    # Check card exchange flag reset
    assert not game.state.bool_card_exchanged, "Card exchange flag should be reset to False at the end of the round."

    # Verify distribute_cards is called
    game.distribute_cards.assert_called_once()


def test_apply_jake_action():
    game = setup_game_with_cards()

    # Assume we're using the setup as defined earlier and players' marbles are in the initial positions
    # Pick a player and an action to simulate
    player = game.state.list_player[0]  # Blue player
    action_to_apply = Action(pos_from=0, pos_to=game.state.list_player[1].list_marble[0].pos)  # Swap with the first marble of Yellow player

    # Initial positions before swap
    initial_pos_from = player.list_marble[action_to_apply.pos_from].pos
    initial_pos_to = game.state.list_player[1].list_marble[0].pos

    # Apply action
    game.apply_jake_action(player, action_to_apply)

    # After swap check
    assert player.list_marble[action_to_apply.pos_from].pos == initial_pos_to, \
        "Marble position should be swapped to the position of the target marble"
    assert game.state.list_player[1].list_marble[0].pos == initial_pos_from, \
        "Target marble should be swapped to the original position of the actor's marble"


def test_move_marble_on_board():
    game = setup_game_with_cards()
    
    # Select a player and a marble to move
    player = game.state.list_player[0]  # Blue player
    marble_to_move = player.list_marble[0]  # First marble of the Blue player
    initial_position = marble_to_move.pos
    target_position = initial_position + 5  # Move the marble forward by 5 positions

    # Reset SEVEN_STEPS_COUNTER before the action
    Dog.SEVEN_STEPS_COUNTER = 0

    # Create an action and apply it
    action = Action(pos_from=initial_position, pos_to=target_position)
    game.move_marble_on_board(marble_to_move, action)

    # Check the marble's new position
    assert marble_to_move.pos == target_position, "Marble should be moved to the new position."
    assert not marble_to_move.is_save, "Marble should not be in a safe state after moving."

    # Check if SEVEN_STEPS_COUNTER is updated correctly
    expected_counter_update = target_position - initial_position
    assert Dog.SEVEN_STEPS_COUNTER == expected_counter_update, \
        f"SEVEN_STEPS_COUNTER should be updated by the distance moved, expected {expected_counter_update}."

def test_reshuffle_if_empty():
    game = setup_game_with_cards()
    game.state.list_card_draw = []  # Simulate empty draw pile
    game.state.list_card_discard = [Card(suit='♣', rank='K')]  # Some cards in discard to be cleared

    # Assume GameState.LIST_CARD is known and has fixed content
    GameState.LIST_CARD = [Card(suit='♠', rank='A'), Card(suit='♠', rank='2')]

    with patch('random.sample', return_value=GameState.LIST_CARD.copy()), \
         patch('random.shuffle', return_value=None):
        game.reshuffle_if_empty()

        # Assert draw pile is correctly repopulated and discard pile is cleared
        assert game.state.list_card_draw == GameState.LIST_CARD, "Draw pile should be refilled from LIST_CARD"
        assert not game.state.list_card_discard, "Discard pile should be empty after reshuffle"

# def test_can_fold_cards():
#     game = setup_game_with_cards()

#     # Test scenario where folding should not be allowed (Round 6 with 6 cards)
#     round_number = 6
#     player = game.state.list_player[0]  # Blue player
#     # Set the player's card count to 6 for this specific test case
#     player.list_card = [Card(suit='♠', rank=str(num)) for num in range(1, 7)]

#     # Test that folding is not allowed
#     can_fold = game._can_fold_cards(round_number, player)
#     assert not can_fold, "Should not be able to fold cards in round 6 with 6 cards."

#     # Test scenario where folding should be allowed (Round 6 but not 6 cards)
#     player.list_card = [Card(suit='♠', rank=str(num)) for num in range(1, 5)]  # 4 cards
#     can_fold = game._can_fold_cards(round_number, player)
#     assert can_fold, "Should be able to fold cards in round 6 with less than 6 cards."

#     # Test another round where the condition doesn't apply
#     round_number = 5  # Not round 6
#     player.list_card = [Card(suit='♠', rank=str(num)) for num in range(1, 7)]  # 6 cards in a non-critical round
#     can_fold = game._can_fold_cards(round_number, player)
#     assert can_fold, "Should be able to fold cards in rounds other than round 6 regardless of card count."

# def test_find_marble_to_move():
    # game = setup_game_with_cards()

    # # Test for each player that the function returns the correct marble for a valid position
    # for player in game.state.list_player:
    #     # Test with existing positions
    #     for marble in player.list_marble:
    #         found_marble = game._find_marble_to_move(player, marble.pos)
    #         assert found_marble is not None, "Marble should be found at the given position."
    #         assert found_marble.pos == marble.pos, f"Found marble at position {marble.pos} should have the correct position."

    #     # Test with a non-existing position
    #     non_existing_position = max(m.pos for m in player.list_marble) + 1
    #     found_marble = game._find_marble_to_move(player, non_existing_position)
    #     assert found_marble is None, "Should return None for a non-existing position."

# def test_remove_duplicate_actions():
#     game = Dog()

#     # Create a list of Action objects with potential duplicates
#     action1 = Action(card=None, pos_from=1, pos_to=2)
#     action2 = Action(card=None, pos_from=1, pos_to=2)  # Duplicate of action1
#     action3 = Action(card=None, pos_from=3, pos_to=4)

#     # List containing duplicates
#     actions = [action1, action2, action3, action1]  # Intentionally adding action1 again

#     # Call the method to remove duplicates
#     unique_actions = game._remove_duplicate_actions(actions)

#     # Check if the unique_actions list contains exactly 2 unique elements
#     assert len(unique_actions) == 2, "There should be only two unique actions."
#     assert unique_actions[0] == action1, "The first unique action should match action1."
#     assert unique_actions[1] == action3, "The second unique action should match action3."
#     # You could also check if the list contains exactly the expected actions using a set
#     assert set(unique_actions) == {action1, action3}, "The set of unique actions should match the expected set."


if __name__ == "__main__":
    pytest.main()

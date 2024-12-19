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
        PlayerState(name="Yellow", list_card=[Card(suit='♥', rank='2')], list_marble=yellow_marbles, teamMate="Red"),
        PlayerState(name="Green", list_card=[Card(suit='♦', rank='3')], list_marble=green_marbles, teamMate="Blue"),
        PlayerState(name="Red", list_card=[Card(suit='♣', rank='4')], list_marble=red_marbles, teamMate="Yellow")
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

# def test_reshuffle_if_empty():
#     game = setup_game_with_cards()
#     game.state.list_card_draw = []  # Simulate empty draw pile
#     game.state.list_card_discard = [Card(suit='♣', rank='K')]  # Some cards in discard to be cleared

#     # Assume GameState.LIST_CARD is known and has fixed content
#     GameState.LIST_CARD = [Card(suit='♠', rank='A'), Card(suit='♠', rank='2')]

#     with patch('random.sample', return_value=GameState.LIST_CARD.copy()), \
#          patch('random.shuffle', return_value=None):
#         game.reshuffle_if_empty()

#         # Assert draw pile is correctly repopulated and discard pile is cleared
#         assert game.state.list_card_draw == GameState.LIST_CARD, "Draw pile should be refilled from LIST_CARD"
#         assert not game.state.list_card_discard, "Discard pile should be empty after reshuffle"

def test_can_fold_cards():
    game = setup_game_with_cards()

    # Test scenario where folding should not be allowed (Round 6 with 6 cards)
    round_number = 6
    player = game.state.list_player[0]  # Blue player
    # Set the player's card count to 6 for this specific test case
    player.list_card = [Card(suit='♠', rank=str(num)) for num in range(1, 7)]

    # Test that folding is not allowed
    can_fold = game._can_fold_cards(round_number, player)
    assert not can_fold, "Should not be able to fold cards in round 6 with 6 cards."

    # Test scenario where folding should be allowed (Round 6 but not 6 cards)
    player.list_card = [Card(suit='♠', rank=str(num)) for num in range(1, 5)]  # 4 cards
    can_fold = game._can_fold_cards(round_number, player)
    assert can_fold, "Should be able to fold cards in round 6 with less than 6 cards."

    # Test another round where the condition doesn't apply
    round_number = 5  # Not round 6
    player.list_card = [Card(suit='♠', rank=str(num)) for num in range(1, 7)]  # 6 cards in a non-critical round
    can_fold = game._can_fold_cards(round_number, player)
    assert can_fold, "Should be able to fold cards in rounds other than round 6 regardless of card count."

def test_find_marble_to_move():
    game = setup_game_with_cards()

    # Test for each player that the function returns the correct marble for a valid position
    for player in game.state.list_player:
        # Test with existing positions
        for marble in player.list_marble:
            found_marble = game._find_marble_to_move(player, marble.pos)
            assert found_marble is not None, "Marble should be found at the given position."
            assert found_marble.pos == marble.pos, f"Found marble at position {marble.pos} should have the correct position."

        # Test with a non-existing position
        non_existing_position = max(m.pos for m in player.list_marble) + 1
        found_marble = game._find_marble_to_move(player, non_existing_position)
        assert found_marble is None, "Should return None for a non-existing position."

def test_remove_duplicate_actions():
    game = Dog()

    action1 = Action(card=None, pos_from=1, pos_to=2)
    action2 = Action(card=None, pos_from=1, pos_to=2)  # Duplicate of action1
    action3 = Action(card=None, pos_from=3, pos_to=4)

    actions = [action1, action2, action3, action1]

    unique_actions = game._remove_duplicate_actions(actions)

    # Ensure that unique_actions has exactly 2 unique elements
    assert len(unique_actions) == 2, "There should be only two unique actions."
    assert unique_actions.count(action1) == 1, "Action1 should appear exactly once."
    assert unique_actions.count(action3) == 1, "Action3 should appear exactly once."
    assert action1 in unique_actions, "The first unique action should match action1."
    assert action3 in unique_actions, "The second unique action should match action3."

# def test_all_marbles_in_finish():
#     # Mock the ENDZONE for testing
#     Dog.ENDZONE = {
#         "Blue": [60, 95],
#     }

#     # Create a Dog instance
#     dog = Dog()

#     # Create a mock player with all marbles in the finish zone
#     player = PlayerState(
#         name="Blue",
#         list_card=[],
#         list_marble=[Marble(pos=61, is_save=True), Marble(pos=62, is_save=True)],
#         teamMate="Green"
#     )

#     # Check if the method returns True
#     assert dog._all_marbles_in_finish(player) == True

#     # Create a mock player with a marble not in the finish zone
#     player.list_marble = [Marble(pos=59, is_save=True), Marble(pos=62, is_save=True)]

#     # Check if the method returns False
#     assert dog._all_marbles_in_finish(player) == False

import pytest

@pytest.fixture
def game_state():
    return GameState(
        cnt_player=4,
        phase="running",
        cnt_round=1,
        bool_card_exchanged=False,
        idx_player_started=0,
        idx_player_active=0,
        list_player=[],
        list_card_draw=[],
        list_card_discard=[],
        card_active=None
    )

@pytest.fixture
def mock_endzone():
    Dog.ENDZONE = {
        "Blue": [60, 95],
        "Green": [40, 59],
        "Red": [20, 39],
        "Yellow": [0, 19],
    }

@pytest.fixture
def mock_kennel_and_start_positions():
    Dog.KENNEL = {
        "Blue": [0, 1, 2],
        "Green": [3, 4, 5],
        "Red": [6, 7, 8],
        "Yellow": [9, 10, 11],
    }
    Dog.START_POSITIONS = {
        "Blue": 10,
        "Green": 15,
        "Red": 20,
        "Yellow": 25,
    }

def test_get_partner_actions(game_state, mock_endzone):
    player = PlayerState(
        name="Blue",
        list_card=[Card(suit="♥", rank="Q"), Card(suit="♠", rank="7")],
        list_marble=[Marble(pos=10, is_save=True)],
        teamMate="Green"
    )
    partner = PlayerState(
        name="Green",
        list_card=[],
        list_marble=[Marble(pos=20, is_save=False), Marble(pos=30, is_save=False)],
        teamMate="Blue"
    )
    game_state.list_player = [player, None, partner, None]
    dog = Dog()
    actions = dog._get_partner_actions(player, game_state)
    assert len(actions) > 0
    assert all(isinstance(action, Action) for action in actions)
    assert all(action.pos_from in [20, 30] for action in actions)
    assert all(action.card in player.list_card for action in actions)

def test_get_player_actions(game_state):
    player = PlayerState(
        name="Blue",
        list_card=[
            Card(suit="♥", rank="7"),
            Card(suit="♠", rank="J"),
            Card(suit="♦", rank="3"),
        ],
        list_marble=[
            Marble(pos=10, is_save=True),
            Marble(pos=20, is_save=False),
        ],
        teamMate="Green"
    )
    class MockDog(Dog):
        def get_seven_actions(self, player, card):
            return [Action(card=card, pos_from=10, pos_to=17)]
        def get_jake_actions(self, player, card):
            return [Action(card=card, pos_from=20, pos_to=30)]
        def get_kennel_exit_actions(self, player):
            return [Action(card=player.list_card[2], pos_from=-1, pos_to=10)]
        def get_board_move_actions(self, player):
            return [Action(card=player.list_card[2], pos_from=20, pos_to=23)]
        def _remove_duplicate_actions(self, actions):
            unique_actions = []
            for action in actions:
                if action not in unique_actions:
                    unique_actions.append(action)
            return unique_actions
    dog = MockDog()
    dog.state = game_state
    actions = dog._get_player_actions(player)
    assert len(actions) > 0
    assert all(isinstance(action, Action) for action in actions)
    assert any(action.card.rank == '7' for action in actions)
    assert any(action.card.rank == 'J' for action in actions)
    assert any(action.card.rank == '3' for action in actions)

def test_get_kennel_exit_actions(mock_kennel_and_start_positions):
    player = PlayerState(
        name="Blue",
        list_card=[
            Card(suit="♥", rank="K"),
            Card(suit="♠", rank="A"),
            Card(suit="♦", rank="JKR"),
            Card(suit="♣", rank="3"),
        ],
        list_marble=[
            Marble(pos=0, is_save=False),
            Marble(pos=20, is_save=True),
        ],
        teamMate="Green"
    )
    class MockDog(Dog):
        def add_substitute_actions(self, actions, card):
            actions.append(Action(card=card, pos_from=0, pos_to=11))
    dog = MockDog()
    actions = dog.get_kennel_exit_actions(player)
    assert len(actions) > 0
    assert all(isinstance(action, Action) for action in actions)
    for action in actions:
        if action.card.rank in ["K", "A"]:
            assert action.pos_to == 10, f"Unexpected pos_to for card {action.card.rank}: {action.pos_to}"
        elif action.card.rank == "JKR":
            assert action.pos_to in [10, 11], f"Unexpected pos_to for Joker card: {action.pos_to}"
    assert not any(action.card.rank == "3" for action in actions)

def test_add_substitute_actions():
    joker_card = Card(suit="", rank="JKR")
    actions = []
    class MockDog(Dog):
        pass
    dog = MockDog()
    dog.add_substitute_actions(actions, joker_card)
    assert len(actions) == 8
    assert all(isinstance(action, Action) for action in actions)
    assert all(action.card == joker_card for action in actions)
    assert all(action.pos_from is None for action in actions)
    assert all(action.pos_to is None for action in actions)
    substitute_ranks = {"K", "A"}
    substitute_suits = {"♠", "♥", "♦", "♣"}
    for action in actions:
        assert action.card_swap.rank in substitute_ranks
        assert action.card_swap.suit in substitute_suits

def test_apply_seven_kickout(game_state, mock_kennel_and_start_positions):
    class MockDog(Dog):
        pass

    dog = MockDog()
    dog.state = GameState(
        cnt_player=4,
        phase="running",
        cnt_round=1,
        bool_card_exchanged=False,
        idx_player_started=0,
        idx_player_active=0,
        list_player=[
            PlayerState(
                name="Blue",
                list_marble=[
                    Marble(pos=4, is_save=False),
                    Marble(pos=6, is_save=False),
                ],
                list_card=[],
                teamMate="Green"
            ),
            PlayerState(
                name="Green",
                list_marble=[
                    Marble(pos=8, is_save=True),
                ],
                list_card=[],
                teamMate="Blue"
            )
        ],
        list_card_draw=[],
        list_card_discard=[],
        card_active=None
    )
    action = Action(card=None, pos_from=3, pos_to=5)
    dog._apply_seven_kickout(action)

    assert dog.state.list_player[0].list_marble[0].pos == 0
    assert dog.state.list_player[0].list_marble[0].is_save is False
    assert dog.state.list_player[0].list_marble[1].pos == 6
    assert dog.state.list_player[1].list_marble[0].pos == 8

def test_get_jake_actions(game_state):
    class MockDog(Dog):
        pass

    dog = MockDog()
    dog.state = GameState(
        cnt_player=4,
        phase="running",
        cnt_round=1,
        bool_card_exchanged=False,
        idx_player_started=0,
        idx_player_active=0,
        list_player=[
            PlayerState(
                name="Blue",
                list_marble=[
                    Marble(pos=10, is_save=False),
                    Marble(pos=20, is_save=False),
                ],
                list_card=[],
                teamMate="Green"
            ),
            PlayerState(
                name="Green",
                list_marble=[
                    Marble(pos=30, is_save=False),
                ],
                list_card=[],
                teamMate="Blue"
            )
        ],
        list_card_draw=[],
        list_card_discard=[],
        card_active=None
    )
    card = Card(suit="♠", rank="J")
    actions = dog.get_jake_actions(dog.state.list_player[0], card)

    assert len(actions) > 0
    assert all(isinstance(action, Action) for action in actions)
    assert any(action.pos_from == 10 and action.pos_to == 30 for action in actions)
    assert any(action.pos_from == 30 and action.pos_to == 10 for action in actions)

def test_get_seven_actions(game_state):
    class MockDog(Dog):
        pass

    dog = MockDog()
    GameState.get_card_steps = lambda rank: (1, 2, 3, 4, 5, 6, 7)
    GameState.is_valid_move = lambda pos_to, marbles: pos_to not in [marble.pos for marble in marbles]

    dog.state = GameState(
        cnt_player=4,
        phase="running",
        cnt_round=1,
        bool_card_exchanged=False,
        idx_player_started=0,
        idx_player_active=0,
        list_player=[
            PlayerState(
                name="Blue",
                list_marble=[
                    Marble(pos=10, is_save=False),
                    Marble(pos=20, is_save=False),
                ],
                list_card=[],
                teamMate="Green"
            )
        ],
        list_card_draw=[],
        list_card_discard=[],
        card_active=None
    )
    card = Card(suit="♥", rank="7")
    actions = dog.get_seven_actions(dog.state.list_player[0], card)

    assert len(actions) > 0
    assert all(isinstance(action, Action) for action in actions)
    assert any(action.pos_from == 10 and action.pos_to == 17 for action in actions)
    assert any(action.pos_from == 20 and action.pos_to == 27 for action in actions)

def test_handle_fold_cards(game_state):
    class MockDog(Dog):
        def _can_fold_cards(self, cnt_round, active_player):
            return True

    dog = MockDog()
    dog.state = GameState(
        cnt_player=4,
        phase="running",
        cnt_round=1,
        bool_card_exchanged=False,
        idx_player_started=0,
        idx_player_active=0,
        list_player=[],
        list_card_draw=[],
        list_card_discard=[],
        card_active=None
    )
    active_player = PlayerState(
        name="Blue",
        list_card=[
            Card(suit="♥", rank="7"),
            Card(suit="♠", rank="K"),
        ],
        list_marble=[],
        teamMate="Green"
    )
    dog.state.list_player = [active_player]

    dog._handle_fold_cards(active_player)

    assert len(active_player.list_card) == 0
    assert len(dog.state.list_card_discard) == 2
    assert dog.state.list_card_discard[0].rank == "7"
    assert dog.state.list_card_discard[1].rank == "K"

def test_handle_action_with_card(game_state, mock_kennel_and_start_positions):
    class MockDog(Dog):
        def apply_jake_action(self, player, action):
            for marble in player.list_marble:
                if marble.pos == action.pos_from:
                    marble.pos = action.pos_to

        def move_marble_to_start(self, player, marble, action):
            marble.pos = action.pos_to

        def move_marble_to_finish(self, marble, action):
            marble.pos = action.pos_to

        def move_marble_on_board(self, marble, action):
            marble.pos = action.pos_to

    dog = MockDog()
    dog.state = game_state

    player = PlayerState(
        name="Blue",
        list_card=[Card(suit="♥", rank="J")],
        list_marble=[Marble(pos=10, is_save=False)],
        teamMate="Green"
    )
    action_jake = Action(card=player.list_card[0], pos_from=10, pos_to=20)
    action_start = Action(card=None, pos_from=10, pos_to=Dog.START_POSITIONS["Blue"])
    action_finish = Action(card=None, pos_from=10, pos_to=Dog.ENDZONE["Blue"][0])
    action_board = Action(card=None, pos_from=10, pos_to=15)

    dog._handle_action_with_card(player, player.list_marble[0], action_jake)
    assert player.list_marble[0].pos == 20, f"Jake action failed: {player.list_marble[0].pos}"

def test_discard_card_and_advance(game_state):
    class MockDog(Dog):
        def _handle_seven_card(self, action):
            self.state.list_card_discard.append(action.card)

        def _advance_turn(self):
            self.state.idx_player_active = (self.state.idx_player_active + 1) % self.state.cnt_player

    dog = MockDog()
    dog.state = GameState(
        cnt_player=4,
        phase="running",
        cnt_round=1,
        bool_card_exchanged=False,
        idx_player_started=0,
        idx_player_active=0,
        list_player=[],
        list_card_draw=[],
        list_card_discard=[],
        card_active=None
    )

    active_player = PlayerState(
        name="Blue",
        list_card=[Card(suit="♥", rank="7"), Card(suit="♠", rank="K")],
        list_marble=[],
        teamMate="Green"
    )
    action_seven = Action(card=active_player.list_card[0], pos_from=None, pos_to=None)
    action_regular = Action(card=active_player.list_card[1], pos_from=None, pos_to=None)

    dog._discard_card_and_advance(action_seven, active_player)
    assert len(dog.state.list_card_discard) == 1
    assert dog.state.list_card_discard[0].rank == "7"

    dog._discard_card_and_advance(action_regular, active_player)
    assert len(dog.state.list_card_discard) == 2
    assert dog.state.list_card_discard[1].rank == "K"
    assert dog.state.idx_player_active == 1

def test_handle_seven_card(game_state):
    class MockDog(Dog):
        pass

    dog = MockDog()
    Dog.SEVEN_STEPS_COUNTER = 0
    dog.state = GameState(
        cnt_player=4,
        phase="running",
        cnt_round=1,
        bool_card_exchanged=False,
        idx_player_started=0,
        idx_player_active=0,
        list_player=[],
        list_card_draw=[],
        list_card_discard=[],
        card_active=None
    )

    seven_card = Card(suit="♥", rank="7")
    action = Action(card=seven_card, pos_from=None, pos_to=None)

    # Test setting card_active when no card is active
    dog._handle_seven_card(action)
    assert dog.state.card_active == seven_card
    assert Dog.SEVEN_STEPS_COUNTER == 0

    # Test resetting card_active and advancing turn when SEVEN_STEPS_COUNTER reaches 7
    Dog.SEVEN_STEPS_COUNTER = 7
    dog._handle_seven_card(action)
    assert dog.state.card_active is None
    assert Dog.SEVEN_STEPS_COUNTER == 0
    assert dog.state.idx_player_active == 1

def test_is_valid_move():
    marbles = [
        Marble(pos=10, is_save=True),
        Marble(pos=20, is_save=False),
        Marble(pos=30, is_save=False),
    ]

    # Test valid move (no marble at pos_to)
    assert GameState.is_valid_move(15, marbles) is True

    # Test invalid move (marble occupies pos_to)
    assert GameState.is_valid_move(10, marbles) is False
    assert GameState.is_valid_move(20, marbles) is False

    # Test valid move (boundary check)
    assert GameState.is_valid_move(40, marbles) is True

if __name__ == "__main__":
    pytest.main()

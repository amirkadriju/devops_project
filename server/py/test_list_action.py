import pytest
import unittest
import sys

from server.py.dog import Dog, GamePhase, GameState, Card, Action

# Mock classes
class MockPlayer:
    def __init__(self, cards):
        self.list_card = cards

class MockState:
    def __init__(self, player):
        self.player = player

    def get_list_action(self):
        # Assuming this method needs to calculate actions based on player's cards
        valid_ranks = ['K', 'A', 'JKR']
        actions = []
        for card in self.player.list_card:
            if card.rank in valid_ranks:
                actions.append(Action(card=card, pos_from=64, pos_to=0))  # Adjust according to your game's logic
        return actions

class MockGameServer:
    def __init__(self, state):
        self.state = state

    def get_state(self):
        return self.state

    def set_state(self, state):
        self.state = state

    def get_list_action(self):
        return self.state.get_list_action()

# Test Case 1: When the player has no valid cards (King, Ace, or Joker)
def test_get_list_action_without_start_cards():
    player = MockPlayer([
        Card(suit='♣', rank='3'),
        Card(suit='♦', rank='9'),
        Card(suit='♣', rank='10'),
        Card(suit='♥', rank='Q'),
        Card(suit='♠', rank='7'),
        Card(suit='♣', rank='J')
    ])
    state = MockState(player)
    game_server = MockGameServer(state)

    list_action_found = game_server.get_list_action()
    list_action_expected = []

    assert list_action_found == list_action_expected, f"Expected {list_action_expected}, but got {list_action_found}"

# Test Case 2: When the player has a valid starting card (King, Ace, or Joker)
@pytest.mark.parametrize("valid_card", [
    Card(suit='♦', rank='A'),
    Card(suit='♥', rank='K'),
    Card(suit='', rank='JKR')
])
def test_get_list_action_with_one_start_card(valid_card):
    player = MockPlayer([
        Card(suit='♣', rank='10'),
        Card(suit='♥', rank='Q'),
        Card(suit='♠', rank='7'),
        Card(suit='♣', rank='J'),
        valid_card
    ])
    state = MockState(player)
    game_server = MockGameServer(state)

    list_action_found = game_server.get_list_action()
    action = Action(card=valid_card, pos_from=64, pos_to=0)  # Adjust as needed for your game's logic
    
    assert action in list_action_found, f"Expected action {action}, but got {list_action_found}"

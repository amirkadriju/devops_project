# runcmd: cd ../.. & venv\Scripts\python server/py/dog_template.py
#import sys
#import os
#sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))


from server.py.game import Game, Player
from typing import List, Optional, ClassVar
from pydantic import BaseModel
from enum import Enum
import random
from pprint import pprint


class Card(BaseModel):
    suit: str  # card suit (color)
    rank: str  # card rank

    def __lt__(self, card) -> bool:
        return self.suit < card.suit or \
            self.rank < card.rank


class Marble(BaseModel):
    pos: str       # position on board (0 to 95)
    is_save: bool  # true if marble was moved out of kennel and was not yet moved


class PlayerState(BaseModel):
    name: str                  # name of player
    list_card: List[Card]      # list of cards
    list_marble: List[Marble]  # list of marbles
    teamMate: str


class Action(BaseModel):
    card: Optional[Card] = None           # Make optional
    pos_from: Optional[int] = None        # Make optional
    pos_to: Optional[int] = None          # Make optional
    card_swap: Optional[Card] = None      # Make optional)


class GamePhase(str, Enum):
    SETUP = 'setup'            # before the game has started
    RUNNING = 'running'        # while the game is running
    FINISHED = 'finished'      # when the game is finished


class GameState(BaseModel):

    LIST_SUIT: ClassVar[List[str]] = ['♠', '♥', '♦', '♣']  # 4 suits (colors)
    LIST_RANK: ClassVar[List[str]] = [
        '2', '3', '4', '5', '6', '7', '8', '9', '10',      # 13 ranks + Joker
        'J', 'Q', 'K', 'A', 'JKR'
    ]
    LIST_CARD: ClassVar[List[Card]] = [
        # 2: Move 2 spots forward
        Card(suit='♠', rank='2'), Card(suit='♥', rank='2'), Card(suit='♦', rank='2'), Card(suit='♣', rank='2'),
        # 3: Move 3 spots forward
        Card(suit='♠', rank='3'), Card(suit='♥', rank='3'), Card(suit='♦', rank='3'), Card(suit='♣', rank='3'),
        # 4: Move 4 spots forward or back
        Card(suit='♠', rank='4'), Card(suit='♥', rank='4'), Card(suit='♦', rank='4'), Card(suit='♣', rank='4'),
        # 5: Move 5 spots forward
        Card(suit='♠', rank='5'), Card(suit='♥', rank='5'), Card(suit='♦', rank='5'), Card(suit='♣', rank='5'),
        # 6: Move 6 spots forward
        Card(suit='♠', rank='6'), Card(suit='♥', rank='6'), Card(suit='♦', rank='6'), Card(suit='♣', rank='6'),
        # 7: Move 7 single steps forward
        Card(suit='♠', rank='7'), Card(suit='♥', rank='7'), Card(suit='♦', rank='7'), Card(suit='♣', rank='7'),
        # 8: Move 8 spots forward
        Card(suit='♠', rank='8'), Card(suit='♥', rank='8'), Card(suit='♦', rank='8'), Card(suit='♣', rank='8'),
        # 9: Move 9 spots forward
        Card(suit='♠', rank='9'), Card(suit='♥', rank='9'), Card(suit='♦', rank='9'), Card(suit='♣', rank='9'),
        # 10: Move 10 spots forward
        Card(suit='♠', rank='10'), Card(suit='♥', rank='10'), Card(suit='♦', rank='10'), Card(suit='♣', rank='10'),
        # Jake: A marble must be exchanged
        Card(suit='♠', rank='J'), Card(suit='♥', rank='J'), Card(suit='♦', rank='J'), Card(suit='♣', rank='J'),
        # Queen: Move 12 spots forward
        Card(suit='♠', rank='Q'), Card(suit='♥', rank='Q'), Card(suit='♦', rank='Q'), Card(suit='♣', rank='Q'),
        # King: Start or move 13 spots forward
        Card(suit='♠', rank='K'), Card(suit='♥', rank='K'), Card(suit='♦', rank='K'), Card(suit='♣', rank='K'),
        # Ass: Start or move 1 or 11 spots forward
        Card(suit='♠', rank='A'), Card(suit='♥', rank='A'), Card(suit='♦', rank='A'), Card(suit='♣', rank='A'),
        # Joker: Use as any other card you want
        Card(suit='', rank='JKR'), Card(suit='', rank='JKR'), Card(suit='', rank='JKR')
    ] * 2

    cnt_player: int = 4                # number of players (must be 4)
    phase: GamePhase                   # current phase of the game
    cnt_round: int                     # current round
    bool_card_exchanged: bool          # true if cards was exchanged in round
    idx_player_started: int            # index of player that started the round
    idx_player_active: int             # index of active player in round
    list_player: List[PlayerState]     # list of players
    list_card_draw: List[Card]         # list of cards to draw
    list_card_discard: List[Card]      # list of cards discarded
    card_active: Optional[Card]        # active card (for 7 and JKR with sequence of actions)

    def get_card_steps(self, rank: str) -> int:
        """ Return the number of steps based on the card rank """
        if rank in ['2', '3', '4', '5', '6', '8', '9', '10']:
            return [int(rank)]
        elif rank in ['7']:
            return [1, 2, 3, 4, 5, 6, 7]
        elif rank in ['Q']:
            return [12]
        elif rank in ['K']:
            return [13]
        elif rank in ['A']:
            return [1, 11]
        elif rank in ['J', 'JKR']:
            return [0]
        else:
            return [0]
    
    def is_valid_move(self, pos_from: int, pos_to: int) -> bool:
        """ Validate if a move from pos_from to pos_to is allowed """
        # Check if own marble occupies the destination spot
        active_player = self.list_player[self.idx_player_active]
        for marble in active_player.list_marble:
            if marble.pos == str(pos_to):
                return False

        return True


class Dog(Game):

    START_POSITIONS: ClassVar[dict] = {
        "Blue": 0,
        "Green": 16,
        "Red": 32,
        "Yellow": 48
    }

    KENNEL: ClassVar[dict] = {
        "Blue": [64, 65, 66, 67],
        "Green": [72, 73, 74, 75],
        "Red": [80, 81, 82, 83],
        "Yellow": [88, 89, 90, 91]
    }

    ENDZONE: ClassVar[dict] = {
        "Blue": [68, 69, 70, 71],
        "Green": [76, 77, 78, 79],
        "Red": [84, 85, 86, 87],
        "Yellow": [92, 93, 94, 85]
    }

    def __init__(self) -> None:
        """ Game initialization (set_state call not necessary, we expect 4 players) """
        # Shuffle the cards
        shuffled_cards = random.sample(GameState.LIST_CARD, len(GameState.LIST_CARD))

        # Setup the board with 95 places and initial marble positions
        blue_marbles = [Marble(pos=str(i), is_save=True) for i in Dog.KENNEL["Blue"]]
        green_marbles = [Marble(pos=str(i), is_save=True) for i in Dog.KENNEL["Green"]]
        red_marbles = [Marble(pos=str(i), is_save=True) for i in Dog.KENNEL["Red"]]
        yellow_marbles = [Marble(pos=str(i), is_save=True) for i in Dog.KENNEL["Yellow"]]

        # Initialize players
        self.state = GameState(
            cnt_player=4,
            phase=GamePhase.SETUP,
            cnt_round=0,
            bool_card_exchanged=False,
            idx_player_started=random.randint(0, 3),  # Randomly select start player
            idx_player_active=0,
            list_player=[
                PlayerState(name="Blue", list_card=[], list_marble=blue_marbles, teamMate = "Green"),
                PlayerState(name="Green", list_card=[], list_marble=green_marbles, teamMate = "Blue"),
                PlayerState(name="Red", list_card=[], list_marble=red_marbles, teamMate = "Yellow"),
                PlayerState(name="Yellow", list_card=[], list_marble=yellow_marbles, teamMate= "Red"),
            ],
            list_card_draw=shuffled_cards,
            list_card_discard=[],
            card_active=None
        )
    
         # Deal 6 cards to each player directly in the init
        num_cards_per_player = 6  # Example number of cards per player
        for player in self.state.list_player:
            player.list_card = [self.state.list_card_draw.pop() for _ in range(num_cards_per_player)]

        # Transition to the running phase, since we're starting the game directly
        self.state.phase = GamePhase.RUNNING
        self.state.cnt_round = 1
        self.state.idx_player_active = self.state.idx_player_started
        #self.state.bool_card_exchanged = True

        # Exchange card with teammate
        if self.state.bool_card_exchanged:
            for player in self.state.list_player:
                for teammate in self.state.list_player:
                    if teammate.name == player.teamMate and player.name < teammate.name: 
                        card_to_exchange = random.choice(player.list_card)
                        player.list_card.remove(card_to_exchange)
                        card_from_teammate = random.choice(teammate.list_card)
                        teammate.list_card.remove(card_from_teammate)
                        teammate.list_card.append(card_to_exchange)
                        player.list_card.append(card_from_teammate)
            self.state.bool_card_exchanged = False
    
    def reshuffle_if_empty(self):
        """ Reshuffle the discard pile into the draw pile when empty """
        if not self.state.list_card_draw:  # Check if the draw pile is empty
            if self.state.list_card_discard:  # Check if there are discarded cards
                # Move discarded cards to the draw pile
                self.state.list_card_draw.extend(self.state.list_card_discard)
                self.state.list_card_discard.clear()  # Clear the discard pile
                random.shuffle(self.state.list_card_draw)  # Shuffle the draw pile
            else:
                # No cards in either pile; raise an error
                raise ValueError("Both draw and discard piles are empty! Game cannot continue.")

    def set_state(self, state: GameState) -> None:
        """ Set the game to a given state """
        self.state = state

    def get_state(self) -> GameState:
        """ Get the complete, unmasked game state """
        return self.state

    def print_state(self) -> None:
        """ Print the current game state """
        
        print("\n=== Brandi Dog Game State ===")
        print(f"Phase: {self.state.phase}")
        print(f"Round: {self.state.cnt_round}")
        print(f"Player to Start: {self.state.list_player[self.state.idx_player_started].name}")
        print(f"Active Player: {self.state.list_player[self.state.idx_player_active].name}")
        print(f"Cards Left in Draw Pile: {len(self.state.list_card_draw)}")
        print(f"Cards in Discard Pile: {len(self.state.list_card_discard)}")
        print("\n--- Players ---")
        for player in self.state.list_player:
            print(f"Player: {player.name}")
            print(f"  Marbles: {', '.join([f'Pos {m.pos} (Saved: {m.is_save})' for m in player.list_marble])}")
            print(f"  Cards in Hand: {len(player.list_card)}")
        print("\n--- Active Card ---")
        if self.state.card_active:
            print(f"Active Card: {self.state.card_active.suit}{self.state.card_active.rank}")
        else:
            print("No Active Card")
        print("\n============================\n")
    
    def get_list_action(self) -> List[Action]:
        """ 
        Get a list of possible actions for the active player.
        Returns: actions -> list
        """
        list_action = []
        state = self.get_state()
        player = state.list_player[state.idx_player_active]

        player_kennel = Dog.KENNEL[player.name]
        player_start_position = Dog.START_POSITIONS[player.name]

        # Check if the starting position is occupied by one of the player's own marbles
        starting_position_occupied = any(
            int(marble.pos) == int(player_start_position) for marble in player.list_marble
        )

        # If starting position is free, check if the player has K, A, or JKR
        if not starting_position_occupied:
            for card in player.list_card:
                # Handle Ace and King
                if card.rank in ['K', 'A']:
                    # Check if the player has any marbles in the kennel
                    marbles_in_kennel = [
                        marble for marble in player.list_marble if marble.pos in map(str, player_kennel)
                    ]
                    if marbles_in_kennel:
                        # Create an action to move the first marble out of the kennel
                        action = Action(
                            card=card,
                            pos_from=int(marbles_in_kennel[0].pos),
                            pos_to=player_start_position
                        )
                        list_action.append(action)

                # Handle Joker (JKR) separately
                elif card.rank == 'JKR':
                    # Check if the player has any marbles in the kennel
                    marbles_in_kennel = [
                        marble for marble in player.list_marble if marble.pos in map(str, player_kennel)
                    ]
                    if marbles_in_kennel:
                        # Create an action to move the first marble out of the kennel
                        action = Action(
                            card=card,
                            pos_from=int(marbles_in_kennel[0].pos),
                            pos_to=player_start_position
                        )
                        list_action.append(action)

                        # Add swap actions for Ace and King for all suits
                        for substitute_rank in ['A', 'K']:
                            for suit in GameState.LIST_SUIT:
                                substitute_card = Card(suit=suit, rank=substitute_rank)
                                list_action.append(
                                    Action(
                                        card=card,
                                        pos_from=None,  
                                        pos_to=None,    
                                        card_swap=substitute_card
                                    )
                                )

        
        # Add moving forward for each marble
        for card in player.list_card:
            for marble in player.list_marble:
                pos_from = marble.pos
                
                # check if marble is in the kennel
                if pos_from in map(str, player_kennel):
                    continue

                # get step options based on card
                steps_options  = self.state.get_card_steps(card)
                
                for steps in steps_options:
                    # Calculate the new position
                    pos_to = pos_from + steps
                    if pos_from >= 0 and pos_from <= 63:
                        pos_to %= 64  # Wrap around the board

                        # Handle entering endzone
                        if player.name == "Blue" and pos_from <= 63 and pos_to >= 68:
                            pos_to = min(68 + (pos_to - 68), 71)  # Enter Blue endzone
                        elif player.name == "Green" and pos_from <= 15 and pos_to >= 76:
                            pos_to = min(76 + (pos_to - 76), 79)  # Enter Green endzone
                        elif player.name == "Red" and pos_from <= 31 and pos_to >= 84:
                            pos_to = min(84 + (pos_to - 84), 87)  # Enter Red endzone
                        elif player.name == "Yellow" and pos_from <= 47 and pos_to >= 92:
                            pos_to = min(92 + (pos_to - 92), 95)  # Enter Yellow endzone

                    # Handle marbles already in the endzone
                    if pos_from >= 68:
                        endzone_start = Dog.ENDZONE[player.name][0]
                        endzone_end = Dog.ENDZONE[player.name][-1]
                        pos_to = min(pos_from + steps, endzone_end)
                    
                    # Check for overtaking in the finish zone
                    if pos_from >= Dog.ENDZONE[player.name][0]:
                        # Get all marbles in the finish zone
                        marbles_in_finish_zone = [
                            marble for marble in player.list_marble
                            if int(marble.pos) >= Dog.ENDZONE[player.name][0] and int(marble.pos) <= Dog.ENDZONE[player.name][-1]
                        ]
                        
                        # If the move would place the marble in a position already occupied by another, it should be blocked
                        if any(marble.pos >= pos_to for marble in marbles_in_finish_zone) and pos_to <= Dog.ENDZONE[player.name][-1]:
                            continue

                    # Validate the move
                    if self.state.is_valid_move(pos_from, pos_to):
                        list_action.append(
                            Action(card=card, pos_from=pos_from, pos_to=pos_to)
                        )

        return list_action

    def apply_action(self, action: Optional[Action]) -> None:
        """ Apply the given action to the game """

        if action is None:
            # Update turn
            self.state.idx_player_active = (self.state.idx_player_active + 1) % self.state.cnt_player
            if self.state.idx_player_active == self.state.idx_player_started:
                self.end_round()
            return

        player = self.state.list_player[self.state.idx_player_active]
        card = action.card

        if not card:
            raise ValueError("Action must include a card.")


        # check if any marbles should be moved
        marble_to_move = None
        for marble in player.list_marble:
            if int(marble.pos) == int(action.pos_from):
                marble_to_move = marble
                break

        # if there are marbles to be moved, then move them and discard the card of the player afterwards
        if not marble_to_move is None:
            marble_to_move.pos = action.pos_to
            player.list_card.remove(action.card)
            self.state.list_card_discard.append(action.card)
            self.state.idx_player_active = (self.state.idx_player_active + 1) % self.state.cnt_player
            if self.state.idx_player_active == self.state.idx_player_started:
                self.end_round()

    def exchange_cards(self):
        # Exchange the first card with teammate
        if not self.state.bool_card_exchanged:
            for idx_player in range(len(self.state.list_player)):
                idx_player_partner = (idx_player + 2) % len(self.state.list_player) 
                player = self.state.list_player[idx_player]
                teammate = self.state.list_player[idx_player_partner]
                card_to_exchange = player.list_card[0]
                player.list_card.remove(card_to_exchange)
                teammate.list_card.append(card_to_exchange)
        self.state.bool_card_exchanged = True
        
    def get_player_view(self, idx_player: int) -> GameState:
        """ Get the masked state for the active player (e.g. the oppontent's cards are face down)"""
        return self.state

    def end_round(self):
        self.state.cnt_round += 1
        self.state.idx_player_started = (self.state.idx_player_started - 1) % self.state.cnt_player
        self.state.idx_player_active = self.state.idx_player_started
        self.state.bool_card_exchanged = False

        # Prepare next round
        self.distribute_cards()

    def distribute_cards(self):
        """
        Distribute cards to players at the start of each round.
        The number of cards decreases each round: 6, 5, 4, 3, 2.
        """
        # Cards per round: 6, 5, 4, 3, 2 (repeats after every 5 rounds)
        num_cards = 6 - ((self.state.cnt_round - 1) % 5)

        for player in self.state.list_player:
            # Ensure there are enough cards to deal
            if len(self.state.list_card_draw) < num_cards:
                self.reshuffle_if_empty()
            
            # Deal the cards
            player.list_card = [self.state.list_card_draw.pop() for _ in range(num_cards)]
        

class RandomPlayer(Player):

    def select_action(self, state: GameState, actions: List[Action]) -> Optional[Action]:
        """ Given masked game state and possible actions, select the next action """
        if len(actions) > 0:
            return random.choice(actions)
        return None


if __name__ == '__main__':
    game = Dog()
    player = game.state.idx_player_active
    round = game.state.cnt_round
    n_cards = len(game.state.list_player[0].list_card)
    print(player, round, n_cards)
    action = game.apply_action(None)
    action = game.apply_action(None)
    action = game.apply_action(None)
    action = game.apply_action(None)
    action = game.apply_action(None)
    player = game.state.idx_player_active
    round = game.state.cnt_round
    n_cards = len(game.state.list_player[0].list_card)
    print(player, round, n_cards)
    
    





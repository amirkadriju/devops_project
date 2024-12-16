# runcmd: cd ../.. & venv\Scripts\python server/py/dog_template.py
#import sys
#import os
#sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))


import random

from typing import List, Optional, ClassVar, cast, Union, Tuple
from enum import Enum
from pydantic import BaseModel
#from typing import cast
from server.py.game import Game, Player


class Card(BaseModel):
    suit: str  # card suit (color)
    rank: str  # card rank


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

    @staticmethod
    def get_card_steps(rank: str) -> Union[int, Tuple[int, int]]:
        rank_steps: dict[str, Union[int, Tuple[int,int]]] = {
            '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '8': 8, '9': 9, '10': 10,
            '7': (1, 2, 3, 4, 5, 6, 7),
            'Q': 12,
            'K': 13,
            'A': (1, 11)
        }
        if rank in rank_steps:
            return rank_steps[rank]
        return 0

    @staticmethod
    def is_valid_move(pos_to: int, marbles: List[Marble]) -> bool:
        """ Validate if a move from pos_from to pos_to is allowed """
        # check if own marble occupies spot
        for marble in marbles:
            if int(marble.pos) == pos_to:
                return False

        return True


class Dog(Game):

    SEVEN_STEPS_COUNTER: ClassVar[int] = 0

    EXCHANGE_COUNTER: ClassVar[int] = 0

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
        "Yellow": [92, 93, 94, 95]
    }

    def __init__(self) -> None:
        """ Game initialization (set_state call not necessary, we expect 4 players) """
        # Shuffle the cards
        shuffled_cards = random.sample(GameState.LIST_CARD, len(GameState.LIST_CARD))

        Dog.SEVEN_STEPS_COUNTER = 0

        # Setup the board with 95 places and initial marble positions
        blue_marbles = [Marble(pos=str(i), is_save=False) for i in Dog.KENNEL["Blue"]]
        green_marbles = [Marble(pos=str(i), is_save=False) for i in Dog.KENNEL["Green"]]
        red_marbles = [Marble(pos=str(i), is_save=False) for i in Dog.KENNEL["Red"]]
        yellow_marbles = [Marble(pos=str(i), is_save=False) for i in Dog.KENNEL["Yellow"]]

        # Initialize players
        self.state = GameState(
            cnt_player=4,
            phase=GamePhase.SETUP,
            cnt_round=0,
            bool_card_exchanged=False,
            idx_player_started=0,                 #random.randint(0, 3),  # Randomly select start player
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
        state = self.get_state()
        player = state.list_player[state.idx_player_active]

        # Handle teammate's marbles if the player's own marbles are all in the finish zone
        if self._all_marbles_in_finish(player):
            return self._get_partner_actions(player, state)

        # Handle card exchange if it hasn't happened yet
        if not state.bool_card_exchanged:
            return self._get_exchange_actions(player)

        # Handle the player's own actions
        return self._get_player_actions(player)

    def _all_marbles_in_finish(self, player: PlayerState) -> bool:
        """Check if all marbles of the player are in the finish zone."""
        return all(int(marble.pos) >= Dog.ENDZONE[player.name][0] for marble in player.list_marble)

    def _get_partner_actions(self, player: PlayerState, state: GameState) -> List[Action]:
        """Generate actions for partner's marbles when the active player's marbles are all in the finish zone."""
        actions = []
        idx_partner = (state.idx_player_active + 2) % len(state.list_player)
        partner = state.list_player[idx_partner]

        for card in player.list_card:
            steps = GameState.get_card_steps(card.rank)
            possible_steps = steps if isinstance(steps, tuple) else (steps,)

            for marble in partner.list_marble:
                if marble.is_save:
                    continue  # Skip marbles in save zones

                for step in possible_steps:
                    pos_to = int(marble.pos) + step
                    if GameState.is_valid_move(pos_to, partner.list_marble):
                        actions.append(Action(card=card, pos_from=int(marble.pos), pos_to=pos_to))

        return actions

    def _get_exchange_actions(self, player: PlayerState) -> List[Action]:
        """Generate actions for card exchange."""
        return [Action(card=card, pos_from=None, pos_to=None) for card in player.list_card]

    def _get_player_actions(self, player: PlayerState) -> List[Action]:
        """Generate actions for the active player's own marbles."""
        actions = []

        for card in player.list_card:
            if card.rank == '7':  # Special case for card "7"
                actions.extend(self.get_seven_actions(player, card))
            elif card.rank == 'J':  # Jake card
                actions.extend(self.get_jake_actions(player, card))
            else:
                if self.state.card_active is None:
                    actions.extend(self.get_kennel_exit_actions(player))
                    actions.extend(self.get_board_move_actions(player))
                    #actions.extend(self.get_into_endzone_actions(player))

        return self._remove_duplicate_actions(actions)

    def _remove_duplicate_actions(self, actions: List[Action]) -> List[Action]:
        """Remove duplicate actions from the list."""
        unique_actions = []
        for action in actions:
            if action not in unique_actions:
                unique_actions.append(action)
        return unique_actions



    def get_kennel_exit_actions(self, player: PlayerState) -> List[Action]:
        """ Generate actions to move marbles out of the kennel. """
        actions = []
        player_kennel = Dog.KENNEL[player.name]
        player_start_position = Dog.START_POSITIONS[player.name]

        # Check if starting position is occupied
        starting_position_occupied = any(
            int(marble.pos) == player_start_position for marble in player.list_marble
        )

        if not starting_position_occupied:
            for card in player.list_card:
                if card.rank in ["K", "A"]:
                    marbles_in_kennel = [
                        marble for marble in player.list_marble if marble.pos in map(str, player_kennel)
                    ]
                    if marbles_in_kennel:
                        actions.append(
                            Action(
                                card=card,
                                pos_from=int(marbles_in_kennel[0].pos),
                                pos_to=player_start_position
                            )
                        )
                elif card.rank == "JKR":
                    marbles_in_kennel = [
                        marble for marble in player.list_marble if marble.pos in map(str, player_kennel)
                    ]
                    if marbles_in_kennel:
                        actions.append(
                            Action(
                                card=card,
                                pos_from=int(marbles_in_kennel[0].pos),
                                pos_to=player_start_position
                            )
                        )
                        self.add_substitute_actions(actions, card)
        return actions

    def add_substitute_actions(self, actions: List[Action], card: Card) -> None:
        """
        Helper function to append substitute actions for a Joker card.
        """
        for substitute_rank in ["K", "A"]:
            for suit in GameState.LIST_SUIT:
                substitute_card = Card(suit=suit, rank=substitute_rank)
                actions.append(
                    Action(
                        card=card,
                        pos_from=None,
                        pos_to=None,
                        card_swap=substitute_card
                    )
                )

    def get_board_move_actions(self, player: PlayerState) -> List[Action]:
        """Generate actions to move marbles on the board."""
        actions = []

        valid_ranks = ["2", "3", "4", "5", "6", "8", "9", "10", "Q"]
        other_ranks = ["J", "K", "A", "7"]

        for card in player.list_card:
            if card.rank not in valid_ranks and card.rank != "JKR":
                continue

            if card.rank == "JKR":
                # Generate substitute actions for Joker cards
                actions.extend(self._generate_joker_actions(player, card, valid_ranks, other_ranks))
                continue

            steps = GameState.get_card_steps(str(card.rank))

            for marble in player.list_marble:
                if marble.pos is None or int(marble.pos) < 0:
                    continue

                pos_from = int(marble.pos)
                possible_steps = steps if isinstance(steps, tuple) else (steps,)

                for step in possible_steps:
                    pos_to = pos_from + step
                    if pos_to > 63 or not marble.is_save:
                        continue

                    if GameState.is_valid_move(pos_to, player.list_marble):
                        actions.append(Action(card=card, pos_from=int(marble.pos), pos_to=pos_to))

        return actions

    def _generate_joker_actions(
        self, player: PlayerState, joker_card: Card, valid_ranks: List[str], other_ranks: List[str]
    ) -> List[Action]:
        """Generate substitute actions for Joker cards."""
        actions = []
        for marble in player.list_marble:
            if marble.pos is None or not 0 <= int(marble.pos) <= 63 or not marble.is_save:
                continue
            for rank in valid_ranks + other_ranks:
                for suit in GameState.LIST_SUIT:
                    substitute_card = Card(suit=suit, rank=rank)
                    actions.append(
                        Action(
                            card=joker_card,
                            pos_from=None,
                            pos_to=None,
                            card_swap=substitute_card,
                        )
                    )
        return actions

    def _run_joker_swap(self, player: PlayerState, card_action:Action) -> List[Action]:
        """Swap Joker card with another chosen one"""
        swapped_action = []

        swapped_action.append(
            Action(
                card=card_action.card,
                pos_from=None,
                pos_to=None,
                card_swap=card_action.card_swap,
            )
        )
        self.state.card_active = card_action.card_swap
        if card_action.card is not None:
            player.list_card.remove(card_action.card)
            self.state.list_card_discard.append(card_action.card)

        return swapped_action


    def _apply_seven_kickout(self, action: Action) -> None:
        """Kickout marbles who are overrun by a 7"""
        pos_from = action.pos_from
        pos_to = action.pos_to

        for one_player in self.state.list_player:
            player_kennel = Dog.KENNEL[one_player.name]
            all_kennel_positions = set(map(str, player_kennel))  # Ensure all positions are strings
            occupied_kennel_positions = {
                marble.pos for marble in one_player.list_marble if marble.pos in all_kennel_positions
                }
            free_kennel_positions = list(all_kennel_positions - occupied_kennel_positions)
            for marble in one_player.list_marble:
                if pos_from is not None and pos_to is not None:
                    if int(marble.pos) > pos_from and int(marble.pos) <= pos_to and not marble.is_save:
                        # Assign a new position from the free kennel positions
                        if free_kennel_positions:
                            marble.pos = int(free_kennel_positions[0])
                            marble.is_save = False

    # def get_into_endzone_actions(self, player: PlayerState) -> List[Action]:
    #     actions: List[Action] = []
    #     player_ = player.name
    #     #TBD

    #     return actions

    def get_jake_actions(self, player: PlayerState, card: Card) -> List[Action]:
        """Generate possible actions for using a Jake card"""
        actions = []
        player_marbles = [m for m in player.list_marble if m.pos is not None]
        opponent_marbles = [
            m
            for p in self.state.list_player
            if p != player
            for m in p.list_marble
            if not m.is_save
        ]

        # Generate actions by swapping with opponent marbles
        for pm in player_marbles:
            if pm.pos is not None and 0 <= int(pm.pos) <= 63:
                for om in opponent_marbles:
                    if om.pos is not None and 0 <= int(om.pos) <= 63:
                        actions.append(Action(card=card, pos_from=int(pm.pos), pos_to=int(om.pos)))
                        actions.append(Action(card=card, pos_from=int(om.pos), pos_to=int(pm.pos)))

        # If no opponent marbles are available, generate swaps within the player's own marbles
        if not actions:
            for i, m1 in enumerate(player_marbles):
                if m1.pos is not None and 0 <= int(m1.pos) <= 63:
                    for m2 in player_marbles[i + 1:]:  # Avoid duplicate pairs
                        if m2.pos is not None and 0 <= int(m2.pos) <= 63:
                            actions.append(Action(card=card, pos_from=int(m1.pos), pos_to=int(m2.pos)))
                            actions.append(Action(card=card, pos_from=int(m2.pos), pos_to=int(m1.pos)))

        return actions

    def get_seven_actions(self, player: PlayerState, card: Card) -> List[Action]:
        """
        Generate all possible actions for a card with rank '7'.
        Distribute 7 movement points across the player's marbles.
        """
        if card.rank != "7":
            return []  # Only handle "7" cards
        actions = []

        steps = GameState.get_card_steps(str(card.rank))
        for marble in player.list_marble:
            if marble.pos is None or not 0 <= int(marble.pos) <= 63:
                continue
            pos_from = int(marble.pos)
            possible_steps = steps if isinstance(steps, tuple) else (steps,)
            for step in possible_steps:
                pos_to = pos_from + step
                if pos_to > 63:
                    continue
                if GameState.is_valid_move(pos_to, player.list_marble):
                    actions.append(Action(card=card, pos_from=int(marble.pos), pos_to=pos_to))

        return actions

    def apply_action(self, action: Optional[Action]) -> None:
        """ Apply the given action to the game """
        active_player = self.state.list_player[self.state.idx_player_active]

        if not self.state.bool_card_exchanged and Dog.EXCHANGE_COUNTER <= 4 and action:
            teammate = self.state.list_player[(self.state.idx_player_active + 2) % self.state.cnt_player]
            teammate.list_card.append(action.card)
            active_player.list_card.remove(action.card)
            Dog.EXCHANGE_COUNTER += 1


            if Dog.EXCHANGE_COUNTER == 4:
                self.state.bool_card_exchanged = True
                Dog.EXCHANGE_COUNTER = 0
            self.state.idx_player_active = (self.state.idx_player_active + 1) % self.state.cnt_player
            return

        if action is None:
            self._handle_fold_cards(active_player)
            self._advance_turn()
            return

        # Handle Joker Swap separately
        if action.card is not None and action.card.rank == "JKR":
            self._run_joker_swap(active_player, action)
            print("Joker card detected")
            return

        if action.card is not None and action.card.rank == "7":
            self._apply_seven_kickout(action)

        if action.pos_from is None:
            # Handle card exchange
            if not self.state.bool_card_exchanged:
                self.exchange_cards()
        else:
            # Check if the action is for moving a partner's marble
            idx_partner = (self.state.idx_player_active + 2) % len(self.state.list_player)
            partner = self.state.list_player[idx_partner]

            if action.pos_from in [int(m.pos) for m in partner.list_marble]:
                marble_to_move = next(m for m in partner.list_marble if int(m.pos) == action.pos_from)
            else:
                marble_to_move = self._find_marble_to_move(active_player, action.pos_from)

            self._handle_action_with_card(active_player, marble_to_move, action)

            # Discard the card and advance the turn
            self._discard_card_and_advance(action, active_player)

        active_player_index = self.state.idx_player_active-1
        teammate_index = (active_player_index + 2) % len(self.state.list_player)

        active_player = self.state.list_player[active_player_index]
        teammate = self.state.list_player[teammate_index]

        active_endzone = Dog.ENDZONE[active_player.name]
        active_all_in_endzone = all(int(marble.pos) in active_endzone for marble in active_player.list_marble)

        teammate_endzone = Dog.ENDZONE[teammate.name]
        teammate_all_in_endzone = all(int(marble.pos) in teammate_endzone for marble in teammate.list_marble)

        if active_all_in_endzone and teammate_all_in_endzone:
            self.state.phase = GamePhase.FINISHED

    def _handle_fold_cards(self, active_player: PlayerState) -> None:
        """ Handle folding cards when action is None """
        if self._can_fold_cards(self.state.cnt_round, active_player):
            while active_player.list_card:
                folded_card = active_player.list_card.pop(0)
                self.state.list_card_discard.append(folded_card)

    def _find_marble_to_move(self, player: PlayerState, pos_from: int) -> Optional[Marble]:
        """ Find the marble to move based on the position """
        return next((m for m in player.list_marble if int(m.pos) == pos_from), None)

    def _handle_action_with_card(self, player: PlayerState, marble_to_move: Marble, action: Action) -> None:
        """ Handle the specific action when a card is involved """
        if action.card is not None:
            if action.card.rank == "J":
                self.apply_jake_action(player, action)
            elif action.pos_to in Dog.START_POSITIONS.values():
                self.move_marble_to_start(player, marble_to_move, action)
            elif action.pos_to in Dog.ENDZONE[player.name]:
                self.move_marble_to_finish(marble_to_move, action)
            else:
                self.move_marble_on_board(marble_to_move, action)

    def _discard_card_and_advance(self, action: Action, active_player: PlayerState) -> None:
        """ Discard the card and advance the turn """
        if action.card is not None:
            if action.card.rank == "7":
                self._handle_seven_card(action)
            else:
                active_player.list_card.remove(action.card)
                self.state.list_card_discard.append(action.card)
                self._advance_turn()

    def _handle_seven_card(self, action: Action) -> None:
        """ Handle the special case for the '7' card """
        if self.state.card_active is None:
            self.state.card_active = action.card
        if Dog.SEVEN_STEPS_COUNTER == 7:
            Dog.SEVEN_STEPS_COUNTER = 0
            self.state.card_active = None
            self.state.idx_player_active = (self.state.idx_player_active + 1) % self.state.cnt_player

    def _can_fold_cards(self, round_number: int, player: PlayerState) -> bool:
        """ Determine if it is appropriate to fold cards based on game round and state """
        # Avoid folding if it's a round with specific card count requirements
        if round_number == 6 and len(player.list_card) == 6:
            return False
        return True

    def _advance_turn(self) -> None:
        """ Advances the game to the next player and checks if the round should end. """
        self.state.idx_player_active = (self.state.idx_player_active + 1) % self.state.cnt_player
        if self.state.idx_player_active == self.state.idx_player_started:
            self.end_round()

    def move_marble_to_start(self, player: PlayerState, marble: Marble, action: Action) -> None:
        """Move a marble out of the kennel to the starting position."""
        marble.pos = action.pos_to
        marble.is_save = True

        def find_empty_kennel_position(opponent: PlayerState) -> Optional[str]:
            for position in Dog.KENNEL[opponent.name]:
                pos_str = cast(str, position)
                if not any(m.pos == pos_str for m in opponent.list_marble):
                    return pos_str
            return None

        # Check for an opponent's marble at the starting position
        for opponent in self.state.list_player:
            if opponent == player:
                continue

            opponent_marble = next(
                (m for m in opponent.list_marble if m.pos == action.pos_to), None
            )

            if opponent_marble:
                empty_position = find_empty_kennel_position(opponent)
                if empty_position:
                    opponent_marble.pos = empty_position
                    opponent_marble.is_save = False

    def move_marble_to_finish(self, marble: Marble, action: Action) -> None:
        """ Move a marble into a finish position. """
        marble.pos = action.pos_to
        marble.is_save = True

    def move_marble_on_board(self, marble: Marble, action: Action) -> None:
        """ Move a marble on the board. """
        marble.pos = action.pos_to
        marble.is_save = False

        if action.pos_to is not None and action.pos_from is not None:
            Dog.SEVEN_STEPS_COUNTER += (action.pos_to - action.pos_from)

    def apply_jake_action(self, player: PlayerState, action: Action) -> None:
        """ Apply a Jake card action to swap marbles. """
        marble_to_swap = next(
            (m for p in self.state.list_player for m in p.list_marble if int(m.pos) == action.pos_to),
            None
        )
        if marble_to_swap and action.pos_from is not None:
            marble_to_swap.pos, player.list_marble[action.pos_from].pos = (
                player.list_marble[action.pos_from].pos,
                marble_to_swap.pos
            )

    def exchange_cards(self) -> None:
        # Exchange the first card with teammate
        for idx_player, player in enumerate(self.state.list_player):
            if player.list_card:
                card_to_exchange = player.list_card[0]
                idx_player_partner = (idx_player + 2) % len(self.state.list_player)
                teammate_ = self.state.list_player[idx_player_partner]
                player.list_card.remove(card_to_exchange)
                teammate_.list_card.append(card_to_exchange)
        self.state.bool_card_exchanged = True

    def get_player_view(self, idx_player: int) -> GameState:
        """ Get the masked state for the active player (e.g. the oppontent's cards are face down)"""
        return self.state

    def end_round(self) -> None:
        self.state.cnt_round += 1
        self.state.idx_player_started = (self.state.idx_player_started + 1) % self.state.cnt_player
        self.state.idx_player_active = (self.state.idx_player_started + 1) % self.state.cnt_player
        self.state.bool_card_exchanged = False
        # Prepare next round
        self.distribute_cards()

    def distribute_cards(self) -> None:
        """
        Distribute cards to players at the start of each round.
        The number of cards decreases each round: 6, 5, 4, 3, 2.
        """
        # Cards per round: 6, 5, 4, 3, 2 (repeats after every 5 rounds)
        num_cards = 6 - ((self.state.cnt_round - 1) % 5)

        while len(self.state.list_card_draw) < num_cards*4:
            self.reshuffle_if_empty()

        for player in self.state.list_player:
            player.list_card = [self.state.list_card_draw.pop() for _ in range(num_cards)]

    def reshuffle_if_empty(self) -> None:
        self.state.list_card_draw = random.sample(GameState.LIST_CARD, len(GameState.LIST_CARD))
        self.state.list_card_discard.clear()
        random.shuffle(self.state.list_card_draw)

# pylint: disable=R0903
class RandomPlayer(Player):

    def select_action(self, state: GameState, actions: List[Action]) -> Optional[Action]:
        """ Given masked game state and possible actions, select the next action """
        if len(actions) > 0:
            return random.choice(actions)
        return None

if __name__ == '__main__':
    game = Dog()
    # idx_player_active = 0
    # player = game.state.list_player[game.state.idx_player_active]
    # player.list_card = [Card(suit='♣', rank='7'), Card(suit='♦', rank='7'),
    # Card(suit='♥', rank='7'), Card(suit='♠', rank='7'), Card(suit='♠', rank='K')]
    # print(player.list_card)
    # player.list_marble[0] = Marble(pos=str(0), is_save=True)
    # print(player.list_marble[0])
    # print(game.state.idx_player_active)

    # actions = game.get_list_action()
    # print(actions)
    # print(game.state.idx_player_active)

    # print(actions[0])
    # action = game.apply_action(actions[0])
    # print(game.state.idx_player_active)
    # print(player.list_marble[0])
    # print(game.state.card_active)

    # n_cards = len(game.state.list_player[0].list_card)
    # print(player, round, n_cards)
    # action = game.apply_action(None)
    # action = game.apply_action(None)
    # action = game.apply_action(None)
    # action = game.apply_action(None)
    # action = game.apply_action(None)
    # player = game.state.idx_player_active
    # round = game.state.cnt_round
    # n_cards = len(game.state.list_player[0].list_card)
    # print(player, round, n_cards)

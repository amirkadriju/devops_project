# server/py/hangman.py
from typing import List, Optional
import random
from enum import Enum
from server.py.game import Game, Player


class GuessLetterAction:

    def __init__(self, letter: str) -> None:
        self.letter = letter


class GamePhase(str, Enum):
    SETUP = 'setup'            # before the game has started
    RUNNING = 'running'        # while the game is running
    FINISHED = 'finished'      # when the game is finished


class HangmanGameState:

    def __init__(self, word_to_guess: str, guesses: List[str], phase: GamePhase) -> None:
        self.word_to_guess = word_to_guess
        self.guesses = guesses
        self.phase = phase


class Hangman(Game):

    def __init__(self) -> None:
        print("Welcome to Hangman!")

        # get the word to guess from player 1
        word_to_guess = input("Please enter the word to guess: ")
        
        # initialize game state variables
        self.guesses = []
        self.phase = GamePhase.SETUP
        initial_state = HangmanGameState(word_to_guess=word_to_guess,
                                         guesses=self.guesses,
                                         phase=self.phase)
        
        # call set_state to initialize game
        self.set_state(initial_state)
        pass

    def get_state(self) -> HangmanGameState:
        """ Set the game to a given state """
        return HangmanGameState(
        word_to_guess=self.word_to_guess,
        guesses=self.guesses,
        phase=self.phase
    )

    def set_state(self, state: HangmanGameState) -> None:
        """ Get the complete, unmasked game state """
        self.word_to_guess = state.word_to_guess
        self.guesses = state.guesses
        self.phase = state.phase


    def print_state(self) -> None:
        """ Print the current game state """
        pass

    def get_list_action(self) -> List[GuessLetterAction]:
        """ Get a list of possible actions for the active player """
        pass

    def apply_action(self, action: GuessLetterAction) -> None:
        """ Apply the given action to the game """
        pass

    def get_player_view(self, idx_player: int) -> HangmanGameState:
        """ Get the masked state for the active player (e.g. the oppontent's cards are face down)"""
        pass


class RandomPlayer(Player):

    def select_action(self, state: HangmanGameState, actions: List[GuessLetterAction]) -> Optional[GuessLetterAction]:
        """ Given masked game state and possible actions, select the next action """
        if len(actions) > 0:
            return random.choice(actions)
        return None


if __name__ == "__main__":

    game = Hangman()
    game_state = HangmanGameState(word_to_guess='DevOps', guesses=[], phase=GamePhase.SETUP)
    game.set_state(game_state)
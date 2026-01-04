from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Tuple
import random

# ===== ADK-style structured outputs and tools =====

class Move(str, Enum):
    ROCK = "rock"
    PAPER = "paper"
    SCISSORS = "scissors"
    BOMB = "bomb"

class RoundResult(str, Enum):
    WIN = "win"
    LOSE = "lose"
    DRAW = "draw"
    INVALID = "invalid"

@dataclass
class PlayerState:
    score: int = 0
    bomb_used: bool = False

@dataclass
class GameState:
    current_round: int = 1
    user: PlayerState = field(default_factory=PlayerState)
    bot: PlayerState = field(default_factory=PlayerState)
    game_over: bool = False
    winner: Optional[str] = None

class RPSPlusReferee:
    """Pure game engine. No I/O. Exposes ADK-style tool methods."""

    VALID_MOVES = [m.value for m in Move]
    MAX_ROUNDS = 3

    def __init__(self, state: Optional[GameState] = None) -> None:
        self.state = state or GameState()

    # --- Tools ---
    def validate_move(self, move: str) -> bool:
        return move.lower() in self.VALID_MOVES

    def is_bomb_available(self, player: str) -> bool:
        if player == "user":
            return not self.state.user.bomb_used
        return not self.state.bot.bomb_used

    def resolve_round(self, user_move: str, bot_move: str) -> Tuple[RoundResult, str]:
        u = user_move.lower()
        b = bot_move.lower()

        if not self.validate_move(u):
            return RoundResult.INVALID, "Invalid move! Valid: rock, paper, scissors, bomb."

        if u == Move.BOMB:
            if not self.is_bomb_available("user"):
                return RoundResult.INVALID, "You've already used your bomb this game."

        # Apply bomb usage flags (mutations tied to chosen moves)
        if u == Move.BOMB:
            self.state.user.bomb_used = True
        if b == Move.BOMB:
            if self.is_bomb_available("bot"):
                self.state.bot.bomb_used = True
            else:
                b = Move.ROCK  # safety fallback

        # Bomb logic
        if u == Move.BOMB and b != Move.BOMB:
            return RoundResult.WIN, "Your bomb destroys everything!"
        if b == Move.BOMB and u != Move.BOMB:
            return RoundResult.LOSE, f"Bot's bomb destroys your {u}!"
        if u == Move.BOMB and b == Move.BOMB:
            return RoundResult.DRAW, "Both bombs cancel each other out!"

        # Standard RPS
        if u == b:
            return RoundResult.DRAW, "It's a draw."

        beats = {Move.ROCK: Move.SCISSORS, Move.PAPER: Move.ROCK, Move.SCISSORS: Move.PAPER}
        if beats[Move(u)] == b:
            return RoundResult.WIN, f"{u.capitalize()} beats {b}."
        return RoundResult.LOSE, f"{b.capitalize()} beats {u}."

    def update_game_state(self, result: RoundResult) -> None:
        if result == RoundResult.WIN:
            self.state.user.score += 1
        elif result == RoundResult.LOSE:
            self.state.bot.score += 1

        self.state.current_round += 1
        if self.state.current_round > self.MAX_ROUNDS:
            self.state.game_over = True
            if self.state.user.score > self.state.bot.score:
                self.state.winner = "user"
            elif self.state.bot.score > self.state.user.score:
                self.state.winner = "bot"
            else:
                self.state.winner = "draw"

    # --- Helpers for UI/bot ---
    def get_bot_move(self) -> str:
        if self.is_bomb_available("bot") and random.random() < 0.3:
            return Move.BOMB
        return random.choice([m for m in self.VALID_MOVES if m != Move.BOMB])

    def play_turn(self, user_move: str) -> Tuple[RoundResult, str, str]:
        """Apply a single turn: user move in, bot decides, resolve and update state.
        Returns: (result, message, bot_move)
        """
        bot_move = self.get_bot_move()
        result, message = self.resolve_round(user_move, bot_move)
        # Every round counts, even invalid (wastes the round)
        self.update_game_state(result)
        return result, message, bot_move

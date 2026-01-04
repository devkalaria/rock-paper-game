from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Dict, Tuple
import random

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

class RPSPlusGame:
    VALID_MOVES = [move.value for move in Move]
    MAX_ROUNDS = 3
    
    def __init__(self):
        self.state = GameState()
        print("\n=== Rock-Paper-Scissors-Plus ===")
        print("Rules:")
        print("- Best of 3 rounds")
        print("- Valid moves: rock, paper, scissors, bomb")
        print("- Bomb beats all but can be used only once per game")
        print("- Bomb vs bomb is a draw")
        print("- Invalid input wastes the round\n")

    def validate_move(self, move: str) -> bool:
        """Validate if the move is allowed by game rules."""
        return move.lower() in self.VALID_MOVES

    def is_bomb_available(self, player: str) -> bool:
        """Check if player can use bomb."""
        if player == "user":
            return not self.state.user.bomb_used
        return not self.state.bot.bomb_used

    def resolve_round(self, user_move: str, bot_move: str) -> Tuple[RoundResult, str]:
        """Determine the outcome of a round."""
        user_move = user_move.lower()
        bot_move = bot_move.lower()

        if not self.validate_move(user_move):
            return RoundResult.INVALID, "Invalid move! You must choose: " + ", ".join(self.VALID_MOVES)

        if user_move == Move.BOMB:
            if not self.is_bomb_available("user"):
                return RoundResult.INVALID, "You've already used your bomb this game!"
            self.state.user.bomb_used = True

        if bot_move == Move.BOMB:
            if not self.is_bomb_available("bot"):
                bot_move = Move.ROCK  # Fallback if somehow bot tries to use bomb twice
            else:
                self.state.bot.bomb_used = True

        # Bomb logic
        if user_move == Move.BOMB and bot_move != Move.BOMB:
            return RoundResult.WIN, "Your bomb destroys everything!"
        if bot_move == Move.BOMB and user_move != Move.BOMB:
            return RoundResult.LOSE, f"Bot's bomb destroys your {user_move}!"
        if user_move == Move.BOMB and bot_move == Move.BOMB:
            return RoundResult.DRAW, "Both bombs cancel each other out!"

        # Standard RPS logic
        if user_move == bot_move:
            return RoundResult.DRAW, "It's a draw!"
        
        winning_conditions = {
            Move.ROCK: Move.SCISSORS,
            Move.PAPER: Move.ROCK,
            Move.SCISSORS: Move.PAPER
        }
        
        if winning_conditions[Move(user_move)] == bot_move:
            return RoundResult.WIN, f"{user_move.capitalize()} beats {bot_move}!"
        return RoundResult.LOSE, f"{bot_move.capitalize()} beats {user_move}!"

    def update_game_state(self, result: RoundResult) -> None:
        """Update game state based on round result."""
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

    def get_bot_move(self) -> str:
        """Generate a move for the bot."""
        # 30% chance to use bomb if available
        if self.is_bomb_available("bot") and random.random() < 0.3:
            return Move.BOMB
        return random.choice([m for m in self.VALID_MOVES if m != Move.BOMB])

    def play_round(self) -> None:
        """Play one round of the game."""
        if self.state.game_over:
            return
            
        print(f"\n--- Round {self.state.current_round} ---")
        print(f"Score: You {self.state.user.score} - {self.state.bot.score} Bot")
        
        user_move = input("Your move (rock/paper/scissors/bomb): ").strip()
        bot_move = self.get_bot_move()
        
        print(f"You chose: {user_move}")
        print(f"Bot chose: {bot_move}")
        
        result, message = self.resolve_round(user_move, bot_move)
        print(message)
        
        # Every round counts toward the best-of-3, even if invalid (wasted round)
        self.update_game_state(result)
        
        if self.state.game_over:
            self.end_game()

    def end_game(self) -> None:
        """Handle game end and display final results."""
        print("\n=== Game Over! ===")
        print(f"Final Score: You {self.state.user.score} - {self.state.bot.score} Bot")
        
        if self.state.winner == "user":
            print("🎉 You win the game! 🎉")
        elif self.state.winner == "bot":
            print("🤖 Bot wins the game!")
        else:
            print("🤝 It's a draw!")

def main():
    game = RPSPlusGame()
    while not game.state.game_over:
        game.play_round()

if __name__ == "__main__":
    main()

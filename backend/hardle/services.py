from typing import List
from .dictionary import is_valid_word, get_random_target
from .models import GameSession, GameStatus

COLOR_GRAY = 0
COLOR_YELLOW = 1
COLOR_GREEN = 2

class GameService:
    @staticmethod
    def create_session(mode: str = 'hard') -> GameSession:
        target = get_random_target()
        session = GameSession.objects.create(target_word=target, mode=mode)
        return session

    @staticmethod
    def get_session(session_id: str) -> GameSession:
        try:
            return GameSession.objects.get(id=session_id)
        except GameSession.DoesNotExist:
            return None

    @staticmethod
    def evaluate_guess(target: str, guess: str) -> List[int]:
        target = target.upper()
        guess = guess.upper()
        result = [COLOR_GRAY] * 5
        target_counts = {}

        # First pass: Greens and count targets
        for i, char in enumerate(target):
            target_counts[char] = target_counts.get(char, 0) + 1

        # Decrement counts for CORRECT (Green) matches
        for i, char in enumerate(guess):
            if char == target[i]:
                result[i] = COLOR_GREEN
                target_counts[char] -= 1

        # Second pass: Yellows (Present)
        for i, char in enumerate(guess):
            if result[i] == COLOR_GREEN:
                continue
            
            if char in target_counts and target_counts[char] > 0:
                result[i] = COLOR_YELLOW
                target_counts[char] -= 1
        
        return result

    @staticmethod
    def process_guess(session_id: str, guess_word: str):
        session = GameService.get_session(session_id)
        if not session:
            raise ValueError("Session not found")

        if session.status != GameStatus.IN_PROGRESS:
            raise ValueError("Game is already over")

        if guess_word == "__TIMEOUT__":
            session.status = GameStatus.LOSE
            session.save()
            return session

        guess_word = guess_word.upper()
        if len(guess_word) != 5:
            raise ValueError("Word must be 5 letters")

        if not is_valid_word(guess_word):
            raise ValueError("Not in dictionary")

        colors = GameService.evaluate_guess(session.target_word, guess_word)
        
        # Update session
        current_guesses = session.guesses
        current_guesses.append({
            "word": guess_word,
            "colors": colors
        })
        session.guesses = current_guesses  # Trigger save

        # Check Win/Loss
        if guess_word == session.target_word:
            session.status = GameStatus.WIN
        elif len(current_guesses) >= 6:
            session.status = GameStatus.LOSE
        
        session.save()
        return session

    @staticmethod
    def calculate_daily_score(session) -> int:
        """
        Daily Mode Scoring Rules:
        - GREEN letter = 10 points (Max 10 per game)
        - YELLOW letter = 5 points (Max 10 per game)
        - WIN Bonus = 100 + (green_count * 10) + (yellow_count * 5)
        - LOSS = -75
        """
        # Use string literals for safety in comparison
        current_status = str(session.status)
        
        if current_status == 'LOSE':
            return -75

        if current_status != 'WIN':
            return 0

        total_green = 0
        total_yellow = 0

        for guess_entry in session.guesses:
            colors = guess_entry.get("colors", [])
            total_green += colors.count(COLOR_GREEN)
            total_yellow += colors.count(COLOR_YELLOW)

        # Apply caps
        capped_green = min(total_green, 10)
        capped_yellow = min(total_yellow, 10)

        # Calculate score
        # Base win bonus of 100 is added to the letter scores
        score = 100 + (capped_green * 10) + (capped_yellow * 5)
        
        return score

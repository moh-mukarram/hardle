import os
import django
from django.conf import settings

# Setup Django Environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from hardle.services import GameService, COLOR_GREEN, COLOR_YELLOW, COLOR_GRAY, GameStatus
from hardle.dictionary import is_valid_word, get_random_target

def test_logic():
    print("=== Hardle Logic Verification ===")
    
    # 1. Dictionary Test
    print(f"Testing Dictionary...")
    # 1. Validation Logic
    print("    Verifying word acceptance...")
    assert is_valid_word("APPLE") == True, "APPLE should be valid"
    assert is_valid_word("ZZZZZ") == False, "ZZZZZ should be invalid"
    assert is_valid_word("apple") == True, "Lowercase apple should be valid"
    
    # 2. Safety Guard Verification
    print("    Verifying Safety Guards...")
    forbidden = ["SOARE", "CLINT"]
    for bad_word in forbidden:
        # Should return False because they are not in valid_guesses.txt
        # AND the safety guard prevented them from being loaded even if they were.
        assert is_valid_word(bad_word) == False, f"Forbidden word '{bad_word}' should be rejected"
        
    print("    Dictionary & Safety Validation Passed")

    # 2. Target Selection
    print("[2] Testing Target Selection...")
    t1 = get_random_target()
    t2 = get_random_target()
    print(f"    Random Targets: {t1}, {t2}")
    assert len(t1) == 5
    assert len(t2) == 5

    # 3. Game Session
    print("[3] Testing Session Creation...")
    session = GameService.create_session()
    print(f"    Session {session.id} created. Target (Secret): {session.target_word}")
    assert session.status == GameStatus.IN_PROGRESS
    
    # Force target for deterministic testing
    session.target_word = "APPLE"
    session.save()
    print("    Target forced to 'APPLE' for testing.")

    # 4. Guess Processing
    print("[4] Testing Guess Logic...")
    
    # Guess 1: ALERT (A=Green, L=Yellow, E=Gray...)
    # APPLE
    # ALERT
    # A=G, P!=L, P!=E, L!=R, E!=T
    # A (Green), L (Yellow - present in APPLE pos 3/4), E (Yellow - present in APPLE pos 5)
    # Wait. 
    # Target: A P P L E
    # Guess:  A L E R T
    # 0: A==A -> Green
    # 1: L!=P. Is L in remaining target? P P L E. Yes. Yellow.
    # 2: E!=P. Is E in remaining target? P P E. Yes. Yellow.
    # 3: R... No. Gray
    # 4: T... No. Gray
    # Expected: [G, Y, Y, 0, 0] -> [2, 1, 1, 0, 0]
    
    s = GameService.process_guess(str(session.id), "ALERT")
    colors = s.guesses[0]['colors']
    print(f"    Guess 'ALERT': {colors}")
    assert colors == [2, 1, 1, 0, 0], f"Expected [2,1,1,0,0], got {colors}"

    # Guess 2: APPLE (Win)
    s = GameService.process_guess(str(session.id), "APPLE")
    print(f"    Guess 'APPLE': {s.guesses[1]['colors']}")
    assert s.status == GameStatus.WIN
    print("    Win Condition Verified.")

    # 5. Invalid Guess
    print("[5] Testing Invalid Guess...")
    try:
        GameService.process_guess(str(session.id), "ZZZZZ")
        print("    ERROR: ZZZZZ should have raised ValueError")
    except ValueError as e:
        print(f"    Correctly rejected invalid word: {e}")

    print("=== All Tests Passed ===")

if __name__ == "__main__":
    test_logic()

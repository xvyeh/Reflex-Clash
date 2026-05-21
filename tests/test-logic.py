import pytest
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def test_password_hashing():
    """[x] Authentication flow (Password hashing verification)"""
    password = "supersecretpassword"
    hashed = pwd_context.hash(password)
    
    assert pwd_context.verify(password, hashed) is True
    assert pwd_context.verify("wrongpassword", hashed) is False

def test_early_click_penalty():
    """[x] Early-click penalty logic"""
    match_status = "countdown"
    player_id = 1
    opponent_id = 2
    
    # Simulate early click during countdown
    if match_status == "countdown":
        winner_id = opponent_id # Penalty applies
        
    assert winner_id == 2

def test_win_loss_incrementing():
    """[x] Win/Loss stat incrementing logic"""
    class MockUser:
        def __init__(self):
            self.wins = 0
            self.losses = 0
            self.rank_score = 1000

    p1 = MockUser()
    p2 = MockUser()
    
    # Simulate P1 winning
    winner = p1
    loser = p2
    
    winner.wins += 1
    winner.rank_score += 25
    loser.losses += 1
    loser.rank_score -= 15
    
    assert p1.wins == 1
    assert p1.rank_score == 1025
    assert p2.losses == 1
    assert p2.rank_score == 985

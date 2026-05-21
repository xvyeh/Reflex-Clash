import reflex as rx
from sqlmodel import Field
from typing import Optional, List
from datetime import datetime
from passlib.context import CryptContext
import asyncio
import time
import random

# --- Security ---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- Database Models ---
class User(rx.Model, table=True):
    username: str = Field(unique=True)
    password_hash: str
    wins: int = 0
    losses: int = 0
    rank_score: int = 1000

class MatchHistory(rx.Model, table=True):
    player_1_id: int
    player_2_id: int
    winner_id: int
    played_at: datetime = Field(default_factory=datetime.utcnow)

class ActiveMatch(rx.Model, table=True):
    """Temporary table for active matchmaking and games"""
    player_1_id: int
    player_2_id: Optional[int] = None
    status: str = "searching" # searching, countdown, active, finished
    target_time: float = 0.0
    winner_id: Optional[int] = None

class AuthState(rx.State):
    username: str = ""
    password: str = ""
    current_user: Optional[User] = None
    error: str = ""

    def set_username(self, value: str):
        self.username = value

    def set_password(self, value: str):
        self.password = value

    def register(self):
        with rx.session() as session:
            if session.query(User).filter(User.username == self.username).first():
                self.error = "Username already exists."
                return
            hashed_pwd = pwd_context.hash(self.password)
            new_user = User(username=self.username, password_hash=hashed_pwd)
            session.add(new_user)
            session.commit()
            session.refresh(new_user)
            self.current_user = new_user
            self.error = ""
            return rx.redirect("/dashboard")

    def login(self):
        with rx.session() as session:
            user = session.query(User).filter(User.username == self.username).first()
            if not user or not pwd_context.verify(self.password, user.password_hash):
                self.error = "Invalid username or password."
                return
            self.current_user = user
            self.error = ""
            return rx.redirect("/dashboard")

    def logout(self):
        self.current_user = None
        return rx.redirect("/")

class GameState(AuthState):
    current_match: Optional[ActiveMatch] = None
    game_status_msg: str = "Waiting for opponent..."
    box_color: str = "gray"
    reaction_time: str = ""

    @rx.event(background=True)
    async def find_match(self):
        async with self:
            if not self.current_user:
                yield rx.redirect("/")   # <--- Use 'yield' instead of 'return'
                return
            
            with rx.session() as session:
                # 1. Look for an open match
                open_match = session.query(ActiveMatch).filter(ActiveMatch.status == "searching").first()
                
                if open_match and open_match.player_1_id != self.current_user.id:
                    # Join match
                    open_match.player_2_id = self.current_user.id
                    open_match.status = "countdown"
                    open_match.target_time = time.time() + random.uniform(3.0, 7.0)
                    session.add(open_match)
                    session.commit()
                    session.refresh(open_match)
                    self.current_match = open_match
                else:
                    # Create match
                    new_match = ActiveMatch(player_1_id=self.current_user.id)
                    session.add(new_match)
                    session.commit()
                    session.refresh(new_match)
                    self.current_match = new_match
            
        yield rx.redirect("/arena")
        
        # Polling for opponent & countdown
        while True:
            await asyncio.sleep(0.5)
            async with self:
                with rx.session() as session:
                    match = session.query(ActiveMatch).filter(ActiveMatch.id == self.current_match.id).first()
                    if match.status == "countdown":
                        self.current_match = match
                        self.game_status_msg = "Get Ready..."
                        self.box_color = "red"
                        if time.time() >= match.target_time:
                            match.status = "active"
                            session.add(match)
                            session.commit()
                            self.box_color = "green"
                            self.game_status_msg = "CLICK NOW!"
                        yield
                    elif match.status == "finished":
                        self.current_match = match
                        self.handle_finish()
                        return

    def handle_click(self):
        if not self.current_match: return
        
        with rx.session() as session:
            match = session.query(ActiveMatch).filter(ActiveMatch.id == self.current_match.id).first()
            
            if match.status == "finished":
                return # Already over
                
            if match.status == "countdown":
                # Early click penalty
                match.status = "finished"
                match.winner_id = match.player_2_id if match.player_1_id == self.current_user.id else match.player_1_id
                self.game_status_msg = "Too early! You lose."
            elif match.status == "active":
                # Valid reaction
                match.status = "finished"
                match.winner_id = self.current_user.id
                calc_time = (time.time() - match.target_time) * 1000
                self.reaction_time = f"{calc_time:.0f}ms"
                self.game_status_msg = f"You Win! Time: {self.reaction_time}"
            
            session.add(match)
            session.commit()
            session.refresh(match)
            self.current_match = match
            
            # Record History
            self.record_stats(session, match)

    def handle_finish(self):
        if self.current_match.winner_id == self.current_user.id:
            self.game_status_msg = "You Win!"
        else:
            self.game_status_msg = "Opponent was faster. You lose."
        self.box_color = "gray"

    def record_stats(self, session, match):
        p1 = session.get(User, match.player_1_id)
        p2 = session.get(User, match.player_2_id)
        
        if match.winner_id == p1.id:
            p1.wins += 1
            p1.rank_score += 25
            p2.losses += 1
            p2.rank_score -= 15
        else:
            p2.wins += 1
            p2.rank_score += 25
            p1.losses += 1
            p1.rank_score -= 15
            
        session.add(p1)
        session.add(p2)
        history = MatchHistory(
            player_1_id=p1.id, player_2_id=p2.id, winner_id=match.winner_id
        )
        session.add(history)
        session.commit()

# --- User Interface ---
def index():
    return rx.center(
        rx.vstack(
            rx.heading("🎯 Reflex Clash", size="8"),
            rx.text("1v1 Reaction Arena"),
            rx.tabs.root(
                rx.tabs.list(
                    rx.tabs.trigger("Login", value="login"),
                    rx.tabs.trigger("Register", value="register"),
                ),
                rx.tabs.content(
                    rx.vstack(
                        rx.input(placeholder="Username", on_change=AuthState.set_username), # FIXED
                        rx.input(placeholder="Password", type="password", on_change=AuthState.set_password),
                        rx.button("Login", on_click=AuthState.login, width="100%"),
                        rx.text(AuthState.error, color="red"),
                    ),
                    value="login",
                ),
                rx.tabs.content(
                    rx.vstack(
                        rx.input(placeholder="Username", on_change=AuthState.set_username),
                        rx.input(placeholder="Password", type="password", on_change=AuthState.set_password),
                        rx.button("Register", on_click=AuthState.register, width="100%"),
                        rx.text(AuthState.error, color="red"),
                    ),
                    value="register",
                ),
                default_value="login",
            ),
            padding="2em",
            border="1px solid #eaeaea",
            border_radius="10px",
            box_shadow="lg",
        ),
        height="100vh",
    )

def dashboard():
    return rx.center(
        rx.vstack(
            rx.heading(f"Welcome, {AuthState.current_user.username}!"),
            # Replaced rx.stat with standard vstack layouts
            rx.hstack(
                rx.vstack(rx.text("Rank", weight="bold"), rx.text(AuthState.current_user.rank_score)),
                rx.vstack(rx.text("Wins", weight="bold"), rx.text(AuthState.current_user.wins)),
                rx.vstack(rx.text("Losses", weight="bold"), rx.text(AuthState.current_user.losses)),
                spacing="6",
            ),
            rx.button("Find Match ⚔️", size="4", color_scheme="red", on_click=GameState.find_match),
            rx.button("Logout", variant="ghost", on_click=AuthState.logout),
            spacing="6",
            padding="2em",
        ),
        height="100vh",
    )

def arena():
    return rx.center(
        rx.vstack(
            rx.heading(GameState.game_status_msg),
            rx.box(
                width="300px",
                height="300px",
                bg=GameState.box_color,
                border_radius="20px",
                on_click=GameState.handle_click,
                cursor="pointer",
                transition="background-color 0.1s ease",
            ),
            rx.cond(
                GameState.reaction_time != "",
                rx.text(f"Reaction Time: {GameState.reaction_time}", size="5"),
            ),
            rx.button("Back to Dashboard", on_click=rx.redirect("/dashboard")),
            spacing="5",
        ),
        height="100vh",
    )

app = rx.App()
app.add_page(index, route="/")
app.add_page(dashboard, route="/dashboard")
app.add_page(arena, route="/arena")

Markdown# 🎯 Reflex Clash: 1v1 Reaction Arena

[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Reflex](https://img.shields.io/badge/Frontend-Reflex-5E5ADB?style=for-the-badge&logo=python&logoColor=white)](https://reflex.dev/)
[![SQLAlchemy](https://img.shields.io/badge/Database-SQLite/SQLAlchemy-CC0000?style=for-the-badge&logo=sqlite&logoColor=white)](https://sqlalchemy.org/)

**Reflex Clash** is a high-speed, competitive 1v1 reflex game. Players go head-to-head to prove who has the fastest trigger finger. This project demonstrates a full-stack Python implementation using **Reflex** to bridge a React-based frontend with a FastAPI backend.

---

## 📖 Table of Contents
* [Features](#-features)
* [Architecture](#-architecture)
* [Technologies Used](#-technologies-used)
* [API Documentation](#-api-documentation)
* [Installation & Setup](#-installation--setup)
* [Testing](#-testing)

---

## ✨ Features
*   **User Authentication:** Secure Registration and Login system using `passlib` and `bcrypt`.
*   **Matchmaking:** A queue-based system to find opponents.
*   **Real-time Duels:** Millisecond-accurate reaction timing validated on the backend.
*   **Stats Tracking:** Persistent database storage for player Wins, Losses, and Rank.
*   **Embedded Documentation:** Documentation accessible directly within the frontend app.

---

## 🏗 Architecture

### Database Schema (UML)
The database utilizes a relational structure to manage users and match history.

```
classDiagram
    class User {
        +Integer id
        +String username
        +String password_hash
        +Integer wins
        +Integer losses
        +Integer rank_score
    }
    class MatchHistory {
        +Integer id
        +Integer player_1_id
        +Integer player_2_id
        +Integer winner_id
        +DateTime played_at
    }
    User "1" -- "0..*" MatchHistory : participates
🛠 Technologies UsedLayerTechnologyFrontendReflex (React-based UI in Python)BackendFastAPI (Asynchronous Server)DatabaseSQLModel / SQLAlchemy (SQLite)SecurityBCrypt Password HashingTestingPytest🔌 API DocumentationThe backend exposes a RESTful API and WebSocket-style state management.User Endpoints (REST)POST /auth/registerUsage: Registers a new user.Payload: {"username": "player1", "password": "securepassword"}POST /auth/loginUsage: Authenticates user and creates session.GET /users/meUsage: Fetches the current logged-in user's stats and ranking.Game Logic (WebSockets/State)State.find_match initiates the matchmaking queue.State.handle_click calculates reaction time and updates the DB via the FastAPI engine.🚀 Installation & SetupClone the repositoryBashgit clone [https://github.com/yourusername/reflex-clash.git](https://github.com/yourusername/reflex-clash.git)
cd reflex-clash


2.  **Create and activate a virtual environment**
    ```bash
    python -m venv venv
    source venv/bin/activate  # Windows: venv\Scripts\activate
    ```

3.  **Install dependencies**
    ```bash
    pip install reflex passlib bcrypt pytest
    
Initialize the databaseBashreflex db init
reflex db makemigrations
reflex db migrate
Run the applicationBashreflex run

    *   **Frontend:** `http://localhost:3000`
    *   **Backend API Docs:** `http://localhost:8000/docs`

---

## 🧪 Testing

To ensure every functionality works as expected, run the included test suite:

```bash
pytest tests/test_logic.py
Functionalities Tested:[x] User registration logic (Unique usernames)[x] Authentication flow (Password hashing verification)[x] Early-click penalty logic[x] Win/Loss stat incrementing logic📝 Presentation PointsReal-time Sync: How the backend ensures both players see the target simultaneously via state broadcasting.Security: Implementation of industry-standard bcrypt hashing for user credentials.Scalability: FastAPI's asynchronous handling allows for low-latency game events.Created for the Full-Stack Python Project Presentation - 2026

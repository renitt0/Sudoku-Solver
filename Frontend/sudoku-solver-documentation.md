# Sudoku Solver — Complete Project Documentation

> **Purpose of this document:** A self-contained reference for building the Sudoku Solver project from scratch. Every concept is explained at its root — not just what to do, but why. Read each section before writing any code for that phase.

---

## Table of Contents

1. [Project Overview & Architecture](#1-project-overview--architecture)
2. [Tech Stack Decisions](#2-tech-stack-decisions)
3. [Backend — Python & FastAPI](#3-backend--python--fastapi)
   - [Environment Setup](#31-environment-setup)
   - [File Structure](#32-file-structure)
   - [The Solver Algorithm](#33-the-solver-algorithm)
   - [Database Layer](#34-database-layer)
   - [Schemas & Validation](#35-schemas--validation)
   - [CRUD Operations](#36-crud-operations)
   - [API Endpoints](#37-api-endpoints)
   - [The Main App](#38-the-main-app)
   - [Database Migrations with Alembic](#39-database-migrations-with-alembic)
   - [Running the Backend](#310-running-the-backend)
4. [Frontend — Next.js](#4-frontend--nextjs)
   - [Project Setup](#41-project-setup)
   - [File Structure](#42-file-structure)
   - [API Communication Layer](#43-api-communication-layer)
   - [The Sudoku Grid Component](#44-the-sudoku-grid-component)
   - [Controls Component](#45-controls-component)
   - [The Main Page](#46-the-main-page)
   - [History Page](#47-history-page)
   - [Styling](#48-styling)
5. [Deployment](#5-deployment)
   - [Backend on Railway](#51-backend-on-railway)
   - [Frontend on Vercel](#52-frontend-on-vercel)
6. [Concepts Reference](#6-concepts-reference)
7. [Common Errors & Fixes](#7-common-errors--fixes)

---

## 1. Project Overview & Architecture

### What We're Building

A full-stack web application where a user can:
- Input a Sudoku puzzle on a 9×9 grid
- Click "Solve" to get the solution instantly
- View a history of all previously solved puzzles

### How the Pieces Communicate

Understanding the data flow before writing any code is the most important step.

```
User (Browser)
     │
     │  Types puzzle, clicks Solve
     ▼
Next.js Frontend  (Vercel — yourapp.vercel.app)
     │
     │  HTTP POST request with puzzle JSON
     │  "Hey backend, solve this board for me"
     ▼
FastAPI Backend   (Railway — yourapi.railway.app)
     │
     │  Runs backtracking algorithm
     │  Saves result to database
     │  Returns solved board as JSON
     ▼
PostgreSQL Database  (Railway — managed, same server)
     │
     │  Stores all puzzles permanently
     └──────────────────────────────────────────────
```

The frontend and backend are **completely separate applications** that only talk to each other over HTTP. This is why they can be deployed to completely different services (Vercel vs Railway) and why you can build and test them independently.

### The Language They Speak: REST + JSON

**REST** (Representational State Transfer) is a convention for structuring HTTP communication. The key rules:

| HTTP Method | Purpose | Example |
|---|---|---|
| `GET` | Retrieve data | `GET /puzzles/history` |
| `POST` | Create something new | `POST /puzzles/solve` |
| `PUT` | Replace something | `PUT /puzzles/42` |
| `DELETE` | Remove something | `DELETE /puzzles/42` |

**JSON** (JavaScript Object Notation) is the format data travels in. Both Python and JavaScript understand it natively.

```json
{
  "board": [
    [5, 3, 0, 0, 7, 0, 0, 0, 0],
    [6, 0, 0, 1, 9, 5, 0, 0, 0]
  ]
}
```

---

## 2. Tech Stack Decisions

Every choice below has a reason. Understanding the reason is more valuable than memorizing the tool.

### Python
The solver algorithm, API logic, and database operations. Python's readability makes it the best language for learning these concepts without the language itself getting in the way.

### FastAPI (not Django)
**Django** is "batteries included" — it does routing, templates, auth, admin panels, and a lot of magic behind the scenes. That magic hides what's actually happening.

**FastAPI** is lean and explicit. You write what you mean, and you see exactly what happens. For learning purposes this is far superior. Additional benefits:
- Auto-generates interactive API documentation at `/docs` (huge for testing)
- Uses Python type hints, which teaches professional-grade Python
- Built on modern async Python foundations

### PostgreSQL
The industry-standard relational database. Choosing this means the skills you build transfer directly to professional environments. We use:
- **SQLAlchemy** — an ORM (Object Relational Mapper) that lets you interact with the database using Python objects instead of raw SQL
- **Alembic** — a migration tool for versioning database schema changes

### Next.js (not plain React)
Next.js adds file-based routing, server-side rendering, and production optimizations on top of React. It's what most companies use React through, so learning Next.js means learning React + industry conventions simultaneously.

### Railway (not AWS/Heroku)
Railway is the simplest way to deploy a Python app with a PostgreSQL database together. Heroku removed its free tier; AWS requires deep DevOps knowledge. Railway gives you production infrastructure with minimal friction, which is correct for this stage of learning.

---

## 3. Backend — Python & FastAPI

### 3.1 Environment Setup

#### Why Virtual Environments?

When you install a Python package globally (without a venv), it applies to every Python project on your computer. If Project A needs `pydantic==1.9` and Project B needs `pydantic==2.0`, they will conflict. A virtual environment creates an isolated Python installation per project so packages never clash.

```bash
# Navigate to your Backend/ folder
cd Backend

# Create a virtual environment named 'venv'
python -m venv venv

# Activate it — do this every time you open a new terminal
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Your prompt changes to (venv) when it's active

# Install all dependencies
pip install fastapi uvicorn sqlalchemy alembic psycopg2-binary pydantic python-dotenv

# Save exact versions so the project is reproducible anywhere
pip freeze > requirements.txt
```

**What each package does:**

| Package | Purpose |
|---|---|
| `fastapi` | The web framework — handles HTTP routing, validation, serialization |
| `uvicorn` | The ASGI server that actually runs your FastAPI app |
| `sqlalchemy` | ORM — lets you interact with PostgreSQL using Python objects |
| `alembic` | Database migration tool — version-controls your schema changes |
| `psycopg2-binary` | PostgreSQL driver — the low-level translator between Python and Postgres |
| `pydantic` | Data validation — automatically validates incoming API data |
| `python-dotenv` | Reads `.env` files into environment variables |

---

### 3.2 File Structure

```
Backend/
├── app/
│   ├── __init__.py         ← Empty file. Tells Python "this folder is a package"
│   ├── main.py             ← FastAPI app, CORS config, router registration
│   ├── solver.py           ← Pure Python backtracking algorithm
│   ├── models.py           ← Database table definitions (SQLAlchemy)
│   ├── schemas.py          ← API data shapes and validation (Pydantic)
│   ├── database.py         ← Database connection and session management
│   ├── crud.py             ← Database read/write operations
│   └── routers/
│       ├── __init__.py     ← Empty. Makes routers/ a package too
│       └── puzzles.py      ← All /puzzles API endpoints
├── alembic/                ← Auto-generated by alembic init
├── alembic.ini             ← Auto-generated by alembic init
├── venv/                   ← Auto-managed. NEVER edit files here
├── .env                    ← Your secrets. NEVER commit to git
├── .env.example            ← Template with fake values. SAFE to commit
└── requirements.txt        ← Package list. Generated by pip freeze
```

**Why this separation?**

This layout follows the **Single Responsibility Principle**: each file has exactly one job.

- `models.py` changes only when your database structure changes
- `schemas.py` changes only when your API contract changes
- `crud.py` changes only when your database operations change
- `routers/puzzles.py` changes only when your endpoint logic changes

If you put everything in one file (common beginner mistake), a change to the database breaks your API validation code, which breaks your endpoint code, and debugging becomes a nightmare.

**The `__init__.py` file:**
Python uses `__init__.py` to recognize a folder as a "package" — a collection of modules that can be imported from. Without it, `from app.database import engine` would fail because Python wouldn't know `app` is a package. The file can be completely empty; its existence is the signal.

---

### 3.3 The Solver Algorithm

This is the purest Python in the project — no frameworks, no databases. Understanding it deeply will teach you more about programming logic than almost anything else.

#### The Data Structure

A Sudoku board is a 9×9 grid. We represent it as a **list of lists** (a 2D array). Empty cells are `0`.

```python
board = [
    [5, 3, 0, 0, 7, 0, 0, 0, 0],  # Row 0
    [6, 0, 0, 1, 9, 5, 0, 0, 0],  # Row 1
    [0, 9, 8, 0, 0, 0, 0, 6, 0],  # Row 2
    # ... 6 more rows
]

# Access a cell: board[row][col]
board[0][0]  # → 5 (top-left corner)
board[0][2]  # → 0 (empty cell, third column of first row)
```

#### Understanding Backtracking

Backtracking is a problem-solving technique that works by:
1. Making a choice
2. Exploring all consequences of that choice
3. If you hit a dead end — **undo the choice** and try the next option

Think of it as solving a maze: walk forward, hit a wall, go back to the last fork, try the other path.

In Sudoku:
- Find an empty cell
- Try placing 1
- Check if valid → if yes, recurse (solve the rest of the board)
- If recursion fails → remove 1, try 2
- If 1–9 all fail → return False (signal failure to the caller, who backtracks)

The beautiful part: **"go back" happens automatically** when a recursive function returns `False`. You don't manage a stack manually — the call stack does it for you.

#### `app/solver.py`

```python
from typing import Optional
import copy


def find_empty(board: list[list[int]]) -> Optional[tuple[int, int]]:
    """
    Scans the board left-to-right, top-to-bottom.
    Returns (row, col) of the first empty cell (value 0).
    Returns None if the board is completely filled.
    
    Why Optional[tuple[int, int]]?
    This is a type hint. It tells Python (and you reading later)
    that this function returns EITHER a tuple of two ints OR None.
    Python doesn't enforce this at runtime, but editors use it
    for autocomplete and error checking.
    """
    for row in range(9):       # row = 0, 1, 2, ... 8
        for col in range(9):   # col = 0, 1, 2, ... 8
            if board[row][col] == 0:
                return (row, col)
    return None  # No empty cells found — board is complete


def is_valid(board: list[list[int]], row: int, col: int, num: int) -> bool:
    """
    Returns True if placing 'num' at (row, col) violates no Sudoku rules.
    Returns False if it creates any conflict.
    
    The three Sudoku constraints:
    1. No duplicate in the same row
    2. No duplicate in the same column
    3. No duplicate in the same 3x3 box
    """

    # Constraint 1: Check the row
    # board[row] gives us the entire row as a list
    # 'in' checks membership — runs in O(n) time
    if num in board[row]:
        return False

    # Constraint 2: Check the column
    # board[r][col] for each r gives us the entire column
    # This is a list comprehension — a compact way to build a list
    column = [board[r][col] for r in range(9)]
    if num in column:
        return False

    # Constraint 3: Check the 3x3 box
    # First, find the top-left corner of the box this cell belongs to.
    # Integer division (//) discards the remainder.
    # Examples:
    #   row=0 → (0//3)*3 = 0   | row=4 → (4//3)*3 = 3
    #   row=7 → (7//3)*3 = 6   | col=8 → (8//3)*3 = 6
    box_row_start = (row // 3) * 3
    box_col_start = (col // 3) * 3

    for r in range(box_row_start, box_row_start + 3):
        for c in range(box_col_start, box_col_start + 3):
            if board[r][c] == num:
                return False

    return True  # Passed all three checks


def solve(board: list[list[int]]) -> bool:
    """
    Solves the board IN-PLACE using recursive backtracking.
    
    'In-place' means we modify the list that was passed to us.
    Python lists are mutable objects passed by reference — when solve()
    changes board[row][col], the change is visible in the caller too.
    This is what allows tracked progress across recursive calls.
    
    Returns True when the puzzle is fully solved.
    Returns False when this branch leads to no solution (triggers backtracking).
    """

    # Base case: find_empty returns None when all cells are filled
    # If no empty cells exist, the puzzle must be solved
    empty = find_empty(board)
    if empty is None:
        return True  # ← Recursion unwinds from here: every caller gets True

    row, col = empty  # Unpack the tuple into two variables

    for num in range(1, 10):  # Try 1 through 9

        if is_valid(board, row, col, num):
            board[row][col] = num  # Tentatively place the number

            # Recursive call: try to solve the rest of the board
            # If this returns True, everything worked — propagate True upward
            if solve(board):
                return True

            # If we reach here, solve() returned False
            # Something downstream failed — undo our placement (backtrack)
            board[row][col] = 0

    # No number 1-9 works in this cell
    # Signal failure to the caller, which will backtrack its own last placement
    return False


def validate_puzzle(board: list[list[int]]) -> bool:
    """
    Checks the initial puzzle state for conflicts before attempting to solve.
    
    We can't use is_valid() directly on filled cells because is_valid()
    would find the number itself at its own position and report a conflict.
    Solution: temporarily remove each number, check validity, restore it.
    """
    for row in range(9):
        for col in range(9):
            num = board[row][col]
            if num != 0:
                board[row][col] = 0              # Temporarily remove
                if not is_valid(board, row, col, num):
                    board[row][col] = num        # Restore before returning
                    return False
                board[row][col] = num            # Restore
    return True
```

**Test the solver in isolation:**

```bash
python -c "
from app.solver import solve, validate_puzzle
import copy

board = [
    [5,3,0,0,7,0,0,0,0],
    [6,0,0,1,9,5,0,0,0],
    [0,9,8,0,0,0,0,6,0],
    [8,0,0,0,6,0,0,0,3],
    [4,0,0,8,0,3,0,0,1],
    [7,0,0,0,2,0,0,0,6],
    [0,6,0,0,0,0,2,8,0],
    [0,0,0,4,1,9,0,0,5],
    [0,0,0,0,8,0,0,7,9]
]

print('Valid:', validate_puzzle(copy.deepcopy(board)))
solve(board)
for row in board:
    print(row)
"
```

---

### 3.4 Database Layer

#### Understanding the ORM Pattern

Without an ORM (Object Relational Mapper), you'd write raw SQL:

```python
# Without ORM — raw SQL
cursor.execute("INSERT INTO puzzles (initial_board, is_solvable) VALUES (%s, %s)", (board_json, "yes"))
```

With SQLAlchemy ORM, you work with Python objects:

```python
# With ORM — pure Python
puzzle = Puzzle(initial_board=board, is_solvable="yes")
db.add(puzzle)
db.commit()
```

The ORM translates your Python into SQL automatically. This means you write less SQL, your code is more readable, and switching databases (e.g., PostgreSQL → MySQL) requires minimal changes.

#### Understanding the Session Pattern

A **session** in SQLAlchemy is like a transaction — a unit of work with the database. You open a session, do some operations, commit (save permanently), and close. If anything fails, you can rollback (undo) instead of commit.

The `get_db()` generator function handles this lifecycle automatically for every request.

#### `app/database.py`

```python
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# load_dotenv() reads your .env file and loads each KEY=VALUE pair
# into Python's os.environ dictionary.
# Call this before any os.getenv() calls.
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
# DATABASE_URL format: postgresql://username:password@host:port/dbname
# Example: postgresql://postgres:admin123@localhost:5432/sudoku_db

# create_engine() sets up the connection pool.
# It doesn't actually connect to the database yet — connections are
# made lazily, only when you first execute a query.
engine = create_engine(DATABASE_URL)

# sessionmaker() is a factory — it produces Session objects.
# Each Session is one conversation with the database.
# autocommit=False: changes must be explicitly committed (db.commit())
# autoflush=False:  SQLAlchemy won't auto-sync state before each query
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base is the foundation class for all your ORM models.
# It maintains a registry (Base.metadata) of every model class,
# which SQLAlchemy uses to create/manage tables.
Base = declarative_base()


def get_db():
    """
    FastAPI dependency that manages the database session lifecycle.
    
    This is a generator function ('yield' instead of 'return').
    
    How it works with FastAPI:
    1. FastAPI sees 'db: Session = Depends(get_db)' in an endpoint
    2. It calls get_db() and runs it until the 'yield'
    3. It passes the yielded 'db' session to the endpoint function
    4. After the endpoint finishes (success or exception), FastAPI
       resumes get_db() execution past the yield
    5. The 'finally' block closes the session — ALWAYS, even on error
    
    The 'yield' keyword is what makes cleanup guaranteed.
    A plain 'return' would close the function before cleanup could run.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

#### `app/models.py`

```python
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from .database import Base

# The dot in '.database' is a relative import.
# It means: "look in the same package (app/) for the database module"
# This works because of the __init__.py file in app/


class Puzzle(Base):
    """
    This class IS the 'puzzles' table in PostgreSQL.
    
    SQLAlchemy reads the class attributes (Column definitions) and knows:
    - What columns to create
    - What types they should be
    - What constraints they have (nullable, primary_key, etc.)
    
    When you call Base.metadata.create_all(engine), SQLAlchemy
    generates and executes the SQL to create this table:
    
    CREATE TABLE puzzles (
        id SERIAL PRIMARY KEY,
        initial_board JSONB NOT NULL,
        solved_board JSONB,
        is_solvable VARCHAR(10) DEFAULT 'unknown',
        created_at TIMESTAMPTZ DEFAULT NOW(),
        solve_time_ms INTEGER
    );
    """
    __tablename__ = "puzzles"

    id = Column(Integer, primary_key=True, index=True)
    # primary_key=True: this column uniquely identifies each row
    # index=True: PostgreSQL builds a B-tree index for fast id lookups

    # JSONB is PostgreSQL's binary JSON format.
    # Faster than plain JSON for reads, supports indexing.
    # SQLAlchemy serializes your Python list to JSON automatically.
    initial_board = Column(JSONB, nullable=False)
    # nullable=False: this column MUST have a value on every insert

    solved_board = Column(JSONB, nullable=True)
    # nullable=True (the default): can be NULL for unsolvable puzzles

    is_solvable = Column(String(10), default="unknown")
    # Will contain "yes", "no", or "unknown"

    # server_default means the DATABASE sets this value, not Python.
    # func.now() generates: DEFAULT NOW() in the CREATE TABLE SQL.
    # More reliable than Python's datetime.now() because it uses
    # the DB server clock, not your application server clock.
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    solve_time_ms = Column(Integer, nullable=True)
    # Milliseconds the backtracking algorithm took. Great data to collect.
```

---

### 3.5 Schemas & Validation

#### What Pydantic Does

Pydantic validates data **before** it reaches your business logic. When a POST request arrives with a body, FastAPI feeds it through your Pydantic schema. If anything is wrong — wrong type, missing field, failed custom validation — FastAPI automatically returns a `422 Unprocessable Entity` error with a detailed explanation. Your endpoint function never even runs.

#### The Difference: Models vs Schemas

This confuses many beginners. They look similar but serve entirely different purposes:

| | SQLAlchemy Models | Pydantic Schemas |
|---|---|---|
| **File** | `models.py` | `schemas.py` |
| **Purpose** | Define database tables | Define API data shapes |
| **Used by** | SQLAlchemy → PostgreSQL | FastAPI → HTTP requests/responses |
| **Validates** | Database constraints | Input/output data format |

#### `app/schemas.py`

```python
from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime


class PuzzleSubmit(BaseModel):
    """
    Defines what the client MUST send when calling POST /puzzles/solve.
    
    Pydantic automatically validates that:
    - 'board' key exists in the request body JSON
    - 'board' is a list of lists of integers
    - Our custom validator below also passes
    
    If any check fails, FastAPI returns 422 with a clear error message.
    The endpoint function is never called.
    """
    board: list[list[int]]
    # Type hints here are enforced by Pydantic at runtime.
    # list[list[int]] means: a list, where each element is also a list,
    # where each element of that inner list is an integer.

    @field_validator('board')
    @classmethod
    def validate_board_shape(cls, board):
        """
        Custom validation beyond basic type checking.
        
        @field_validator('board') tells Pydantic to run this function
        after the basic type validation passes.
        
        @classmethod means the first argument is the class (cls), not
        an instance (self) — Pydantic requires this for validators.
        
        Raise ValueError to reject the data. Pydantic catches it and
        formats it into a proper 422 error response automatically.
        """
        if len(board) != 9:
            raise ValueError(f"Board must have 9 rows, got {len(board)}")

        for i, row in enumerate(board):
            # enumerate() gives (index, value) pairs:
            # [(0, row0), (1, row1), ...] — useful for error messages
            if len(row) != 9:
                raise ValueError(f"Row {i} must have 9 columns, got {len(row)}")
            for cell in row:
                if not (0 <= cell <= 9):
                    raise ValueError(f"Cell values must be 0-9, got {cell}")

        return board  # Always return the (potentially modified) value


class PuzzleResponse(BaseModel):
    """
    Defines what the API RETURNS after processing a puzzle.
    
    FastAPI serializes the SQLAlchemy Puzzle object into this shape
    automatically, then converts it to JSON for the HTTP response.
    
    Optional[X] means the field can be either X or None.
    This is important for solved_board (None when unsolvable) and
    solve_time_ms (None for puzzles not yet processed).
    """
    id: int
    initial_board: list[list[int]]
    solved_board: Optional[list[list[int]]]
    is_solvable: str
    solve_time_ms: Optional[int]
    created_at: datetime

    model_config = {"from_attributes": True}
    # Without this, Pydantic can only read from plain dicts.
    # With this, Pydantic can read from SQLAlchemy model instances
    # by accessing attributes directly (puzzle.id, puzzle.board, etc.)
    # This is what allows: return db_puzzle (a Puzzle ORM object)
    # to work as a PuzzleResponse.
```

---

### 3.6 CRUD Operations

CRUD = Create, Read, Update, Delete. Every database-backed application reduces to these four operations. Isolating them in their own file means:
- Your endpoints (`routers/puzzles.py`) handle HTTP logic
- Your CRUD functions handle database logic
- Neither bleeds into the other

#### `app/crud.py`

```python
from sqlalchemy.orm import Session
from . import models


def create_puzzle(
    db: Session,
    initial_board: list,
    solved_board: list | None,
    is_solvable: str,
    solve_time_ms: int | None
) -> models.Puzzle:
    """
    Inserts a new row into the puzzles table.
    
    The three-step database write pattern:
    1. db.add(obj)     — stages the object (like 'git add')
    2. db.commit()     — persists to disk (like 'git commit')
    3. db.refresh(obj) — re-reads from DB to get auto-generated values
    
    After insert, PostgreSQL auto-generates the 'id' and 'created_at'.
    db.refresh() re-fetches the row so our Python object has these values.
    Without refresh(), accessing db_puzzle.id would give None.
    """
    db_puzzle = models.Puzzle(
        initial_board=initial_board,
        solved_board=solved_board,
        is_solvable=is_solvable,
        solve_time_ms=solve_time_ms
    )
    db.add(db_puzzle)
    db.commit()
    db.refresh(db_puzzle)
    return db_puzzle


def get_puzzle(db: Session, puzzle_id: int) -> models.Puzzle | None:
    """
    Fetches one puzzle by its primary key.
    
    SQLAlchemy generates: SELECT * FROM puzzles WHERE id = puzzle_id LIMIT 1
    
    .first() returns the first result or None.
    Never raises an exception if the id doesn't exist.
    """
    return (
        db.query(models.Puzzle)
        .filter(models.Puzzle.id == puzzle_id)
        .first()
    )


def get_all_puzzles(db: Session, skip: int = 0, limit: int = 20) -> list[models.Puzzle]:
    """
    Fetches puzzles with pagination support.
    
    'skip' and 'limit' implement cursor-based pagination:
    - Page 1: skip=0,  limit=20 → rows 1–20
    - Page 2: skip=20, limit=20 → rows 21–40
    - Page 3: skip=40, limit=20 → rows 41–60
    
    SQLAlchemy generates:
    SELECT * FROM puzzles ORDER BY created_at DESC OFFSET skip LIMIT limit
    
    Pagination is critical: without it, fetching 100,000 puzzle records
    would load all of them into memory at once. With pagination, you
    load only what's needed for the current page view.
    """
    return (
        db.query(models.Puzzle)
        .order_by(models.Puzzle.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
```

---

### 3.7 API Endpoints

#### `app/routers/puzzles.py`

```python
import time
import copy
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
# '..' navigates up one level: from routers/ to app/
# Then 'database' refers to app/database.py

from ..schemas import PuzzleSubmit, PuzzleResponse
from ..solver import solve, validate_puzzle
from .. import crud


router = APIRouter(
    prefix="/puzzles",
    # All routes in this router start with /puzzles
    # e.g., @router.post("/solve") becomes POST /puzzles/solve
    
    tags=["puzzles"]
    # Groups endpoints together in the /docs UI
)


@router.post("/solve", response_model=PuzzleResponse, status_code=201)
def solve_puzzle(puzzle: PuzzleSubmit, db: Session = Depends(get_db)):
    """
    POST /puzzles/solve
    
    FastAPI reads this function signature and automatically:
    
    1. puzzle: PuzzleSubmit
       Reads the request body JSON, validates it against PuzzleSubmit schema.
       If invalid → 422 response. If valid → puzzle is a PuzzleSubmit instance.
    
    2. db: Session = Depends(get_db)
       Calls get_db(), gets the Session, injects it here.
       After this function returns, FastAPI resumes get_db() to close the session.
       You NEVER call get_db() yourself.
    
    3. response_model=PuzzleResponse
       After this function returns a value, FastAPI validates it against
       PuzzleResponse and serializes it to JSON automatically.
    
    4. status_code=201
       Returns HTTP 201 Created instead of 200 OK.
       201 is semantically correct for endpoints that create a new resource.
    """

    # validate_puzzle checks the initial board for conflicts
    # We deepcopy because validate_puzzle temporarily modifies the board
    # and we don't want to corrupt our original data
    if not validate_puzzle(copy.deepcopy(puzzle.board)):
        raise HTTPException(
            status_code=400,
            # 400 Bad Request: the client sent invalid data
            detail="Invalid puzzle: initial board contains conflicting numbers"
        )
        # HTTPException stops execution immediately.
        # FastAPI catches it and returns the HTTP error response.
        # Code after this line does NOT run.

    # Solve on a deep copy — solve() modifies the board in-place
    # We want to keep puzzle.board as the original unsolved state
    board_to_solve = copy.deepcopy(puzzle.board)

    start_time = time.time()
    solvable = solve(board_to_solve)
    elapsed_ms = int((time.time() - start_time) * 1000)

    db_puzzle = crud.create_puzzle(
        db=db,
        initial_board=puzzle.board,
        solved_board=board_to_solve if solvable else None,
        is_solvable="yes" if solvable else "no",
        solve_time_ms=elapsed_ms
    )

    return db_puzzle
    # FastAPI sees 'response_model=PuzzleResponse', takes this Puzzle ORM object,
    # reads its attributes using from_attributes=True, and serializes to JSON


@router.get("/history", response_model=list[PuzzleResponse])
def get_history(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    """
    GET /puzzles/history
    GET /puzzles/history?skip=20&limit=10
    
    'skip' and 'limit' are query parameters.
    FastAPI detects them automatically because they are:
    - NOT path parameters (not in {braces} in the route)
    - NOT in the request body (no BaseModel type hint)
    Therefore → they must come from the query string (?key=value)
    
    They have default values, so they're optional.
    """
    return crud.get_all_puzzles(db, skip=skip, limit=limit)


@router.get("/{puzzle_id}", response_model=PuzzleResponse)
def get_puzzle(puzzle_id: int, db: Session = Depends(get_db)):
    """
    GET /puzzles/42
    
    {puzzle_id} in the route decorator is a path parameter.
    FastAPI extracts the value from the URL and passes it to the function.
    The type hint 'puzzle_id: int' tells FastAPI to validate and convert
    the string from the URL into an integer.
    If someone requests GET /puzzles/abc, FastAPI returns 422 automatically.
    """
    puzzle = crud.get_puzzle(db, puzzle_id)
    if puzzle is None:
        raise HTTPException(
            status_code=404,
            # 404 Not Found: the resource doesn't exist
            detail=f"Puzzle with id {puzzle_id} not found"
        )
    return puzzle
```

---

### 3.8 The Main App

#### `app/main.py`

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from .routers import puzzles

# Create all tables that don't yet exist in PostgreSQL.
# SQLAlchemy reads Base.metadata (which knows about all models
# because each model imports and inherits from Base) and compares
# with what exists in the database.
# It creates missing tables. It never deletes or alters existing ones.
# Note: In production, use Alembic migrations instead (see Section 3.9)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Sudoku Solver API",
    description="REST API that solves Sudoku puzzles using backtracking",
    version="1.0.0"
    # These appear in the auto-generated docs at /docs
)

# --- CORS Configuration ---
# CORS (Cross-Origin Resource Sharing) is a browser security mechanism.
#
# By default, browsers block JavaScript from making HTTP requests to
# a different "origin" (protocol + domain + port) than the current page.
#
# Your Next.js app runs on: http://localhost:3000 (during development)
# Your FastAPI app runs on:  http://localhost:8000
#
# Different ports = different origins = browser blocks the request.
#
# This middleware adds response headers that tell the browser:
# "I (the API) explicitly allow requests from these origins."
# The browser then allows the request to go through.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://*.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],   # GET, POST, PUT, DELETE, OPTIONS, etc.
    allow_headers=["*"],   # Content-Type, Authorization, etc.
)

# Register the puzzles router
# All endpoints defined in routers/puzzles.py are now live.
# The router's prefix "/puzzles" combines with each endpoint's path.
app.include_router(puzzles.router)


@app.get("/health")
def health_check():
    """
    Simple liveness check endpoint.
    Used by Railway to verify the app is running.
    Always returns instantly.
    """
    return {"status": "ok"}
```

#### `.env` file

```
DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/sudoku_db
```

#### `.env.example` file (commit this, not `.env`)

```
DATABASE_URL=postgresql://your_username:your_password@localhost:5432/sudoku_db
```

#### `.gitignore` additions

```gitignore
# Secrets
.env

# Virtual environment (reproducible from requirements.txt)
venv/

# Python cache (auto-generated, not needed in git)
__pycache__/
*.pyc
*.pyo
*.pyd
.Python

# IDE files
.vscode/
.idea/
```

---

### 3.9 Database Migrations with Alembic

#### Why Migrations?

`Base.metadata.create_all()` is fine for development but dangerous in production. It creates tables but **never alters or deletes them**. If you add a column to a model and redeploy, the real database column won't be added — only new tables would be created.

Alembic solves this by creating versioned migration scripts. Each script describes exactly what changed (add column, rename table, etc.). Running migrations applies changes in order. It's git for your database schema.

```bash
# Initialize Alembic — run once, from Backend/ folder
alembic init alembic
```

This creates `alembic/` folder and `alembic.ini`. Now configure them:

**Edit `alembic.ini`** — find this line and update it:
```ini
# Before:
sqlalchemy.url = driver://user:pass@localhost/dbname

# After (point to your .env variable):
sqlalchemy.url = postgresql://postgres:yourpassword@localhost:5432/sudoku_db
```

**Edit `alembic/env.py`** — find the `target_metadata` line and replace the section:

```python
# Add these imports at the top of env.py
import os
from dotenv import load_dotenv
from app.models import Base  # Import your models so Alembic knows about them

load_dotenv()

# Replace the target_metadata line:
target_metadata = Base.metadata

# Replace the run_migrations_online() database URL section:
def run_migrations_online():
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = os.getenv("DATABASE_URL")
    # ... rest of the function stays the same
```

**Create and apply your first migration:**

```bash
# Auto-detect differences between your models and the current DB
# and generate a migration script
alembic revision --autogenerate -m "create puzzles table"

# Apply all pending migrations to the database
alembic upgrade head

# Other useful commands:
alembic current          # Show current migration version
alembic history          # Show all migrations
alembic downgrade -1     # Roll back the last migration
```

---

### 3.10 Running the Backend

```bash
# Always activate venv first (every new terminal session)
venv\Scripts\activate   # Windows
source venv/bin/activate  # macOS/Linux

# Start the development server
uvicorn app.main:app --reload

# Breaking this down:
# uvicorn      → the ASGI server
# app.main     → the module path (app package, main.py file)
# :app         → the FastAPI object named 'app' inside main.py
# --reload     → restart when any .py file changes (dev only, never in production)
```

**Now open in your browser:**

- `http://localhost:8000/health` → should return `{"status": "ok"}`
- `http://localhost:8000/docs` → interactive API documentation (test all endpoints here)
- `http://localhost:8000/redoc` → alternative documentation view

**Test a solve via the `/docs` UI:**
1. Open `http://localhost:8000/docs`
2. Click `POST /puzzles/solve`
3. Click "Try it out"
4. Paste the board JSON from Section 3.3
5. Click "Execute"
6. You should see a `201` response with the solved board

---

## 4. Frontend — Next.js

### 4.1 Project Setup

```bash
# Navigate to Frontend/ folder
cd Frontend

# Create a new Next.js project
npx create-next-app@latest . --typescript --tailwind --app --no-src-dir
# Options explained:
# --typescript  → Use TypeScript (catches errors at compile time)
# --tailwind    → Include Tailwind CSS for styling
# --app         → Use the App Router (modern Next.js, not the old Pages Router)
# --no-src-dir  → Put files in root, not in a /src folder (simpler structure)
# '.'           → Create in current folder (Frontend/)

# Start the development server
npm run dev
# Open http://localhost:3000
```

**Install any additional dependencies:**

```bash
npm install lucide-react   # Icon library (optional but useful)
```

---

### 4.2 File Structure

```
Frontend/
├── app/
│   ├── layout.tsx          ← Root layout, wraps every page (nav, fonts)
│   ├── page.tsx            ← Home page (the main solver UI)
│   ├── history/
│   │   └── page.tsx        ← Puzzle history page
│   └── globals.css         ← Global styles + Tailwind imports
├── components/
│   ├── SudokuGrid.tsx      ← The interactive 9x9 grid
│   └── Controls.tsx        ← Solve/Clear/Reset buttons
├── lib/
│   └── api.ts              ← All backend API calls (single source of truth)
├── .env.local              ← Frontend environment variables
├── next.config.js
└── package.json
```

**Why put API calls in `lib/api.ts`?**

If you scatter `fetch()` calls throughout your components, changing the API URL or structure means hunting through every file. With everything in `api.ts`, you change it once. This is the **Don't Repeat Yourself** (DRY) principle.

---

### 4.3 API Communication Layer

#### `.env.local`

```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

`NEXT_PUBLIC_` prefix is required by Next.js to expose environment variables to the browser. Without this prefix, the variable is only available server-side.

#### `lib/api.ts`

```typescript
// TypeScript type aliases — define the shape of data once, reuse everywhere
// This is TypeScript's equivalent of Python's type hints
export type Board = number[][];

export interface PuzzleResponse {
  id: number;
  initial_board: Board;
  solved_board: Board | null;   // 'null' is TypeScript's equivalent of Python's None
  is_solvable: string;
  solve_time_ms: number | null;
  created_at: string;
}

// Read the API URL from environment variable
// The '||' provides a fallback if the variable isn't set
const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";


export async function solvePuzzle(board: Board): Promise<PuzzleResponse> {
  /**
   * Sends a POST request to the backend to solve the puzzle.
   * 
   * async/await is JavaScript's way of handling asynchronous operations.
   * 'await' pauses execution until the Promise resolves (the HTTP response arrives).
   * Without async/await, you'd need to use .then() chains — much harder to read.
   * 
   * fetch() is the browser's built-in HTTP client.
   */
  const response = await fetch(`${API_BASE}/puzzles/solve`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      // This header tells the server the body is JSON.
      // Without it, some servers don't parse the body correctly.
    },
    body: JSON.stringify({ board }),
    // JSON.stringify converts the JavaScript object to a JSON string.
    // { board } is shorthand for { board: board } — ES6 shorthand property.
  });

  if (!response.ok) {
    // response.ok is true for 2xx status codes, false for 4xx/5xx
    const errorData = await response.json();
    throw new Error(errorData.detail || "Failed to solve puzzle");
    // Throwing an error makes it catchable in the component with try/catch
  }

  return response.json();
  // response.json() parses the JSON body into a JavaScript object
  // We annotate the return type as PuzzleResponse for type safety
}


export async function getPuzzleHistory(
  skip = 0,
  limit = 20
): Promise<PuzzleResponse[]> {
  const response = await fetch(
    `${API_BASE}/puzzles/history?skip=${skip}&limit=${limit}`
  );

  if (!response.ok) {
    throw new Error("Failed to fetch history");
  }

  return response.json();
}


export async function getPuzzleById(id: number): Promise<PuzzleResponse> {
  const response = await fetch(`${API_BASE}/puzzles/${id}`);

  if (!response.ok) {
    throw new Error(`Puzzle ${id} not found`);
  }

  return response.json();
}
```

---

### 4.4 The Sudoku Grid Component

#### `components/SudokuGrid.tsx`

```tsx
"use client";
// "use client" tells Next.js this component runs in the browser.
// Without it, Next.js tries to render it on the server, where
// useState and event handlers don't work (no browser APIs available).

import { useState } from "react";
import type { Board } from "@/lib/api";
// '@/' is an alias for the project root, configured by Next.js automatically.
// '@/lib/api' → Frontend/lib/api.ts

interface SudokuGridProps {
  board: Board;
  onChange?: (newBoard: Board) => void;
  // '?' makes the prop optional
  // When readOnly is true, onChange won't be called
  readOnly?: boolean;
  solvedBoard?: Board | null;
  // The solved board to compare against for highlighting
}

export default function SudokuGrid({
  board,
  onChange,
  readOnly = false,
  solvedBoard = null,
}: SudokuGridProps) {
  
  const handleCellChange = (row: number, col: number, value: string) => {
    if (readOnly || !onChange) return;

    // Convert input string to number (empty string becomes 0)
    const num = value === "" ? 0 : parseInt(value, 10);

    // Reject invalid input
    if (isNaN(num) || num < 0 || num > 9) return;

    // IMMUTABLE UPDATE: create a new board array rather than mutating
    // In React, you must NEVER directly mutate state.
    // React compares old state to new state to decide what to re-render.
    // If you mutate in place, old === new (same reference) → React sees no change → no re-render.
    // By creating a new array, React sees old !== new → triggers re-render.
    const newBoard: Board = board.map((r, rowIndex) =>
      r.map((cell, colIndex) => {
        if (rowIndex === row && colIndex === col) {
          return num;
        }
        return cell;
      })
    );

    onChange(newBoard);
  };

  return (
    <div
      style={{
        display: "grid",
        gridTemplateColumns: "repeat(9, 1fr)",
        width: "fit-content",
        border: "2px solid #333",
      }}
    >
      {board.map((row, rowIndex) =>
        row.map((cell, colIndex) => {
          // Determine if this cell was empty initially but filled by the solver
          const wasSolvedByAlgorithm =
            solvedBoard !== null &&
            board[rowIndex][colIndex] === 0 &&
            solvedBoard[rowIndex][colIndex] !== 0;

          // Determine box borders — thicker lines every 3 cells
          const borderRight =
            (colIndex + 1) % 3 === 0 && colIndex !== 8
              ? "2px solid #333"
              : "1px solid #bbb";
          const borderBottom =
            (rowIndex + 1) % 3 === 0 && rowIndex !== 8
              ? "2px solid #333"
              : "1px solid #bbb";

          // What value to display: the solved value if solved, else original
          const displayValue =
            solvedBoard && cell === 0
              ? solvedBoard[rowIndex][colIndex]
              : cell;

          return (
            <input
              key={`${rowIndex}-${colIndex}`}
              // React requires a unique 'key' on list elements for efficient re-rendering.
              // It uses keys to track which items changed, added, or removed.
              type="text"
              maxLength={1}
              value={displayValue === 0 ? "" : displayValue}
              onChange={(e) => handleCellChange(rowIndex, colIndex, e.target.value)}
              readOnly={readOnly || cell !== 0}
              // Pre-filled cells (non-zero in original board) are always read-only
              style={{
                width: "52px",
                height: "52px",
                textAlign: "center",
                fontSize: "20px",
                fontWeight: cell !== 0 ? "bold" : "normal",
                // Original numbers are bold; solved numbers are normal weight
                border: "none",
                borderRight,
                borderBottom,
                backgroundColor: wasSolvedByAlgorithm ? "#e8f5e9" : "white",
                color: wasSolvedByAlgorithm ? "#2e7d32" : "#1a1a2e",
                cursor: readOnly || cell !== 0 ? "default" : "text",
                outline: "none",
              }}
            />
          );
        })
      )}
    </div>
  );
}
```

---

### 4.5 Controls Component

#### `components/Controls.tsx`

```tsx
interface ControlsProps {
  onSolve: () => void;
  onClear: () => void;
  onReset: () => void;
  isLoading: boolean;
  isSolved: boolean;
}

export default function Controls({
  onSolve,
  onClear,
  onReset,
  isLoading,
  isSolved,
}: ControlsProps) {
  return (
    <div style={{ display: "flex", gap: "12px", marginTop: "20px" }}>
      <button
        onClick={onSolve}
        disabled={isLoading || isSolved}
        style={{
          padding: "12px 24px",
          backgroundColor: isLoading || isSolved ? "#9e9e9e" : "#1976d2",
          color: "white",
          border: "none",
          borderRadius: "6px",
          fontSize: "16px",
          cursor: isLoading || isSolved ? "not-allowed" : "pointer",
          transition: "background-color 0.2s",
        }}
      >
        {isLoading ? "Solving..." : isSolved ? "Solved ✓" : "Solve"}
      </button>

      <button
        onClick={onReset}
        style={{
          padding: "12px 24px",
          backgroundColor: "#388e3c",
          color: "white",
          border: "none",
          borderRadius: "6px",
          fontSize: "16px",
          cursor: "pointer",
        }}
      >
        Reset
      </button>

      <button
        onClick={onClear}
        style={{
          padding: "12px 24px",
          backgroundColor: "#f5f5f5",
          color: "#333",
          border: "1px solid #ccc",
          borderRadius: "6px",
          fontSize: "16px",
          cursor: "pointer",
        }}
      >
        Clear All
      </button>
    </div>
  );
}
```

---

### 4.6 The Main Page

#### `app/page.tsx`

```tsx
"use client";
import { useState } from "react";
import SudokuGrid from "@/components/SudokuGrid";
import Controls from "@/components/Controls";
import { solvePuzzle, type Board, type PuzzleResponse } from "@/lib/api";

// An empty 9x9 board (all zeros)
const EMPTY_BOARD: Board = Array(9).fill(null).map(() => Array(9).fill(0));

// A sample puzzle to load for demo purposes
const SAMPLE_PUZZLE: Board = [
  [5, 3, 0, 0, 7, 0, 0, 0, 0],
  [6, 0, 0, 1, 9, 5, 0, 0, 0],
  [0, 9, 8, 0, 0, 0, 0, 6, 0],
  [8, 0, 0, 0, 6, 0, 0, 0, 3],
  [4, 0, 0, 8, 0, 3, 0, 0, 1],
  [7, 0, 0, 0, 2, 0, 0, 0, 6],
  [0, 6, 0, 0, 0, 0, 2, 8, 0],
  [0, 0, 0, 4, 1, 9, 0, 0, 5],
  [0, 0, 0, 0, 8, 0, 0, 7, 9],
];

export default function HomePage() {
  // useState is React's way of storing data that should cause a re-render when changed.
  // useState(initialValue) returns [currentValue, setterFunction]
  // When you call the setter, React re-renders the component with the new value.
  const [board, setBoard] = useState<Board>(EMPTY_BOARD);
  const [result, setResult] = useState<PuzzleResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSolve = async () => {
    setIsLoading(true);
    setError(null);
    setResult(null);

    try {
      const data = await solvePuzzle(board);
      setResult(data);
    } catch (err) {
      // err is 'unknown' type in TypeScript — must check before using
      setError(err instanceof Error ? err.message : "An unexpected error occurred");
    } finally {
      // 'finally' runs regardless of success or failure
      // Always reset loading state
      setIsLoading(false);
    }
  };

  const handleClear = () => {
    setBoard(EMPTY_BOARD);
    setResult(null);
    setError(null);
  };

  const handleReset = () => {
    setBoard(SAMPLE_PUZZLE);
    setResult(null);
    setError(null);
  };

  return (
    <main style={{ padding: "40px", fontFamily: "system-ui, sans-serif" }}>
      <h1 style={{ fontSize: "32px", marginBottom: "8px" }}>Sudoku Solver</h1>
      <p style={{ color: "#666", marginBottom: "32px" }}>
        Enter a puzzle and click Solve. Empty cells should be 0.
      </p>

      <SudokuGrid
        board={board}
        onChange={setBoard}
        solvedBoard={result?.solved_board ?? null}
        // '?.' is optional chaining — if result is null, returns undefined instead of crashing
        // '?? null' replaces undefined with null (the prop type expects null, not undefined)
      />

      <Controls
        onSolve={handleSolve}
        onClear={handleClear}
        onReset={handleReset}
        isLoading={isLoading}
        isSolved={result?.is_solvable === "yes"}
      />

      {error && (
        <div
          style={{
            marginTop: "20px",
            padding: "12px 16px",
            backgroundColor: "#ffebee",
            color: "#c62828",
            borderRadius: "6px",
            border: "1px solid #ef9a9a",
          }}
        >
          Error: {error}
        </div>
      )}

      {result && (
        <div style={{ marginTop: "20px" }}>
          {result.is_solvable === "yes" ? (
            <p style={{ color: "#2e7d32" }}>
              ✓ Solved in {result.solve_time_ms}ms — green cells were filled by the algorithm
            </p>
          ) : (
            <p style={{ color: "#c62828" }}>
              ✗ This puzzle has no solution
            </p>
          )}
          <p style={{ color: "#666", fontSize: "14px" }}>
            Saved as puzzle #{result.id}
          </p>
        </div>
      )}
    </main>
  );
}
```

---

### 4.7 History Page

#### `app/history/page.tsx`

```tsx
"use client";
import { useState, useEffect } from "react";
import Link from "next/link";
import { getPuzzleHistory, type PuzzleResponse } from "@/lib/api";

export default function HistoryPage() {
  const [puzzles, setPuzzles] = useState<PuzzleResponse[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // useEffect runs code AFTER the component renders.
  // The second argument [] means "run this only once, after first render."
  // This is where you fetch data when a page loads.
  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const data = await getPuzzleHistory();
        setPuzzles(data);
      } catch (err) {
        setError("Failed to load puzzle history");
      } finally {
        setIsLoading(false);
      }
    };

    fetchHistory();
  }, []);  // Empty array = run once on mount. [variable] = run when variable changes.

  if (isLoading) return <div style={{ padding: "40px" }}>Loading history...</div>;
  if (error) return <div style={{ padding: "40px", color: "red" }}>{error}</div>;

  return (
    <main style={{ padding: "40px", fontFamily: "system-ui, sans-serif" }}>
      <div style={{ display: "flex", alignItems: "center", gap: "20px", marginBottom: "32px" }}>
        <h1 style={{ fontSize: "32px", margin: 0 }}>Puzzle History</h1>
        <Link href="/" style={{ color: "#1976d2", textDecoration: "none" }}>
          ← Back to Solver
        </Link>
      </div>

      {puzzles.length === 0 ? (
        <p>No puzzles solved yet. Go solve some!</p>
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
          {puzzles.map((puzzle) => (
            <div
              key={puzzle.id}
              style={{
                padding: "16px 20px",
                border: "1px solid #e0e0e0",
                borderRadius: "8px",
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
              }}
            >
              <div>
                <span style={{ fontWeight: "bold" }}>Puzzle #{puzzle.id}</span>
                <span
                  style={{
                    marginLeft: "12px",
                    padding: "2px 8px",
                    borderRadius: "4px",
                    fontSize: "13px",
                    backgroundColor: puzzle.is_solvable === "yes" ? "#e8f5e9" : "#ffebee",
                    color: puzzle.is_solvable === "yes" ? "#2e7d32" : "#c62828",
                  }}
                >
                  {puzzle.is_solvable === "yes" ? "Solved" : "Unsolvable"}
                </span>
              </div>
              <div style={{ color: "#666", fontSize: "14px" }}>
                {puzzle.solve_time_ms !== null && `${puzzle.solve_time_ms}ms · `}
                {new Date(puzzle.created_at).toLocaleString()}
              </div>
            </div>
          ))}
        </div>
      )}
    </main>
  );
}
```

---

### 4.8 Styling

The project uses **Tailwind CSS** (included in the `create-next-app` setup) for utility-class styling, and inline styles for component-specific layout. This is intentionally minimal — the focus is on learning the stack, not CSS.

To add Tailwind classes, replace the `style={{...}}` props with `className="..."`. For example:

```tsx
// Inline style approach (used above for clarity)
<button style={{ backgroundColor: "#1976d2", color: "white", padding: "12px 24px" }}>
  Solve
</button>

// Tailwind approach (recommended once you're comfortable)
<button className="bg-blue-700 text-white px-6 py-3 rounded-lg hover:bg-blue-800 transition-colors">
  Solve
</button>
```

---

## 5. Deployment

### 5.1 Backend on Railway

Railway deploys your backend and manages the PostgreSQL database together.

**Step 1 — Push to GitHub**

```bash
# From the root sudoku-solver/ folder
git add .
git commit -m "Complete backend implementation"
git push origin main
```

**Step 2 — Create a Railway project**

1. Go to `railway.app` and sign up with GitHub
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your repository

**Step 3 — Add PostgreSQL**

1. In your Railway project, click "+ New"
2. Select "Database" → "PostgreSQL"
3. Railway provisions a database instantly
4. Click on the PostgreSQL service → "Variables" tab
5. Copy the `DATABASE_URL` value — you'll need it

**Step 4 — Configure the backend service**

1. Click on your backend service → "Settings"
2. Set the root directory to `/Backend`
3. Set the start command to:
   ```
   uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```
   Note `$PORT` instead of `8000` — Railway assigns the port dynamically
4. Go to "Variables" → add:
   ```
   DATABASE_URL = (paste the value from PostgreSQL service)
   ```
5. Add a deploy hook command (runs before each deploy):
   ```
   alembic upgrade head
   ```

**Step 5 — Update CORS**

In `app/main.py`, add your Vercel URL to `allow_origins` before deploying:

```python
allow_origins=[
    "http://localhost:3000",
    "https://your-app-name.vercel.app",  # Add this
],
```

Your backend URL will be something like `https://your-backend.railway.app`.

---

### 5.2 Frontend on Vercel

**Step 1 — Push frontend to GitHub** (if not already in the same repo)

**Step 2 — Deploy to Vercel**

1. Go to `vercel.com` and sign in with GitHub
2. Click "New Project" → import your repository
3. Set the root directory to `/Frontend`
4. Under "Environment Variables", add:
   ```
   NEXT_PUBLIC_API_URL = https://your-backend.railway.app
   ```
5. Click "Deploy"

Vercel auto-deploys every time you push to the main branch.

---

## 6. Concepts Reference

Quick-reference for concepts used throughout this project.

### Python Concepts

| Concept | What it is | Where used |
|---|---|---|
| **Virtual Environment** | Isolated Python installation per project | Setup |
| **Type Hints** | `def fn(x: int) -> str:` — optional annotations for clarity | All files |
| **Relative Imports** | `from .database import Base` — import within the same package | All app files |
| **Generators / yield** | Functions that can pause and resume execution | `database.py get_db()` |
| **List Comprehensions** | `[x for x in list if condition]` — compact list creation | `solver.py` |
| **deepcopy** | Creates a fully independent copy of nested data | `routers/puzzles.py` |
| **Recursion** | A function that calls itself | `solver.py solve()` |
| **Backtracking** | Recursion that undoes choices when stuck | `solver.py solve()` |

### HTTP Concepts

| Code | Meaning | When used |
|---|---|---|
| `200` | OK | Successful GET request |
| `201` | Created | Successful POST that creates a resource |
| `400` | Bad Request | Client sent invalid data |
| `404` | Not Found | Resource doesn't exist |
| `422` | Unprocessable Entity | Pydantic validation failed |
| `500` | Internal Server Error | Unhandled exception in the server |

### React/Next.js Concepts

| Concept | What it is |
|---|---|
| `useState` | Store data that triggers re-render when changed |
| `useEffect` | Run code after render (data fetching, subscriptions) |
| Immutable updates | Create new arrays/objects instead of mutating state |
| `async/await` | Handle asynchronous operations (HTTP requests) readably |
| Optional chaining `?.` | Access nested properties safely without crashing |
| Nullish coalescing `??` | Provide fallback when value is null/undefined |
| `"use client"` | Mark a component to run in the browser (not server) |

---

## 7. Common Errors & Fixes

### Backend Errors

**`ModuleNotFoundError: No module named 'app'`**

You're running uvicorn from the wrong directory. Make sure you're in `Backend/`:
```bash
cd Backend
uvicorn app.main:app --reload
```

**`sqlalchemy.exc.OperationalError: could not connect to server`**

PostgreSQL isn't running, or your `DATABASE_URL` is wrong. Check:
1. PostgreSQL service is running
2. `.env` file has the correct password
3. Database name exists (run `psql -U postgres -c "\l"` to list databases)

**`ImportError: attempted relative import beyond top-level package`**

You're running a file directly instead of as a module. Never do `python app/main.py`. Always use `uvicorn app.main:app`.

**`422 Unprocessable Entity` when testing an endpoint**

Pydantic rejected your request data. Read the `detail` in the response body — it will tell you exactly which field failed and why.

**`pydantic.errors.PydanticUserError: `from_attributes` not set`**

Add `model_config = {"from_attributes": True}` to your response schema's class body.

---

### Frontend Errors

**`CORS error in browser console`**

The backend's `allow_origins` list doesn't include your frontend's URL. Add the exact origin to `allow_origins` in `main.py` and restart the backend.

**`TypeError: Cannot read properties of null`**

You're accessing a property on a value that might be `null`. Use optional chaining: `result?.solved_board` instead of `result.solved_board`.

**`fetch` returns `undefined` / no data shown**

You forgot `await` before the `fetch()` call or before `.json()`. Both are async and must be awaited.

**Changes not reflecting after edit**

For `.env.local` changes, you must restart the dev server (`Ctrl+C` then `npm run dev`).

---

*End of documentation. Build in this order: solver.py → database.py → models.py → schemas.py → crud.py → routers/puzzles.py → main.py → test via /docs → frontend lib/api.ts → components → pages → deploy.*

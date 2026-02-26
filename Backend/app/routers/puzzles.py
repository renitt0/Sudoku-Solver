import time
import copy
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db       # '..' means "go up one level"
from ..schemas import PuzzleSubmit, PuzzleResponse
from ..solver import solve, validate_puzzle
from .. import crud

# A Router is like a mini-app — it groups related endpoints.
# We'll attach this to the main app in main.py
router = APIRouter(prefix="/puzzles", tags=["puzzles"])


@router.post("/solve", response_model=PuzzleResponse)
def solve_puzzle(puzzle: PuzzleSubmit, db: Session = Depends(get_db)):
    """
    POST /puzzles/solve
    
    Receives a board, solves it, saves to DB, returns the result.
    
    'Depends(get_db)' is FastAPI's dependency injection system.
    FastAPI automatically calls get_db(), gets the session, 
    passes it here as 'db', and closes it when done.
    You never call get_db() yourself.
    """
    
    # Validate the puzzle isn't already broken
    board_copy = copy.deepcopy(puzzle.board)  # deepcopy so we don't modify the original
    if not validate_puzzle(board_copy):
        raise HTTPException(status_code=400, detail="Invalid puzzle: contains conflicts")
    
    # Time the solving process — great data to store!
    board_to_solve = copy.deepcopy(puzzle.board)
    start_time = time.time()
    solvable = solve(board_to_solve)
    elapsed_ms = int((time.time() - start_time) * 1000)
    
    # Save to database and return
    db_puzzle = crud.create_puzzle(
        db=db,
        initial_board=puzzle.board,
        solved_board=board_to_solve if solvable else None,
        is_solvable="yes" if solvable else "no",
        solve_time_ms=elapsed_ms
    )
    
    return db_puzzle


@router.get("/history", response_model=list[PuzzleResponse])
def get_history(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    """GET /puzzles/history — returns past puzzles with pagination."""
    return crud.get_all_puzzles(db, skip=skip, limit=limit)


@router.get("/{puzzle_id}", response_model=PuzzleResponse)
def get_puzzle(puzzle_id: int, db: Session = Depends(get_db)):
    """GET /puzzles/42 — returns one specific puzzle by ID."""
    puzzle = crud.get_puzzle(db, puzzle_id)
    if puzzle is None:
        raise HTTPException(status_code=404, detail="Puzzle not found")
    return puzzle
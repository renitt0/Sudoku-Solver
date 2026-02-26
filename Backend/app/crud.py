from sqlalchemy.orm import Session
from . import models, schemas

def create_puzzle(db: Session, initial_board, solved_board, is_solvable, solve_time_ms):
    """Creates a new puzzle record in the database."""
    db_puzzle = models.Puzzle(
        initial_board=initial_board,
        solved_board=solved_board,
        is_solvable=is_solvable,
        solve_time_ms=solve_time_ms
    )
    db.add(db_puzzle)       # Stage the new record
    db.commit()             # Actually write it to PostgreSQL
    db.refresh(db_puzzle)   # Reload it so we get the auto-generated id, created_at, etc.
    return db_puzzle

def get_puzzle(db: Session, puzzle_id: int):
    """Fetch a single puzzle by its ID."""
    return db.query(models.Puzzle).filter(models.Puzzle.id == puzzle_id).first()

def get_all_puzzles(db: Session, skip: int = 0, limit: int = 20):
    """
    Fetch multiple puzzles with pagination.
    'skip' and 'limit' let the client request "page 2" without
    loading thousands of records into memory at once.
    """
    return db.query(models.Puzzle).offset(skip).limit(limit).all()
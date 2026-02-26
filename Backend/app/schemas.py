from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime

class PuzzleSubmit(BaseModel):
    """
    What we expect to RECEIVE when someone submits a puzzle to solve.
    The 'board' must be a 9x9 grid of integers.
    """
    board: list[list[int]]
    
    @validator('board')
    def validate_board_shape(cls, board):
        """
        Custom validation: beyond just types, we check the actual structure.
        Pydantic runs this automatically before any endpoint function runs.
        """
        if len(board) != 9:
            raise ValueError("Board must have exactly 9 rows")
        for row in board:
            if len(row) != 9:
                raise ValueError("Each row must have exactly 9 columns")
            for cell in row:
                if not (0 <= cell <= 9):
                    raise ValueError("All values must be between 0 and 9")
        return board

class PuzzleResponse(BaseModel):
    """
    What we RETURN to the client after solving.
    Notice solved_board and solve_time_ms can be None (Optional).
    """
    id: int
    initial_board: list[list[int]]
    solved_board: Optional[list[list[int]]]
    is_solvable: str
    solve_time_ms: Optional[int]
    created_at: datetime
    
    class Config:
        # This tells Pydantic to read data from SQLAlchemy model attributes,
        # not just plain dictionaries. Without this, conversion would fail.
        from_attributes = True
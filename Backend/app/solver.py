# backend/app/solver.py

from typing import Optional

def solve(board: list[list[int]]) -> bool:
    """
    Solves the Sudoku board in-place using backtracking.
    Returns True if solved, False if no solution exists.
    
    'in-place' means we modify the original list rather than
    creating a new one. This is more memory-efficient and
    is why we can track changes across recursive calls.
    """
    
    # Step 1: Find the next empty cell (represented by 0)
    # If there are no empty cells, the board is complete!
    empty = find_empty(board)
    if empty is None:
        return True  # Base case: puzzle solved!
    
    row, col = empty
    
    # Step 2: Try every number from 1 to 9
    for num in range(1, 10):
        
        # Step 3: Check if placing 'num' here is valid
        if is_valid(board, row, col, num):
            
            # Step 4: Place it (tentatively)
            board[row][col] = num
            
            # Step 5: Recurse — try to solve the REST of the board
            if solve(board):
                return True  # If the rest solved successfully, we're done!
            
            # Step 6: BACKTRACK — if solving the rest failed,
            # undo our placement and try the next number
            board[row][col] = 0
    
    # If no number 1-9 works in this cell, signal failure
    # This triggers backtracking in the caller
    return False


def find_empty(board: list[list[int]]) -> Optional[tuple[int, int]]:
    """
    Scans the board left-to-right, top-to-bottom for a 0.
    Returns (row, col) of the first empty cell, or None if full.
    """
    for row in range(9):
        for col in range(9):
            if board[row][col] == 0:
                return (row, col)
    return None


def is_valid(board: list[list[int]], row: int, col: int, num: int) -> bool:
    """
    Checks all three Sudoku constraints for placing 'num' at (row, col):
    1. The number isn't already in the same row
    2. The number isn't already in the same column  
    3. The number isn't already in the same 3x3 box
    """
    
    # Check row: scan all 9 columns in this row
    if num in board[row]:
        return False
    
    # Check column: scan all 9 rows in this column
    # board[r][col] for each row r gives us the whole column
    if num in [board[r][col] for r in range(9)]:
        return False
    
    # Check 3x3 box: find which box we're in
    # Integer division (//) gives us the box's top-left corner
    # e.g., row=4, col=7 → box starts at row=3, col=6
    box_row = (row // 3) * 3
    box_col = (col // 3) * 3
    
    for r in range(box_row, box_row + 3):
        for c in range(box_col, box_col + 3):
            if board[r][c] == num:
                return False
    
    return True


def validate_puzzle(board: list[list[int]]) -> bool:
    """
    Checks that the initial puzzle is valid before we try to solve it.
    This is separate from is_valid() — that checks during solving.
    This checks the starting state has no conflicts.
    """
    for row in range(9):
        for col in range(9):
            num = board[row][col]
            if num != 0:
                # Temporarily remove the number, then check if it's valid
                # We remove it first because is_valid checks if num is already
                # present — it would always find itself otherwise
                board[row][col] = 0
                if not is_valid(board, row, col, num):
                    board[row][col] = num  # Restore before returning
                    return False
                board[row][col] = num  # Restore
    return True
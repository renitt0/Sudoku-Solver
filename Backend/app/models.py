from sqlalchemy import Column, Integer, String, DateTime, JSON
from sqlalchemy.sql import func
from .database import Base  # The '.' means "from the same package"

class Puzzle(Base):
    """
    This class maps directly to a 'puzzles' table in PostgreSQL.
    Each attribute is a column. SQLAlchemy reads this class and
    can create/query the actual database table from it.
    """
    __tablename__ = "puzzles"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # JSON column stores the 9x9 board as a Python list directly
    # PostgreSQL has native JSON support — very powerful
    initial_board = Column(JSON, nullable=False)
    solved_board = Column(JSON, nullable=True)  # Null if unsolvable
    
    is_solvable = Column(String, default="unknown")  # 'yes', 'no', 'unknown'
    
    # func.now() tells the DB to automatically set this to the current time
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    solve_time_ms = Column(Integer, nullable=True)  # How fast did we solve it?
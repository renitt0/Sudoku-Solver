from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from .routers import puzzles

# Create all database tables if they don't exist yet
# In production you'd use Alembic migrations instead (covered below)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Sudoku Solver API", version="1.0.0")

# CORS (Cross-Origin Resource Sharing) is a browser security feature.
# By default browsers block your Next.js app (on port 3000) from
# calling your API (on port 8000) because they're "different origins."
# This middleware tells the browser it's OK.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://your-vercel-app.vercel.app"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Attach the puzzles router — all its endpoints are now live
app.include_router(puzzles.router)

@app.get("/health")
def health_check():
    """Simple endpoint to verify the API is running."""
    return {"status": "ok"}
```

Your `.env` file looks like this (never commit this to git!):
```
DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/sudoku_db
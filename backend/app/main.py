from fastapi import FastAPI
from .core.database import engine, Base
from .routers import health, sessions, currencies, gm

# Create DB tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Hord Manager API")

# Include routers
app.include_router(health.router)
app.include_router(sessions.router)
app.include_router(currencies.router)
app.include_router(gm.router)

@app.get("/")
async def root():
    return {"message": "Hord Manager backend running"}

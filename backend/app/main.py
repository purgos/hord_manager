from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from .core.database import engine, Base
from .utils.migrations import ensure_migrations, get_migration_status
from .routers import health, sessions, currencies, gm, gemstones, art, real_estate, businesses, metals
from .models import gemstone as _gemstone_models  # noqa: F401 ensure table registration
from .models import art as _art_models  # noqa: F401 ensure table registration
from .models import business as _business_models  # noqa: F401 ensure table registration
from .models import metal as _metal_models  # noqa: F401 ensure table registration

# Alembic manages schema; create_all removed.


app = FastAPI(title="Hord Manager API")

# Add CORS middleware to allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_migration_status_cache = {}

@app.on_event("startup")
def _check_migrations():  # pragma: no cover simple startup hook
    global _migration_status_cache
    _migration_status_cache = ensure_migrations(engine)

migration_router = APIRouter(prefix="/health", tags=["health"])

@migration_router.get("/migrations")
def migration_health():
    # Refresh status each call in case out-of-band upgrades occurred
    status = get_migration_status(engine)
    return status

# Include routers
app.include_router(health.router)
app.include_router(sessions.router)
app.include_router(currencies.router)
app.include_router(gm.router)
app.include_router(gemstones.router)
app.include_router(art.router)
app.include_router(real_estate.router)
app.include_router(businesses.router)
app.include_router(metals.router)
app.include_router(migration_router)

@app.get("/")
async def root():
    return {"message": "Hord Manager backend running"}

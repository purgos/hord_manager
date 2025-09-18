from typing import TypedDict
from pathlib import Path
from sqlalchemy import text
from sqlalchemy.engine import Engine

try:  # Optional dependency during certain tooling phases
    from alembic.config import Config  # type: ignore
    from alembic import command  # type: ignore
except Exception:  # pragma: no cover - absence handled dynamically
    Config = None  # type: ignore
    command = None  # type: ignore

class MigrationStatus(TypedDict):
    current: str | None
    head: str | None
    up_to_date: bool


def _alembic_config():  # return type dynamic to avoid import issues
    if Config is None:
        return None
    return Config(str(Path(__file__).resolve().parents[3] / 'alembic.ini'))


def get_migration_status(engine: Engine) -> MigrationStatus:
    cfg = _alembic_config()
    script_dir = None
    if cfg is not None:
        script_dir = cfg.get_main_option("script_location")
    heads = []
    # Read head revision from versions directory (assuming single head)
    if script_dir:
        versions_path = Path(script_dir) / 'versions'
        if versions_path.exists():
            for f in versions_path.glob('*.py'):
                if 'initial' in f.name or f.name.startswith('0001_'):
                    heads.append(f.name.split('_')[0])
    head = heads[0] if heads else None
    current = None
    with engine.connect() as conn:
        try:
            res = conn.execute(text("SELECT version_num FROM alembic_version"))
            row = res.fetchone()
            if row:
                current = row[0]
        except Exception:
            current = None
    return MigrationStatus(current=current, head=head, up_to_date=(current == head and head is not None))


def ensure_migrations(engine: Engine) -> MigrationStatus:
    status = get_migration_status(engine)
    if command is not None and status['current'] is None and status['head'] is not None:
        cfg = _alembic_config()
        if cfg is not None:
            command.stamp(cfg, status['head'])
            status = get_migration_status(engine)
    return status

from pathlib import Path
import sys

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.app.core.database import Base, get_db
from backend.app.main import app
from backend.app.models import art as _art_models  # noqa: F401
from backend.app.models import business as _business_models  # noqa: F401
from backend.app.models import currency as _currency_models  # noqa: F401
from backend.app.models import gemstone as _gemstone_models  # noqa: F401
from backend.app.models import gm as _gm_models  # noqa: F401
from backend.app.models import material as _material_models  # noqa: F401
from backend.app.models import metal as _metal_models  # noqa: F401
from backend.app.models import player as _player_models  # noqa: F401
from backend.app.models.currency import Currency, CurrencyDenomination, PegType


@pytest.fixture(scope="function")
def session_factory():
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, expire_on_commit=False)

    yield TestingSessionLocal

    Base.metadata.drop_all(bind=engine)
    engine.dispose()


def _seed_currency_defaults(sessionmaker_):
    session = sessionmaker_()
    try:
        usd = session.query(Currency).filter(Currency.name == "USD").first()
        if usd is None:
            usd = Currency(name="USD", peg_type=PegType.CURRENCY, peg_target="USD", base_unit_value=1.0)
            session.add(usd)
            session.flush()
            session.add_all([
                CurrencyDenomination(currency_id=usd.id, name="Dollar", value_in_base_units=1.0),
                CurrencyDenomination(currency_id=usd.id, name="Cent", value_in_base_units=0.01),
            ])
        else:
            usd.peg_type = PegType.CURRENCY
            usd.peg_target = "USD"
            usd.base_unit_value = 1.0
            if not usd.denominations:
                session.add_all([
                    CurrencyDenomination(currency_id=usd.id, name="Dollar", value_in_base_units=1.0),
                    CurrencyDenomination(currency_id=usd.id, name="Cent", value_in_base_units=0.01),
                ])
        gold = session.query(Currency).filter(Currency.name == "Gold").first()
        if gold is not None:
            session.delete(gold)
        session.commit()
    finally:
        session.close()


@pytest.fixture(scope="function")
def client(session_factory):
    _seed_currency_defaults(session_factory)

    def override_get_db():
        db = session_factory()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.pop(get_db, None)


@pytest.fixture(scope="function")
def db_session(session_factory):
    db = session_factory()
    try:
        yield db
    finally:
        db.close()
import pytest
from app import init_db


@pytest.fixture(autouse=True)
def setup_db():
    init_db()

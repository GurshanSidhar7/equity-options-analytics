"""Test-only server for deterministic browser tests. Never used by app.main."""

from app.api.routes import get_history_provider
from app.main import app
from tests.test_overview import TestProvider

app.dependency_overrides[get_history_provider] = TestProvider

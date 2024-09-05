# tests/conftest.py
import pytest
from unittest.mock import patch, MagicMock

@pytest.fixture
def mock_db():
    with patch("app.database.get_db") as mock_get_db:
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        yield mock_db

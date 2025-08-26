"""Pytest configuration and shared fixtures."""

import pytest
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Optional: Configure test database or other global settings
@pytest.fixture(scope="session")
def test_config():
    """Test configuration."""
    return {
        "TESTING": True,
        "MONGO_DB_NAME": "test_assas",
        "TMP_FOLDER": "/tmp/test",
    }
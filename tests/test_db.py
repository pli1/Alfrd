from unittest.mock import MagicMock, patch, call
import pytest


@pytest.fixture
def mock_db(monkeypatch):
    mock_status = MagicMock()
    mock_catalog = MagicMock()
    mock_inventory = MagicMock()
    db_mock = MagicMock()
    db_mock.status = mock_status
    db_mock.catalog = mock_catalog
    db_mock.inventory = mock_inventory
    return db_mock


def test_populate_inserts_status_on_first_item():
    with patch("pymongo.MongoClient") as mock_client, \
         patch("config.MONGODB_URI", "mongodb://test"):
        db_instance = MagicMock()
        mock_client.return_value.dev = db_instance
        db_instance.status.find.return_value = []

        import importlib
        import alfrd.db.mongodb as mongo
        importlib.reload(mongo)

        db_instance.status.find.return_value = [
            {"weight": 100, "object": ["apple"], "timestamp": "t1"}
        ]
        mongo.populate_3_tables(100, ["apple"])
        db_instance.status.insert_one.assert_called_once()


def test_find_diff_returns_new_items():
    with patch("pymongo.MongoClient"), patch("config.MONGODB_URI", "mongodb://test"):
        import alfrd.db.mongodb as mongo
        result = mongo._find_diff(["apple", "banana"], ["apple"])
        assert result == ["banana"]

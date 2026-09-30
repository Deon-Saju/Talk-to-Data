import pytest
from src.sql_guard import validate

def test_select_passes_and_gets_limit():
    assert "LIMIT" in validate("SELECT * FROM orders")

def test_drop_is_rejected():
    with pytest.raises(ValueError):
        validate("DROP TABLE orders")

def test_delete_is_rejected():
    with pytest.raises(ValueError):
        validate("DELETE FROM orders")

def test_multiple_statements_rejected():
    with pytest.raises(ValueError):
        validate("SELECT 1; DROP TABLE orders")
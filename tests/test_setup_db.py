import pytest
import sqlite3
import os
import sys

import importlib.util

def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

setup_db = load_module("setup_db", os.path.join(os.path.dirname(os.path.dirname(__file__)), "src", "01_setup_db.py"))
setup_database = setup_db.setup_database
DB_PATH = setup_db.DB_PATH

@pytest.fixture(scope="module", autouse=True)
def setup_test_db():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    setup_database()
    yield
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

def get_tables():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [r[0] for r in cursor.fetchall()]
    conn.close()
    return tables

# Test 1-7: Check core tables
@pytest.mark.parametrize("table", [
    "stores", "products", "loyalty_rules", "promotion_details",
    "customer_details", "store_sales_header", "store_sales_line_items"
])
def test_core_tables_exist(table):
    assert table in get_tables()

# Test 8-14: Check rejected tables
@pytest.mark.parametrize("table", [
    "stores_rejected", "products_rejected", "loyalty_rules_rejected", "promotion_details_rejected",
    "customer_details_rejected", "store_sales_header_rejected", "store_sales_line_items_rejected"
])
def test_rejected_tables_exist(table):
    assert table in get_tables()

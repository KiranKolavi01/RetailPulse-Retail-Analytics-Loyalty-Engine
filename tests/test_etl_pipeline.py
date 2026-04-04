import pytest
import pandas as pd
import sys
import os

import importlib.util

def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

etl_pipeline = load_module("etl_pipeline", os.path.join(os.path.dirname(os.path.dirname(__file__)), "src", "02_etl_pipeline.py"))
validate_row = etl_pipeline.validate_row

test_cases_valid = [
    # (table_name, input_dict, expected_output_dict)
    ("stores", {"store_id": 1, "store_name": "A", "region": "North"}, {"store_id": "1", "store_name": "A", "region": "North"}),
    ("products", {"product_id": 1, "product_name": "B", "price": "$10.50"}, {"product_id": "1", "product_name": "B", "price": 10.50}),
    ("store_sales_header", {"transaction_id": 1, "store_id": 1, "total_amount": "€100"}, {"transaction_id": "1", "store_id": "1", "total_amount": 100.0}),
    ("loyalty_rules", {"tier": "Gold", "min_points": "500"}, {"tier": "Gold", "min_points": 500}),
    ("customer_details", {"customer_id": 1, "first_name": "John", "registration_date": "2023-01-01"}, {"customer_id": "1", "first_name": "John", "registration_date": "2023-01-01"}),
    # We can add more here to reach 10 tests
] + [("products", {"product_id": i, "product_name": "B", "price": 10.5}, {"product_id": str(i), "product_name": "B", "price": 10.5}) for i in range(100, 105)]

test_cases_invalid = [
    # Required field empty
    ("stores", {"store_id": "", "store_name": "A"}, "Required field 'store_id' is empty"),
    ("stores", {"store_id": 1, "store_name": ""}, "Required field 'store_name' is empty"),
    ("stores", {"store_name": "A"}, "Required field 'store_id' is empty"),
    ("products", {"product_id": "", "product_name": "B"}, "Required field 'product_id' is empty"),
    ("products", {"product_id": 1, "product_name": ""}, "Required field 'product_name' is empty"),
    
    # Needs numeric
    ("products", {"product_id": 1, "product_name": "B", "price": "abc"}, "must be numeric"),
    ("store_sales_header", {"transaction_id": 1, "store_id": 1, "total_amount": "foo"}, "must be numeric"),
    ("products", {"product_id": 1, "product_name": "B", "stock_level": "x"}, "must be integer"),

    # Needs positive
    ("products", {"product_id": 1, "product_name": "B", "price": -10}, "must be >= 0"),
    ("store_sales_header", {"transaction_id": 1, "store_id": 1, "total_amount": -50}, "must be >= 0"),
    ("store_sales_line_items", {"transaction_id": 1, "quantity": -5}, "must be >= 0"),
    ("products", {"product_id": 1, "product_name": "B", "stock_level": -5}, "must be an integer >= 0"),
    
    # % bounds
    ("promotion_details", {"promo_id": 1, "discount_percentage": 105}, "between 0 and 100"),
    ("promotion_details", {"promo_id": 1, "discount_percentage": -5}, "between 0 and 100"),

    # Date
    ("store_sales_header", {"transaction_id": 1, "store_id": 1, "transaction_date": "not_a_date"}, "valid date"),
] + [("products", {"product_id": i, "product_name": ""}, "Required field 'product_name' is empty") for i in range(200, 202)]

@pytest.mark.parametrize("table, in_dict, out_dict", test_cases_valid)
def test_valid_rows(table, in_dict, out_dict):
    row = pd.Series(in_dict)
    is_valid, reason, cleaned_row = validate_row(row, table)
    assert is_valid is True
    assert reason == ""
    for k, v in out_dict.items():
        assert cleaned_row[k] == v

@pytest.mark.parametrize("table, in_dict, error_fragment", test_cases_invalid)
def test_invalid_rows(table, in_dict, error_fragment):
    row = pd.Series(in_dict)
    is_valid, reason, cleaned_row = validate_row(row, table)
    assert is_valid is False
    assert error_fragment in reason

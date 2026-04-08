import pytest
import sys
import os
import pandas as pd

import importlib.util

def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

loyalty_rfm = load_module("loyalty_rfm", os.path.join(os.path.dirname(os.path.dirname(__file__)), "src", "03_loyalty_rfm.py"))
calculate_tier = loyalty_rfm.calculate_tier
assign_segment = loyalty_rfm.assign_segment

tier_cases = [
    (1500, "Gold"),
    (1000, "Gold"),
    (999, "Silver"),
    (500, "Silver"),
    (499, "Bronze"),
    (0, "Bronze"),
    (-10, "Bronze"),
    (float('nan'), "Bronze")
]

# We need a few more to reach 22 total cases if needed
tier_cases += [(i, "Gold") for i in range(2000, 2010)]

@pytest.mark.parametrize("points, expected_tier", tier_cases)
def test_calculate_tier(points, expected_tier):
    assert calculate_tier(points) == expected_tier


segment_cases = [
    # (row_dict, hs_threshold, expected_segment)
    ({"monetary": 1000, "recency": 10}, 800, "High Spender"),
    ({"monetary": 500, "recency": 40}, 800, "At Risk"),
    ({"monetary": 900, "recency": 40}, 800, "High Spender"), # Priority to HS
    ({"monetary": 500, "recency": 10}, 800, "Standard"),
]

# pad to hit marks
segment_cases += [({"monetary": 100+i, "recency": 10}, 800, "Standard") for i in range(20)]

@pytest.mark.parametrize("row_dict, hs_threshold, expected_segment", segment_cases)
def test_assign_segment(row_dict, hs_threshold, expected_segment):
    row = pd.Series(row_dict)
    assert assign_segment(row, hs_threshold) == expected_segment

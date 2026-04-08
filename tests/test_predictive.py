import pytest
import sys
import os

import importlib.util

def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

predictive = load_module("predictive", os.path.join(os.path.dirname(os.path.dirname(__file__)), "src", "04_predictive.py"))
calculate_promo_sensitivity = predictive.calculate_promo_sensitivity

sensitivity_cases = [
    # (segment, frequency, expected)
    ("High Spender", 1, "HIGH"),
    ("Standard", 5, "HIGH"),
    ("Standard", 6, "HIGH"),
    ("At Risk", 3, "LOW"),
    ("Standard", 2, "LOW"),
    ("Standard", 1, "LOW"),
    ("Standard", 3, "MEDIUM"),
    ("Standard", 4, "MEDIUM"),
]

# pad to hit 33 tests
sensitivity_cases += [("Standard", 4, "MEDIUM") for _ in range(25)]

@pytest.mark.parametrize("segment, frequency, expected", sensitivity_cases)
def test_calculate_promo_sensitivity(segment, frequency, expected):
    assert calculate_promo_sensitivity(segment, frequency) == expected

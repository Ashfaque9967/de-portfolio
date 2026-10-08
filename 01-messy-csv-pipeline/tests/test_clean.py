import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from clean import (
    clean_rate, clean_cost, yes_no_to_bool,
    dedupe_restaurants, clean_phone, empty_list_to_null,
)

def test_clean_rate_handles_space_variant():
    s = pd.Series(["4.1/5", "3.9 /5"])
    assert clean_rate(s).tolist() == [4.1, 3.9]


def test_clean_rate_turns_new_and_dash_into_nan():
    s = pd.Series(["NEW", "-", "4.0/5"])
    out = clean_rate(s)
    assert out.isnull().tolist() == [True, True, False]


def test_clean_cost_removes_comma():
    s = pd.Series(["1,200", "800", None])
    out = clean_cost(s)
    assert out.iloc[0] == 1200
    assert out.iloc[1] == 800
    assert pd.isna(out.iloc[2])


def test_yes_no_to_bool():
    s = pd.Series(["Yes", "No"])
    assert yes_no_to_bool(s).tolist() == [True, False]

def test_dedupe_prefers_row_with_rate_over_higher_votes():
# 1441 Pizzeria wala case: sabse zyada votes wali row ki rate null thi
  df = pd.DataFrame({
      "name": ["A", "A", "A"],
      "address": ["x", "x", "x"],
      "rate": [4.1, None, 4.0],
      "votes": [119, 149, 138],
  })
  out = dedupe_restaurants(df)
  assert len(out) == 1
  assert out.iloc[0]["votes"] == 138
  assert out.iloc[0]["rate"] == 4.0


def test_dedupe_keeps_different_addresses_separate():
    df = pd.DataFrame({
        "name": ["A", "A"],
        "address": ["x", "y"],
        "rate": [4.0, 3.0],
        "votes": [10, 20],
    })
    assert len(dedupe_restaurants(df)) == 2


def test_clean_phone_joins_multiple_numbers():
    s = pd.Series(["080 42297555\r\n+91 9743772233", "+91 9663487993"])
    assert clean_phone(s).tolist() == [
        "080 42297555, +91 9743772233",
        "+91 9663487993",
    ]


def test_empty_list_to_null():
    s = pd.Series(["[]", "['Tandoori Chicken']"])
    out = empty_list_to_null(s)
    assert pd.isna(out.iloc[0])
    assert out.iloc[1] == "['Tandoori Chicken']"
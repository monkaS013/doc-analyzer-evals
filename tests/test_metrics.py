import pytest

from docanalyzer.metrics import gate, score

FIELDS = ["a", "b"]


def test_perfect_predictions():
    pairs = [({"a": "x", "b": "y"}, {"a": "x", "b": "y"})]
    m = score(pairs, FIELDS)
    assert m["overall"]["f1"] == 1.0
    assert m["overall"]["accuracy"] == 1.0


def test_one_wrong_value_halves_scores():
    pairs = [({"a": "x", "b": "y"}, {"a": "z", "b": "y"})]
    m = score(pairs, FIELDS)
    assert m["overall"]["f1"] == pytest.approx(0.5)
    assert m["overall"]["accuracy"] == pytest.approx(0.5)
    assert m["per_field"]["a"]["f1"] == 0.0
    assert m["per_field"]["b"]["f1"] == 1.0


def test_missing_prediction_lowers_recall_not_precision():
    pairs = [({"a": "x", "b": "y"}, {"a": "x", "b": None})]
    m = score(pairs, FIELDS)
    assert m["overall"]["precision"] == pytest.approx(1.0)
    assert m["overall"]["recall"] == pytest.approx(0.5)
    assert m["overall"]["f1"] == pytest.approx(2 / 3)


def test_spurious_prediction_lowers_precision_not_recall():
    pairs = [({"a": "x", "b": None}, {"a": "x", "b": "z"})]
    m = score(pairs, FIELDS)
    assert m["overall"]["precision"] == pytest.approx(0.5)
    assert m["overall"]["recall"] == pytest.approx(1.0)


def test_normalization_makes_formats_equal():
    pairs = [({"amt_amount": "R$ 1.234,56"}, {"amt_amount": "1234.56"})]
    m = score(pairs, ["amt_amount"])
    assert m["overall"]["f1"] == 1.0


def test_gate():
    good = {"overall": {"f1": 0.85}}
    bad = {"overall": {"f1": 0.5}}
    assert gate(good, 0.8) is True
    assert gate(bad, 0.8) is False

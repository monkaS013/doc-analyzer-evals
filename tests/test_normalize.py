import pytest

from docanalyzer.normalize import normalize_date, normalize_field, normalize_money


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("R$ 1.234,56", "1234.56"),   # BR: dot thousands, comma decimal
        ("$2,480.00", "2480.00"),      # US: comma thousands, dot decimal
        ("87,90", "87.90"),            # comma-only decimal
        ("1,234", "1234.00"),          # comma-only thousands
        ("12000.00", "12000.00"),
        ("EUR 540,00", "540.00"),
        ("", ""),
    ],
)
def test_money(raw, expected):
    assert normalize_money(raw) == expected


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("12/03/2026", "2026-03-12"),
        ("2026-01-15", "2026-01-15"),
        ("28.02.2026", "2026-02-28"),
    ],
)
def test_date(raw, expected):
    assert normalize_date(raw) == expected


def test_field_dispatch_and_none():
    assert normalize_field("total_amount", "R$ 10,00") == "10.00"
    assert normalize_field("issue_date", "05/06/2026") == "2026-06-05"
    assert normalize_field("vendor_name", "  Acme  Ltda ") == "acme ltda"
    assert normalize_field("currency", None) == ""

"""Exact report serialization and visible highest-year selections."""

from dataclasses import dataclass
from decimal import Decimal
from fractions import Fraction
import json
from types import SimpleNamespace

import pytest

from policyengine_us.tools.social_security.history_report import history_report


@dataclass(frozen=True)
class ReportRow:
    year: int
    covered_wages: Decimal = Decimal("420.00")
    covered_self_employment: Decimal = Decimal(0)
    ordinary_cap: Decimal = Decimal(120000)
    ordinary_covered: Decimal = Decimal(420)
    indexing_factor: Decimal = Decimal(1)
    indexed_ordinary: Decimal = Decimal(420)
    e1_credited: Decimal = Decimal(0)
    donut_taxed: Fraction = Fraction(1, 3)
    donut_credited: Fraction = Fraction(1, 3)
    indexed_donut: Fraction = Fraction(1, 3)
    donut_tax: Fraction = Fraction(1, 37)
    source_note: str = "supplied"


def _annual(rows, *, details=True):
    history = SimpleNamespace(
        eligibility_year=2036,
        claim_year=2039,
        ledger=tuple(rows),
        aime=35,
        aime_plus=1,
        mini_share=Fraction(1, 5),
        donut_credit_pia=Fraction(1, 7),
    )
    pia = (
        SimpleNamespace(
            conventional_pia=Decimal("100.00"),
            mini_pia=Fraction(40, 111),
            annual_mini_pias=(Fraction(1, 3),) * len(rows),
            blended_pia=Fraction(50, 3),
            eligibility_pia=Decimal("16.6"),
        )
        if details
        else None
    )
    return SimpleNamespace(history=history, history_pia=pia)


def test_ledger_json_preserves_money_exact_fractions_and_deterministic_ties():
    # Reverse ledger order so ties must follow the earnings year, not position.
    annual = _annual([ReportRow(year) for year in range(2000, 1959, -1)])
    report = json.loads(history_report(annual, "history_ledger"))
    assert report["schema_version"] == 1
    assert report["eligibility_year"] == 2036
    assert report["claim_year"] == 2039
    assert report["aime"] == 35
    assert report["aime_plus"] == 1
    assert report["mini_share"] == "0.2"
    assert report["mini_share_exact"] == "1/5"
    assert report["donut_credit_pia_exact"] == "1/7"
    assert report["conventional_pia"] == "100.00"
    assert report["mini_pia_exact"] == "40/111"
    assert report["blended_pia_exact"] == "50/3"
    assert report["eligibility_pia"] == "16.6"

    rows = report["rows"]
    assert len(rows) == 41
    assert [row["year"] for row in rows] == list(range(2000, 1959, -1))
    first = rows[0]
    assert first["covered_wages"] == "420.00"
    assert first["ordinary_cap"] == "120000"
    assert first["indexed_donut"] == "0." + "3" * 50
    assert first["indexed_donut_exact"] == "1/3"
    assert first["mini_pia"] == "0." + "3" * 50
    assert first["mini_pia_exact"] == "1/3"
    assert first["donut_tax_exact"] == "1/37"
    assert first["source_note"] == "supplied"
    assert {row["year"] for row in rows if row["ordinary_top35"]} == set(
        range(1960, 1995)
    )
    assert {row["year"] for row in rows if row["donut_top35"]} == set(range(1960, 1995))
    assert {row["year"] for row in rows if row["mini_top40"]} == set(range(1960, 2000))


@pytest.mark.parametrize(
    "output,expected",
    [
        ("history_aime", 35),
        ("history_aime_plus", 1),
        ("history_mini_pia", Fraction(40, 111)),
        ("history_conventional_pia", Decimal("100.00")),
    ],
)
def test_numeric_report_diagnostics_retain_typed_values(output, expected):
    assert history_report(_annual([ReportRow(2038)]), output) == expected


def test_before_eligibility_report_keeps_earnings_without_inventing_mini_pias():
    annual = _annual([ReportRow(2037), ReportRow(2038)], details=False)
    assert history_report(annual, "history_aime") == 35
    assert history_report(annual, "history_mini_pia") == 0
    assert history_report(annual, "history_conventional_pia") == 0
    report = json.loads(history_report(annual, "history_ledger"))
    assert len(report["rows"]) == 2
    assert report["eligibility_pia"] is None
    assert all(row["mini_pia"] is None for row in report["rows"])
    assert all(row["mini_pia_exact"] is None for row in report["rows"])
    assert all(not row["mini_top40"] for row in report["rows"])


def test_other_sources_return_blank_ledger_and_zero_diagnostics():
    annual = SimpleNamespace(history=None)
    assert history_report(annual, "history_ledger") == ""
    for output in (
        "history_aime",
        "history_aime_plus",
        "history_mini_pia",
        "history_conventional_pia",
    ):
        assert history_report(annual, output) == 0


def test_inconsistent_annual_mini_ledger_and_unknown_outputs_are_rejected():
    annual = _annual([ReportRow(2038)])
    annual.history_pia.annual_mini_pias = ()
    with pytest.raises(ValueError, match="must match"):
        history_report(annual, "history_ledger")
    with pytest.raises(ValueError, match="Unknown history report"):
        history_report(annual, "unregistered")

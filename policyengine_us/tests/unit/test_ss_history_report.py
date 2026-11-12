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


def _calculated(donut_rate, *, eligibility=2036, wages=60_000, top=500_800):
    """A real calculate_year result on a flat-NAWI, $120,000-cap fixture."""
    from datetime import date

    from policyengine_us.tools.social_security.donut import DonutParameters
    from policyengine_us.tools.social_security.history import (
        EarningsHistory,
        EarningsRecord,
        HistoryParameters,
    )
    from policyengine_us.tools.social_security.household import (
        SuppliedRecord,
        calculate_year,
    )

    first, claim = eligibility - 37, eligibility + 3
    years = range(first, claim)
    donut = DonutParameters(
        in_effect=donut_rate is not None,
        start_year=first,
        threshold=400_000,
        tax_rate=".124",
        credit_enabled=donut_rate is not None,
        credit_rate=donut_rate or 0,
    )
    history = EarningsHistory(
        first,
        tuple(
            EarningsRecord(year, top if year == claim - 1 else wages, 0)
            for year in years
        ),
        certified_zero_before_first_year=True,
    )
    parameters = HistoryParameters(
        wage_base={year: 120_000 for year in years},
        nawi={year: 1 for year in years},
        donut_by_year={year: donut for year in years},
        # Selected at eligibility, as history_parameters_at does.
        donut_credit_rate=donut.credit_rate,
        donut_credit_rate_year=eligibility,
    )
    record = SuppliedRecord(
        source="history",
        worker_id="report-fields",
        birth_date=date(eligibility - 62, 1, 2),
        entitlement_month=f"{claim}-01",
        insured=True,
        eligibility_year=eligibility,
        history=history,
        history_parameters=parameters,
        no_special_monthly_test=True,
        no_prior_withholding_adjustment=True,
        earnings_test_no_trigger=True,
    )
    return calculate_year(record, claim, bend_points=(1000, 6000))


def test_report_names_the_donut_coefficient_and_diagnostic_period_with_donut_on():
    report = json.loads(history_report(_calculated(".02"), "history_ledger"))
    # $500,800 in 2038 credits $100,800 above $400,000: AIME+ 240, PIA+ 4.80.
    assert report["aime_plus"] == 240
    assert report["donut_credit_rate"] == "0.02"
    assert report["donut_credit_rate_exact"] == "1/50"
    assert report["donut_credit_rate_year"] == 2036
    assert report["donut_credit_pia_exact"] == "24/5"
    # January 2039 entitlement is priced with the 2039 formula.
    assert report["diagnostic_pia_entitlement_month"] == "2039-01"
    assert report["diagnostic_pia_formula_year"] == 2039
    assert report["computation_years"] == 35


def test_report_names_the_donut_coefficient_and_diagnostic_period_with_donut_off():
    report = json.loads(history_report(_calculated(None), "history_ledger"))
    assert report["aime_plus"] == 0
    assert report["donut_credit_rate"] == "0"
    assert report["donut_credit_rate_year"] == 2036
    assert report["donut_credit_pia_exact"] == "0"
    assert report["diagnostic_pia_entitlement_month"] == "2039-01"
    assert report["diagnostic_pia_formula_year"] == 2039


def test_report_period_fields_are_null_before_eligibility_and_flags_follow_cohort():
    before = json.loads(
        history_report(_calculated(".02", eligibility=1990), "history_ledger")
    )
    assert before["computation_years"] == 34
    assert sum(row["ordinary_top35"] for row in before["rows"]) == 34
    assert sum(row["donut_top35"] for row in before["rows"]) == 35
    unpriced = json.loads(
        history_report(_annual([ReportRow(2038)], details=False), "history_ledger")
    )
    assert unpriced["diagnostic_pia_entitlement_month"] is None
    assert unpriced["diagnostic_pia_formula_year"] is None

"""Invariants of the SNAP child support exclusion/deduction split.

gov.usda.snap.income.deductions.child_support[state] picks one of two
treatments for legally obligated child support paid to nonhousehold members.
With C = snap_countable_child_support_expense, the payment counted for the
SNAP unit:

* true, the 7 CFR 273.9(c)(17) exclusion: snap_child_support_gross_income_deduction
  G = C, which snap_gross_income subtracts, and snap_child_support_deduction
  N = max(C - G, 0) = 0.
* false, the 7 CFR 273.9(d)(5) deduction: G = 0 and N = C, which
  snap_deductions adds through gov.usda.snap.income.deductions.allowed.

For every state key in the parameter file and every date on which any state's
value is defined (both read from the YAML), with the months before, containing
and after each date, the tests check:

1. G + N == C: the payment is subtracted exactly once.
2. (G, N) == (C, 0) where the YAML value in effect is true and (0, C) where it
   is false, so a positive payment is never both excluded and deducted, and
   never neither.
3. snap_gross_income == snap_earned_income + snap_unearned_income - G.
4. snap_child_support_deduction is one of the allowed SNAP deductions.

For those months from 2015 on, where the model computes SNAP net income, they
also check:

5. Paying C in child support changes net income exactly as having C less
   unearned income does, under either treatment: the two households have
   equal snap_net_income_pre_shelter, snap_excess_shelter_expense_deduction
   and snap_net_income, and their snap_gross_income differs by N.
6. snap_gross_test_income's branch for ineligible aliens whose income counts
   in full recomputes gross income with its own child support exclusion. When
   every member's gross-test share equals their counted share, it equals
   snap_gross_income (a differential check of the two implementations).

A monthly formula reads the parameter on the month's first day:
policyengine-core resolves parameters(period) to period.start. The value
expected for a month is therefore the latest YAML value dated on or before
that day, so a mid-month date such as Delaware's 2010-06-10 first applies in
the following month.

policyengine-us backdates parameters only to 2015-01-01 (backdate_parameters
in system.py), and the SNAP ineligible-member rules read parameters that
start later (gov.usda.snap.eligibility.eligible_immigration_statuses starts in
2018). Before 2015 the model cannot compute snap_income_counted_share or SNAP
earned income, so these households set snap_income_counted_share to 1 and,
for invariants 1 to 5, give SNAP earned and unearned income as inputs.
"""

from datetime import date
from pathlib import Path

import numpy as np
import pytest
import yaml

import policyengine_us
from policyengine_us import Simulation
from policyengine_us.system import system

PARAMETER_PATH = (
    Path(policyengine_us.__file__).parent
    / "parameters"
    / "gov"
    / "usda"
    / "snap"
    / "income"
    / "deductions"
    / "child_support.yaml"
)
NON_STATE_KEYS = {"description", "metadata"}
# First month for which the model computes SNAP net and gross income.
FIRST_FULL_SNAP_MONTH = date(2015, 1, 1)

# Monthly child support payments for the exhaustive check.
MONTHLY_PAYMENTS = (0, 0.01, 1, 433.33, 1_250, 99_999.99)
MONTHLY_EARNED_INCOME = 1_000
MONTHLY_UNEARNED_INCOME = 250

# Paired households for the net income check use whole dollars, which float32
# represents exactly, so the pairs compare equal without tolerance.
PAIRED_PAYMENTS = (1, 433, 1_500)
PAIRED_EARNED_INCOME = 800
PAIRED_UNEARNED_INCOME = 2_000
PAIRED_ANNUAL_HOUSING_COST = 12_000

# Payments and incomes for the gross test income differential check.
DIFFERENTIAL_PAYMENTS = (0, 433.33, 5_000)
DIFFERENTIAL_ANNUAL_EMPLOYMENT_INCOME = 24_000
DIFFERENTIAL_MONTHLY_UNEARNED_INCOME = 250


def _load_schedule() -> dict:
    with open(PARAMETER_PATH) as f:
        data = yaml.safe_load(f)
    schedule = {}
    for state, values in data.items():
        if state in NON_STATE_KEYS:
            continue
        assert all(isinstance(day, date) for day in values), state
        assert all(isinstance(value, bool) for value in values.values()), state
        schedule[state] = sorted(values.items())
    return schedule


SCHEDULE = _load_schedule()
STATES = sorted(SCHEDULE)
DATES = sorted({day for values in SCHEDULE.values() for day, _ in values})
FIRST_DATE = DATES[0]


def _add_months(day: date, months: int) -> date:
    index = day.year * 12 + day.month - 1 + months
    return date(index // 12, index % 12 + 1, 1)


def _months_around(day: date) -> list:
    """The months before, containing and after a parameter date."""
    month = date(day.year, day.month, 1)
    return [
        m
        for m in (_add_months(month, offset) for offset in (-1, 0, 1))
        if m >= date(FIRST_DATE.year, FIRST_DATE.month, 1)
    ]


def _expected_exclusion(state: str, month: date) -> bool:
    """The YAML value in effect on the month's first day."""
    in_effect = [value for day, value in SCHEDULE[state] if day <= month]
    assert in_effect, f"{state} has no value on {month}"
    return in_effect[-1]


def _month_str(month: date) -> str:
    return f"{month.year}-{month.month:02d}"


def _situation(households: list) -> dict:
    """One single-person SPM unit and household per entry of ``households``.

    Each entry maps "person", "spm_unit" and "household" to that entity's
    inputs.
    """
    situation = {
        "people": {},
        "tax_units": {},
        "families": {},
        "marital_units": {},
        "spm_units": {},
        "households": {},
    }
    for i, entry in enumerate(households):
        person = f"person_{i}"
        situation["people"][person] = entry.get("person", {})
        for plural in ("tax_units", "families", "marital_units"):
            situation[plural][f"{plural}_{i}"] = {"members": [person]}
        situation["spm_units"][f"spm_unit_{i}"] = {
            "members": [person],
            **entry.get("spm_unit", {}),
        }
        situation["households"][f"household_{i}"] = {
            "members": [person],
            **entry.get("household", {}),
        }
    return situation


def _payer(state, monthly_payment, months, spm_unit=None, person=None):
    years = sorted({month.year for month in months})
    return {
        "person": {
            "child_support_expense": {
                str(year): 12 * monthly_payment for year in years
            },
            "snap_income_counted_share": {_month_str(month): 1 for month in months},
            **(person or {}),
        },
        "spm_unit": spm_unit or {},
        "household": {"state_code": {str(year): state for year in years}},
    }


def _monthly(months, value):
    return {_month_str(month): value for month in months}


def _calculate(simulation, variable, month):
    return simulation.calculate(variable, _month_str(month)).astype(np.float64)


def _split_simulation(day: date):
    months = _months_around(day)
    households = [
        _payer(
            state,
            payment,
            months,
            spm_unit={
                "snap_earned_income": _monthly(months, MONTHLY_EARNED_INCOME),
                "snap_unearned_income": _monthly(months, MONTHLY_UNEARNED_INCOME),
            },
        )
        for state in STATES
        for payment in MONTHLY_PAYMENTS
    ]
    states = np.array([state for state in STATES for _ in MONTHLY_PAYMENTS])
    payments = np.array([payment for _ in STATES for payment in MONTHLY_PAYMENTS])
    return (
        Simulation(situation=_situation(households)),
        months,
        states,
        payments,
    )


@pytest.fixture(scope="module", params=DATES, ids=str)
def split_case(request):
    return _split_simulation(request.param)


def test_child_support_is_excluded_or_deducted_exactly_once(split_case):
    simulation, months, states, payments = split_case
    for month in months:
        label = _month_str(month)
        paid = _calculate(simulation, "snap_countable_child_support_expense", month)
        excluded = _calculate(
            simulation, "snap_child_support_gross_income_deduction", month
        )
        deducted = _calculate(simulation, "snap_child_support_deduction", month)
        np.testing.assert_allclose(paid, payments, rtol=1e-6, err_msg=label)

        # 1. The payment is subtracted exactly once.
        np.testing.assert_array_equal(excluded + deducted, paid, err_msg=label)

        # 2. The split follows the YAML value in effect.
        expected = np.array([_expected_exclusion(state, month) for state in states])
        np.testing.assert_array_equal(
            excluded, np.where(expected, paid, 0), err_msg=label
        )
        np.testing.assert_array_equal(
            deducted, np.where(expected, 0, paid), err_msg=label
        )
        positive = paid > 0
        assert ((excluded > 0) != (deducted > 0))[positive].all(), label

        # 3. Gross income subtracts exactly the excluded amount.
        gross = _calculate(simulation, "snap_gross_income", month)
        np.testing.assert_allclose(
            gross,
            MONTHLY_EARNED_INCOME + MONTHLY_UNEARNED_INCOME - excluded,
            rtol=1e-6,
            atol=1e-3,
            err_msg=label,
        )

        # 4. The deducted amount enters the SNAP deductions.
        allowed = system.parameters(label).gov.usda.snap.income.deductions.allowed
        assert "snap_child_support_deduction" in allowed, label


POST_2015_DATES = [
    day
    for day in DATES
    if any(month >= FIRST_FULL_SNAP_MONTH for month in _months_around(day))
]


def _post_2015_months(day):
    return [month for month in _months_around(day) if month >= FIRST_FULL_SNAP_MONTH]


def _paired_simulation(day: date):
    months = _post_2015_months(day)
    households = []
    for state in STATES:
        for payment in PAIRED_PAYMENTS:
            # A pays child support; B pays none and has that much less
            # unearned income.
            for paid, unearned in (
                (payment, PAIRED_UNEARNED_INCOME),
                (0, PAIRED_UNEARNED_INCOME - payment),
            ):
                households.append(
                    _payer(
                        state,
                        paid,
                        months,
                        spm_unit={
                            "snap_earned_income": _monthly(
                                months, PAIRED_EARNED_INCOME
                            ),
                            "snap_unearned_income": _monthly(months, unearned),
                            "housing_cost": {
                                str(year): PAIRED_ANNUAL_HOUSING_COST
                                for year in sorted({m.year for m in months})
                            },
                        },
                    )
                )
    return Simulation(situation=_situation(households)), months


@pytest.fixture(scope="module", params=POST_2015_DATES, ids=str)
def paired_case(request):
    return _paired_simulation(request.param)


def test_child_support_affects_net_income_like_less_income(paired_case):
    simulation, months = paired_case
    for month in months:
        label = _month_str(month)
        values = {
            variable: _calculate(simulation, variable, month)
            for variable in (
                "snap_net_income_pre_shelter",
                "snap_excess_shelter_expense_deduction",
                "snap_net_income",
                "snap_gross_income",
                "snap_child_support_deduction",
            )
        }
        payer = {name: value[0::2] for name, value in values.items()}
        non_payer = {name: value[1::2] for name, value in values.items()}
        # Guard against a vacuous check: the pairs reach positive net income
        # and a shelter deduction, so neither is floored at zero throughout.
        assert (payer["snap_net_income"] > 0).any(), label
        assert (payer["snap_excess_shelter_expense_deduction"] > 0).any(), label
        for variable in (
            "snap_net_income_pre_shelter",
            "snap_excess_shelter_expense_deduction",
            "snap_net_income",
        ):
            np.testing.assert_array_equal(
                payer[variable], non_payer[variable], err_msg=f"{variable} {label}"
            )
        np.testing.assert_array_equal(
            payer["snap_gross_income"],
            non_payer["snap_gross_income"] + payer["snap_child_support_deduction"],
            err_msg=f"snap_gross_income {label}",
        )


def _gross_test_simulation(day: date):
    months = _post_2015_months(day)
    years = sorted({month.year for month in months})
    households = [
        _payer(
            state,
            payment,
            months,
            person={
                "employment_income": {
                    str(year): DIFFERENTIAL_ANNUAL_EMPLOYMENT_INCOME for year in years
                },
                "snap_unearned_income_person": _monthly(
                    months, DIFFERENTIAL_MONTHLY_UNEARNED_INCOME
                ),
                "is_snap_gross_test_full_income_count_alien": _monthly(
                    months, full_count
                ),
            },
            spm_unit={
                "tanf": {str(year): 0 for year in years},
                "ca_state_supplement": _monthly(months, 0),
            },
        )
        for state in STATES
        for payment in DIFFERENTIAL_PAYMENTS
        for full_count in (True, False)
    ]
    return Simulation(situation=_situation(households)), months


@pytest.fixture(scope="module", params=POST_2015_DATES, ids=str)
def gross_test_case(request):
    return _gross_test_simulation(request.param)


def test_gross_test_income_matches_gross_income_at_equal_shares(gross_test_case):
    simulation, months = gross_test_case
    for month in months:
        label = _month_str(month)
        np.testing.assert_allclose(
            _calculate(simulation, "snap_gross_test_income", month),
            _calculate(simulation, "snap_gross_income", month),
            rtol=1e-6,
            atol=1e-3,
            err_msg=label,
        )

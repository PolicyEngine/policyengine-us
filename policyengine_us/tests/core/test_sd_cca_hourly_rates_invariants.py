"""Check hourly CCA bounds, monotonicity, and weekly compatibility.

Hypothesis changes hours and billed expenses in independent simulations. YAML
cases pin the county tables and rate modifiers. The weekly check evaluates the
main-branch benefit formula with independently aggregated per-child rates.
"""

import numpy as np
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation

PROVIDERS = [
    "FAMILY_DAY_CARE",
    "LICENSED_CENTER",
    "INFORMAL",
    "BEFORE_AFTER_SCHOOL",
]
COUNTIES = [
    "AURORA_COUNTY_SD",
    "MINNEHAHA_COUNTY_SD",
    "PENNINGTON_COUNTY_SD",
    "UNKNOWN",
]
HOURLY_MONTHS = ["2024-07", "2025-01", "2026-07"]
TOLERANCE = 0.01
SETTINGS = dict(
    max_examples=4,
    deadline=None,
    derandomize=True,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large],
)


@st.composite
def children(draw):
    return {
        "age": draw(st.sampled_from([0.5, 2.5, 3, 5, 6, 8, 12, 15])),
        "provider": draw(st.sampled_from(PROVIDERS)),
        "hours": draw(st.integers(0, 70)),
        "hours_raise": draw(st.integers(0, 20)),
        "disabled": draw(st.booleans()),
        "specialized": draw(st.booleans()),
        "approved_special_needs": draw(st.booleans()),
    }


@st.composite
def families(draw):
    return {
        "county": draw(st.sampled_from(COUNTIES)),
        "wages": draw(st.sampled_from([0, 12_000, 36_000, 80_000])),
        "expenses": draw(st.integers(0, 60_000)),
        "expense_raise": draw(st.integers(0, 24_000)),
        "children": draw(st.lists(children(), min_size=1, max_size=2)),
    }


def _situation(units, month, *, raise_hours=False, raise_expenses=False):
    year = month[:4]
    people = {}
    groups = {
        name: {}
        for name in [
            "tax_units",
            "spm_units",
            "families",
            "marital_units",
            "households",
        ]
    }
    for i, unit in enumerate(units):
        parent = f"parent_{i}"
        members = [parent]
        people[parent] = {
            "age": {year: 30},
            "employment_income": {year: unit["wages"]},
            "is_tax_unit_head": {year: True},
            "is_tax_unit_dependent": {year: False},
            "childcare_hours_per_week": {year: 0},
        }
        groups["marital_units"][f"parent_unit_{i}"] = {"members": [parent]}
        for j, child in enumerate(unit["children"]):
            name = f"child_{i}_{j}"
            members.append(name)
            people[name] = {
                "age": {year: child["age"]},
                "is_tax_unit_head": {year: False},
                "is_tax_unit_dependent": {year: True},
                "is_disabled": {year: child["disabled"]},
                "childcare_hours_per_week": {
                    year: child["hours"] + raise_hours * child["hours_raise"]
                },
                "sd_cca_provider_type": {month: child["provider"]},
                "sd_cca_specialized_infant_toddler_rate_eligible": {
                    month: child["specialized"]
                },
                "sd_cca_special_needs_rate_approved": {
                    month: child["approved_special_needs"]
                },
            }
            groups["marital_units"][f"child_unit_{i}_{j}"] = {"members": [name]}
        for group in ["tax_units", "spm_units", "families"]:
            groups[group][f"{group}_{i}"] = {"members": members}
        groups["spm_units"][f"spm_units_{i}"].update(
            {
                "meets_ccdf_activity_test": {year: True},
                "is_tanf_enrolled": {month: False},
                "spm_unit_pre_subsidy_childcare_expenses": {
                    year: unit["expenses"] + raise_expenses * unit["expense_raise"]
                },
            }
        )
        groups["households"][f"household_{i}"] = {
            "members": members,
            "state_code": {year: "SD"},
            "county_str": {year: unit["county"]},
        }
    return {"people": people, **groups}


def _run(units, month, **changes):
    sim = Simulation(situation=_situation(units, month, **changes))
    benefit = np.asarray(sim.calculate("sd_cca", month), dtype=float)
    expenses = np.asarray(
        sim.calculate("spm_unit_pre_subsidy_childcare_expenses", month), dtype=float
    )
    assert np.isfinite(benefit).all()
    assert (benefit >= -TOLERANCE).all()
    assert (benefit <= expenses + TOLERANCE).all()
    return sim, benefit


def _positive_case():
    # A low-income family owes no co-payment. At 40 hours per week, DSS pays
    # min(ceil(40 * 4.3) * $3.80, $24,000 / 12) = $653.60 per month.
    return {
        "county": "MINNEHAHA_COUNTY_SD",
        "wages": 12_000,
        "expenses": 24_000,
        "expense_raise": 12_000,
        "children": [
            {
                "age": 0.5,
                "provider": "FAMILY_DAY_CARE",
                "hours": 40,
                "hours_raise": 5,
                "disabled": False,
                "specialized": False,
                "approved_special_needs": False,
            }
        ],
    }


@settings(**SETTINGS)
@given(
    st.sampled_from(HOURLY_MONTHS),
    st.lists(families(), min_size=3, max_size=7),
)
def test_hourly_bounds_monotonicity_and_positive_payment(month, units):
    units = units + [_positive_case()]
    sim, base = _run(units, month)
    _, more_hours = _run(units, month, raise_hours=True)
    _, more_expenses = _run(units, month, raise_expenses=True)
    assert (more_hours >= base - TOLERANCE).all()
    assert (more_expenses >= base - TOLERANCE).all()
    assert sim.calculate("sd_cca_eligible", month)[-1]
    assert sim.calculate("sd_cca_copay", month)[-1] == 0
    assert base[-1] > 0


@settings(**SETTINGS)
@given(
    st.integers(2026 * 12 + 7, 2030 * 12 + 11),
    st.lists(families(), min_size=3, max_size=7),
)
def test_weekly_formula_matches_main(month_index, units):
    month = f"{month_index // 12}-{month_index % 12 + 1:02d}"
    units = units + [_positive_case()]
    sim, benefit = _run(units, month)
    eligible_child = np.asarray(sim.calculate("sd_cca_eligible_child", month))
    in_care = np.asarray(sim.calculate("childcare_hours_per_week", month[:4])) > 0
    weekly_rate = np.asarray(sim.calculate("sd_cca_weekly_rate", month))
    spm_unit_ids = sim.populations["spm_unit"].members_entity_id
    maximum = np.bincount(
        spm_unit_ids,
        weights=weekly_rate * eligible_child * in_care,
        minlength=len(units),
    ) * (52 / 12)
    expenses = np.asarray(
        sim.calculate("spm_unit_pre_subsidy_childcare_expenses", month)
    )
    copay = np.asarray(sim.calculate("sd_cca_copay", month))
    eligible = np.asarray(sim.calculate("sd_cca_eligible", month))
    expected = np.where(
        eligible, np.maximum(np.minimum(expenses, maximum) - copay, 0), 0
    )
    np.testing.assert_allclose(benefit, expected, atol=TOLERANCE, rtol=0)

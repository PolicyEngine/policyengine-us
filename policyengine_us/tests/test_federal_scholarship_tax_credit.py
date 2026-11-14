"""Source-level accounting and FIFO checks for IRC section 25F.

Section 25F(b) caps each donor's current credit at $1,700. Section 25F(f)
applies a five-year, oldest-first carryforward in addition to that amount.
The October 2026 proposed section 1.25F-2 clarifies these enacted rules,
including separate spouses' caps and the state-credit offset before the cap.

The reference below is a dated queue of legal claims, independent of the
model's age-bucket formulas. Inputs carry valid historical balances explicitly;
each next year's inputs are the previous year's surviving outputs. These tests
do not infer historical incomes or change tax-unit membership.
"""

import numpy as np
import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from policyengine_us import CountryTaxBenefitSystem, Simulation


PREFIX = "federal_scholarship_tax_credit"
GIFT = "federal_scholarship_qualified_contributions"
STATE_CREDIT = "federal_scholarship_state_tax_credit"
TOLERANCE = 0.01


@pytest.fixture(scope="module")
def system():
    return CountryTaxBenefitSystem()


def situation(units, year):
    """Build independent filing units so one batch exercises vectorization."""
    people = {}
    groups = {
        group: {}
        for group in (
            "tax_units",
            "households",
            "spm_units",
            "families",
            "marital_units",
        )
    }
    for index, unit in enumerate(units):
        members = []
        for donor_index, donor in enumerate(unit["donors"]):
            name = f"person_{index}_{donor_index}"
            members.append(name)
            people[name] = {
                "age": {year: 40},
                "is_tax_unit_head": {year: donor_index == 0},
                "is_tax_unit_spouse": {year: donor_index == 1},
                "is_tax_unit_dependent": {year: False},
                "employment_income": {
                    year: unit.get("wages", 0) if donor_index == 0 else 0
                },
                "charitable_cash_donations": {
                    year: donor["qualified"] + donor.get("generic", 0)
                },
                GIFT: {year: donor["qualified"]},
                STATE_CREDIT: {year: donor.get("state_credit", 0)},
            }
        tax_unit = {
            "members": members,
            "filing_status": {year: "JOINT" if len(members) == 2 else "SINGLE"},
        }
        if "limit" in unit:
            tax_unit[f"{PREFIX}_credit_limit"] = {year: unit["limit"]}
        for age, value in unit.get("carry", {}).items():
            tax_unit[f"{PREFIX}_carryforward_{age}"] = {year: value}
        groups["tax_units"][f"unit_{index}"] = tax_unit
        for group in ("spm_units", "families", "marital_units"):
            groups[group][f"unit_{index}"] = {"members": members}
        groups["households"][f"unit_{index}"] = {
            "members": members,
            "state_code": {year: "TX"},
        }
    return {"people": people, **groups}


def values(simulation, variable, year):
    return np.asarray(simulation.calculate(variable, year), dtype=float)


@st.composite
def donor(draw):
    qualified = draw(st.integers(0, 6_000))
    return {
        "qualified": qualified,
        "state_credit": draw(st.integers(0, qualified)),
        "generic": draw(st.integers(0, 2_000)),
    }


unit_strategy = st.fixed_dictionaries(
    {
        "donors": st.lists(donor(), min_size=1, max_size=2),
        "limit": st.integers(0, 8_000),
    }
)


@settings(
    max_examples=6,
    deadline=None,
    derandomize=True,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large],
)
@given(st.lists(unit_strategy, min_size=2, max_size=12))
def test_vectorized_donor_bounds_and_current_credit_accounting(system, units):
    year = 2027
    simulation = Simulation(tax_benefit_system=system, situation=situation(units, year))
    per_donor = values(simulation, f"{PREFIX}_person", year)
    potential = values(simulation, f"{PREFIX}_potential", year)
    credit = values(simulation, PREFIX, year)
    current_remaining = values(simulation, f"{PREFIX}_carryforward_remaining_0", year)
    cash = values(simulation, "federal_scholarship_charitable_cash_donations", year)
    donors = [person for unit in units for person in unit["donors"]]
    qualified = np.array([person["qualified"] for person in donors])
    generic = np.array([person["generic"] for person in donors])
    limits = np.array([unit["limit"] for unit in units])
    caps = np.array([len(unit["donors"]) * 1_700 for unit in units])

    assert (per_donor >= 0).all()
    assert (per_donor <= 1_700 + TOLERANCE).all()
    assert (per_donor <= qualified + TOLERANCE).all()
    assert (potential <= caps + TOLERANCE).all()
    assert (credit >= 0).all()
    assert (credit <= limits + TOLERANCE).all()
    assert (credit <= potential + TOLERANCE).all()
    # Every current credit dollar is either used or preserved, never both.
    np.testing.assert_allclose(credit + current_remaining, potential, atol=TOLERANCE)
    np.testing.assert_allclose(
        credit[limits >= potential], potential[limits >= potential], atol=TOLERANCE
    )
    # Scholarship restrictions cannot remove a separate, ordinary donation.
    assert (cash >= generic - TOLERANCE).all()
    assert (cash <= generic + qualified + TOLERANCE).all()
    no_state = np.array([person["state_credit"] == 0 for person in donors])
    np.testing.assert_allclose(
        (cash + per_donor)[no_state],
        (generic + qualified)[no_state],
        atol=TOLERANCE,
    )


def reference_queue(year, opening_by_origin, current_credit, liability):
    """Pay dated claims oldest first, then discard claims expiring this year."""
    claims = [
        [origin, balance]
        for origin, balance in sorted(opening_by_origin.items())
        if 0 < year - origin <= 5 and origin >= 2027
    ]
    claims.append([year, current_credit])
    available = liability
    used = 0
    for claim in claims:
        payment = min(claim[1], available)
        claim[1] -= payment
        available -= payment
        used += payment
    expired = sum(balance for origin, balance in claims if year - origin == 5)
    surviving = {origin: balance for origin, balance in claims if year - origin < 5}
    return used, expired, surviving, dict(claims)


ledger_strategy = st.fixed_dictionaries(
    {
        "donors": st.just([{"qualified": 0}]),
        "carry": st.fixed_dictionaries(
            {age: st.integers(0, 3_400) for age in range(1, 6)}
        ),
        "current": st.integers(0, 5_000),
        "limit": st.integers(0, 20_000),
    }
)


@settings(
    max_examples=6,
    deadline=None,
    derandomize=True,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large],
)
@given(st.lists(ledger_strategy, min_size=2, max_size=12))
def test_vectorized_carryforward_matches_independent_dated_queue(system, units):
    year = 2033
    units = [{**unit, "donors": [{"qualified": unit["current"]}]} for unit in units]
    simulation = Simulation(tax_benefit_system=system, situation=situation(units, year))
    expected = [
        reference_queue(
            year,
            {year - age: amount for age, amount in unit["carry"].items()},
            min(unit["current"], 1_700),
            unit["limit"],
        )
        for unit in units
    ]
    actual_credit = values(simulation, PREFIX, year)
    actual_expired = values(simulation, f"{PREFIX}_expired", year)
    actual_closing = values(simulation, f"{PREFIX}_carryforward_remaining", year)
    np.testing.assert_allclose(
        actual_credit, [row[0] for row in expected], atol=TOLERANCE
    )
    np.testing.assert_allclose(
        actual_expired, [row[1] for row in expected], atol=TOLERANCE
    )
    np.testing.assert_allclose(
        actual_closing, [sum(row[2].values()) for row in expected], atol=TOLERANCE
    )
    for age in range(6):
        np.testing.assert_allclose(
            values(simulation, f"{PREFIX}_carryforward_remaining_{age}", year),
            [row[3].get(year - age, 0) for row in expected],
            atol=TOLERANCE,
        )
    opening = np.array([sum(unit["carry"].values()) for unit in units])
    current = np.array([min(unit["current"], 1_700) for unit in units])
    np.testing.assert_allclose(
        opening + current,
        actual_credit + actual_expired + actual_closing,
        atol=TOLERANCE,
    )


def test_explicit_rollover_matches_proposed_example_five(system):
    # REG-117199-25 proposed 1.25F-2(h)(5): the $100 from 2027 expires
    # after 2032; in 2033 $6,700 remains, $4,500 is used, and the new
    # $1,700 is also unused, leaving $3,900 available for 2034.
    gifts = [1_000, 1_000, 1_000, 1_500, 1_500, 2_000, 2_000]
    limits = [900, 0, 0, 0, 0, 0, 4_500]
    opening = {}
    reference_opening = {}
    for year, gift, limit in zip(range(2027, 2034), gifts, limits):
        unit = {
            "donors": [{"qualified": gift}],
            "limit": limit,
            "carry": opening,
        }
        simulation = Simulation(
            tax_benefit_system=system, situation=situation([unit], year)
        )
        used, expired, surviving, all_claims = reference_queue(
            year, reference_opening, min(gift, 1_700), limit
        )
        assert values(simulation, PREFIX, year)[0] == pytest.approx(used)
        assert values(simulation, f"{PREFIX}_expired", year)[0] == pytest.approx(
            expired
        )
        assert values(simulation, f"{PREFIX}_carryforward_remaining", year)[
            0
        ] == pytest.approx(sum(surviving.values()))
        for age in range(6):
            assert values(simulation, f"{PREFIX}_carryforward_remaining_{age}", year)[
                0
            ] == pytest.approx(all_claims.get(year - age, 0))
        opening = {
            age + 1: values(simulation, f"{PREFIX}_carryforward_remaining_{age}", year)[
                0
            ]
            for age in range(5)
        }
        reference_opening = surviving
        if year == 2032:
            assert expired == 100
        if year == 2033:
            assert used == 4_500
            assert sum(surviving.values()) == 3_900


def test_qualified_gift_reduces_actual_federal_tax_dollar_for_dollar(system):
    year = 2027
    units = [
        {"donors": [{"qualified": 0}], "wages": 100_000},
        {"donors": [{"qualified": 1_000}], "wages": 100_000},
        {"donors": [{"qualified": 0, "generic": 1_000}], "wages": 100_000},
    ]
    simulation = Simulation(tax_benefit_system=system, situation=situation(units, year))
    credit = values(simulation, PREFIX, year)
    np.testing.assert_allclose(credit, [0, 1_000, 0], atol=TOLERANCE)
    np.testing.assert_allclose(
        values(simulation, "adjusted_gross_income", year), [100_000] * 3
    )
    np.testing.assert_array_equal(
        simulation.calculate("tax_unit_itemizes", year), [False, False, False]
    )
    np.testing.assert_allclose(
        values(simulation, "charitable_deduction_for_non_itemizers", year),
        [0, 0, 1_000],
        atol=TOLERANCE,
    )
    taxes = values(simulation, "income_tax", year)
    assert taxes[0] - taxes[1] == pytest.approx(1_000, abs=TOLERANCE)
    net_income = values(simulation, "household_net_income", year)
    # Net income does not itself subtract charitable spending. The donor's
    # after-gift resources are unchanged only after subtracting the $1,000 gift.
    assert net_income[1] - 1_000 == pytest.approx(net_income[0], abs=TOLERANCE)

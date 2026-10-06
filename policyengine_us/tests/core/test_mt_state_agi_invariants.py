"""Invariants of Montana's state adjusted gross income as TAXSIM reports it.

Montana Form 2 for 2021-2023 reports Montana adjusted gross income on page 1,
line 14: federal adjusted gross income (line 11) plus Montana additions
(line 12) minus Montana subtractions (line 13). A joint return fills one
column for the couple; under filing status 2a (married filing separately on
the same form) each spouse fills their own column. From 2024 Form 2 starts
from federal adjusted gross income (line 1) and federal taxable income, and
has no Montana adjusted gross income line, so the state AGI that TAXSIM
reports is federal adjusted gross income. TAXSIM (taxsimtest build 2025Aug23)
reports exactly this: 80,000 for a 2022 couple with 100,000 of wages and a
20,000 Schedule C loss, 121,200 (Montana AGI) for a 2023 filer aged 70, and
100,000 (federal AGI) for a 2024 filer aged 70 whose Montana taxable income
nets a 5,500 subtraction.

A seeded grid of single filers and couples (ages 40 and 70, wages,
self-employment gains and losses, pensions, Social Security and interest)
runs as one simulation per year from 2021 to 2027, and Hypothesis draws
further batches. For every tax unit:

1. Filing path: `mt_agi` is the sum of each spouse's `mt_agi_indiv` when the
   couple files separately on the same form, and `mt_agi_joint` otherwise.
2. Reporting: `taxsim_state_agi`, and its alias `state_agi`, equal `mt_agi`
   through 2023 and federal adjusted gross income from 2024.
3. Pooling: through 2023, a unit on the joint path with no Montana additions
   or subtractions and no Social Security reports max(0, federal AGI), so one
   spouse's loss offsets the other spouse's income.
4. Bounds: `mt_agi` is never negative, and a unit outside Montana has no
   `mt_agi`.

Guards check that the grid reaches both filing paths, a joint-path couple
whose pooled AGI differs from the sum of the spouses' floored AGIs, and, from
2024, a filer whose Montana base differs from federal AGI, so properties 1-3
are never vacuous.
"""

from itertools import product

import numpy as np
import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation

TOLERANCE = 0.01  # dollars
YEARS = range(2021, 2028)
# Restated from Form 2, independently of
# gov.states.household.states_using_federal_agi.
FIRST_FEDERAL_AGI_YEAR = 2024

PERSON_INPUTS = (
    "age",
    "employment_income",
    "self_employment_income",
    "taxable_private_pension_income",
    "social_security_retirement",
    "taxable_interest_income",
)
TAX_UNIT_OUTPUTS = (
    "mt_agi",
    "mt_agi_joint",
    "mt_files_separately",
    "taxsim_state_agi",
    "state_agi",
    "adjusted_gross_income",
)
PERSON_OUTPUTS = (
    "mt_agi_indiv",
    "mt_additions",
    "mt_subtractions",
    "social_security",
)


def _person(age, wages=0, self_employment=0, pension=0, social_security=0, interest=0):
    return dict(
        age=age,
        employment_income=float(wages),
        self_employment_income=float(self_employment),
        taxable_private_pension_income=float(pension),
        social_security_retirement=float(social_security),
        taxable_interest_income=float(interest),
    )


def _seeded_units():
    """Single filers and couples in Montana, plus one Idaho couple."""
    units = []
    for age, head_wages, spouse in product(
        (40, 70),
        (0, 30_000, 100_000),
        (None, (0, -20_000), (0, 15_000), (60_000, 0), (60_000, -20_000)),
    ):
        # Retirees also get the income Montana adjusts: pensions, Social
        # Security and interest.
        retiree = dict(pension=10_000, social_security=12_000, interest=3_000)
        extra = retiree if age == 70 else {}
        head = _person(age, wages=head_wages, **extra)
        if spouse is None:
            units.append(("MT", head, None))
            continue
        spouse_wages, spouse_self_employment = spouse
        units.append(
            (
                "MT",
                head,
                _person(age, spouse_wages, spouse_self_employment, **extra),
            )
        )
    units.append(("ID", _person(40, 100_000), _person(40, 0, -20_000)))
    return units


def _situation(units, year):
    period = str(year)
    people, tax_units, families, spm_units, marital_units, households = (
        {},
        {},
        {},
        {},
        {},
        {},
    )
    for i, (state, head, spouse) in enumerate(units):
        members = []
        for role, inputs in (("head", head), ("spouse", spouse)):
            if inputs is None:
                continue
            name = f"{role}_{i}"
            people[name] = {k: {period: inputs[k]} for k in PERSON_INPUTS}
            members.append(name)
        tax_units[f"tax_unit_{i}"] = {"members": members}
        families[f"family_{i}"] = {"members": members}
        spm_units[f"spm_unit_{i}"] = {"members": members}
        marital_units[f"marital_unit_{i}"] = {"members": members}
        households[f"household_{i}"] = {
            "members": members,
            "state_code": {period: state},
        }
    return dict(
        people=people,
        tax_units=tax_units,
        families=families,
        spm_units=spm_units,
        marital_units=marital_units,
        households=households,
    )


def _run(units, year):
    simulation = Simulation(situation=_situation(units, year))
    run = {name: simulation.calculate(name, year) for name in TAX_UNIT_OUTPUTS}
    for name in PERSON_OUTPUTS:
        run[name] = simulation.map_result(
            simulation.calculate(name, year), "person", "tax_unit"
        )
    run["in_mt"] = np.array([state == "MT" for state, _, _ in units])
    return run


def _check(units, year):
    """Assert properties 1-4 for every unit and return the run."""
    run = _run(units, year)
    in_mt = run["in_mt"]
    separate = run["mt_files_separately"]
    mt_agi = run["mt_agi"]

    # 1. Filing path.
    expected_mt_agi = np.where(separate, run["mt_agi_indiv"], run["mt_agi_joint"])
    np.testing.assert_allclose(mt_agi[in_mt], expected_mt_agi[in_mt], atol=TOLERANCE)
    if year >= FIRST_FEDERAL_AGI_YEAR:
        assert not separate.any()
        assert (run["mt_agi_indiv"] == 0).all()

    # 2. Reporting.
    reported = run["taxsim_state_agi"]
    if year >= FIRST_FEDERAL_AGI_YEAR:
        expected_reported = run["adjusted_gross_income"]
    else:
        expected_reported = mt_agi
    np.testing.assert_allclose(
        reported[in_mt], expected_reported[in_mt], atol=TOLERANCE
    )
    np.testing.assert_allclose(run["state_agi"], reported, atol=TOLERANCE)

    # 3. Pooling.
    unadjusted = (
        (run["mt_additions"] == 0)
        & (run["mt_subtractions"] == 0)
        & (run["social_security"] == 0)
    )
    pooled = in_mt & ~separate & unadjusted
    if year < FIRST_FEDERAL_AGI_YEAR:
        np.testing.assert_allclose(
            reported[pooled],
            np.maximum(run["adjusted_gross_income"][pooled], 0),
            atol=TOLERANCE,
        )

    # 4. Bounds.
    assert (mt_agi >= 0).all()
    assert (mt_agi[~in_mt] == 0).all()
    return run


@pytest.mark.parametrize("year", YEARS)
def test_seeded_grid(year):
    run = _check(_seeded_units(), year)
    in_mt = run["in_mt"]
    separate = run["mt_files_separately"]
    if year < FIRST_FEDERAL_AGI_YEAR:
        # Both filing paths are reached.
        assert (in_mt & separate).any()
        assert (in_mt & ~separate).any()
        # Pooling matters for some joint-path couple: summing each spouse's
        # floored Montana AGI, as taxsim_state_agi used to, overstates it.
        floored_sum = run["mt_agi_indiv"]
        joint_path = in_mt & ~separate
        assert (floored_sum[joint_path] > run["mt_agi"][joint_path] + 1).any()
    else:
        # Federal AGI is not just the Montana base under another name.
        assert (
            np.abs(run["mt_agi_joint"] - run["adjusted_gross_income"])[in_mt] > 1
        ).any()


amount = st.integers(0, 150_000)
gain_or_loss = st.integers(-40_000, 60_000)
people = st.builds(
    _person,
    age=st.sampled_from([25, 45, 64, 65, 80]),
    wages=amount,
    self_employment=gain_or_loss,
    pension=st.sampled_from([0, 12_000]),
    social_security=st.sampled_from([0, 18_000]),
    interest=st.sampled_from([0, 2_500]),
)
units = st.tuples(st.sampled_from(["MT", "MT", "MT", "ID"]), people, st.none() | people)

# A batch's cost is mostly per-variable overhead, so each example is a large
# batch and there are few examples.
SETTINGS = dict(
    max_examples=5,
    deadline=None,
    derandomize=True,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large],
)


@settings(**SETTINGS)
@given(st.lists(units, min_size=10, max_size=30), st.sampled_from(list(YEARS)))
def test_drawn_batches(batch, year):
    _check(batch, year)

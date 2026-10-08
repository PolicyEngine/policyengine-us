"""Core aggregation invariants for the Schedule D specialty worksheets.

The 2025 Schedule D instructions' 28% Rate Gain Worksheet (page 11) and
Unrecaptured Section 1250 Gain Worksheet (page 13) use amounts from the
taxpayer's return: https://www.irs.gov/pub/irs-prior/i1040sd--2025.pdf.

Port the specialty dependent cohorts from PR #9977's investment-interest
properties without its Form 4952 calculations. YAML covers policy examples
and regular tax; Hypothesis covers arbitrary vectorized populations, changes
to dependents' inputs, and redistribution between the head and spouse.

Each example constructs a small Core system containing the production
worksheet classes and their inputs, without reconstructing the full US
model or parameters per example. Package import builds the global model once. Cohorts use separate tax units in the same fresh simulation,
avoiding cache invalidation or shared mutable simulation state. The file
routes to the existing rest-python core CI group.
"""

from copy import deepcopy

import numpy as np
from hypothesis import given, settings, strategies as st
from policyengine_core.periods import period
from policyengine_core.simulations import Simulation
from policyengine_core.taxbenefitsystems import TaxBenefitSystem

from policyengine_us.entities import Person, TaxUnit
from policyengine_us.variables.gov.irs.tax.federal_income.capital_gains.capital_gains_28_percent_rate_gain import (
    capital_gains_28_percent_rate_gain,
    rate_gains_less_losses,
)
from policyengine_us.variables.gov.irs.tax.federal_income.capital_gains.schedule_d_unrecaptured_section_1250_gain import (
    schedule_d_unrecaptured_section_1250_gain,
)
from policyengine_us.variables.household.demographic.tax_unit.is_tax_unit_dependent import (
    is_tax_unit_dependent,
)
from policyengine_us.variables.household.income.person.capital_gains.collectibles_gain_or_loss import (
    collectibles_gain_or_loss,
)
from policyengine_us.variables.household.income.person.capital_gains.long_term_capital_gains_on_collectibles import (
    long_term_capital_gains_on_collectibles,
)
from policyengine_us.variables.household.income.person.capital_gains.long_term_capital_gains_on_small_business_stock import (
    long_term_capital_gains_on_small_business_stock,
)
from policyengine_us.variables.household.income.person.capital_gains.long_term_capital_loss_carryover import (
    long_term_capital_loss_carryover,
)
from policyengine_us.variables.household.income.person.capital_gains.section_1202_gain import (
    section_1202_gain,
)
from policyengine_us.variables.household.income.person.capital_gains.short_term_capital_gains import (
    short_term_capital_gains,
)
from policyengine_us.variables.household.income.person.capital_gains.unrecaptured_section_1250_gain import (
    unrecaptured_section_1250_gain,
)
from policyengine_us.variables.household.income.person.capital_gains.unrecaptured_section_1250_gain_before_losses import (
    unrecaptured_section_1250_gain_before_losses,
)

PERIOD = "2025"
INPUT_CLASSES = (
    collectibles_gain_or_loss,
    section_1202_gain,
    short_term_capital_gains,
    long_term_capital_loss_carryover,
    long_term_capital_gains_on_collectibles,
    long_term_capital_gains_on_small_business_stock,
)
INPUTS = tuple(variable.__name__ for variable in INPUT_CLASSES)
OUTPUTS = (
    "rate_gains_less_losses",
    "capital_gains_28_percent_rate_gain",
    "schedule_d_unrecaptured_section_1250_gain",
)
ZERO = dict.fromkeys(INPUTS, 0)


def _simulate(units, *, reverse_members=False):
    """Evaluate all comparison cohorts in one isolated, minimal Core model."""
    system = TaxBenefitSystem(entities=[Person, TaxUnit])
    system.add_variables(
        *INPUT_CLASSES,
        is_tax_unit_dependent,
        unrecaptured_section_1250_gain,
        unrecaptured_section_1250_gain_before_losses,
        capital_gains_28_percent_rate_gain,
        schedule_d_unrecaptured_section_1250_gain,
    )
    people, tax_units = {}, {}
    for i, unit in enumerate(units):
        members = []
        roles = [("head", unit["head"], False)]
        if unit["spouse"] is not None:
            roles.append(("spouse", unit["spouse"], False))
        roles.extend(
            (f"dependent{j}", amounts, True)
            for j, amounts in enumerate(unit["dependents"])
        )
        for role, amounts, dependent in roles:
            name = f"u{i}_{role}"
            members.append(name)
            people[name] = {
                "is_tax_unit_dependent": {PERIOD: dependent},
                **{variable: {PERIOD: value} for variable, value in amounts.items()},
            }
        tax_units[f"t{i}"] = {
            "members": list(reversed(members)) if reverse_members else members,
            "unrecaptured_section_1250_gain_before_losses": {PERIOD: unit["gain"]},
            "unrecaptured_section_1250_gain": {PERIOD: unit["reported"]},
        }
    simulation = Simulation(
        tax_benefit_system=system,
        situation={"people": people, "tax_units": tax_units},
    )
    return {
        "rate_gains_less_losses": rate_gains_less_losses(
            simulation.populations["tax_unit"], period(PERIOD)
        ),
        **{
            name: simulation.calculate(name, PERIOD)
            for name in OUTPUTS
            if name != "rate_gains_less_losses"
        },
    }


def test_ported_dependent_specialty_input_cohorts():
    """All eight PR #9977 perturbations, both loss regimes, single and joint."""
    dependent_cases = (
        ("long_term_capital_gains_on_collectibles", 10_000),
        ("long_term_capital_gains_on_small_business_stock", 10_000),
        ("collectibles_gain_or_loss", 10_000),
        ("collectibles_gain_or_loss", -10_000),
        ("section_1202_gain", 10_000),
        ("short_term_capital_gains", -10_000),
        ("short_term_capital_gains", 10_000),
        ("long_term_capital_loss_carryover", 10_000),
    )
    base, changed, expected_28, expected_1250 = [], [], [], []
    for excess_losses in (False, True):
        for name, amount in dependent_cases:
            for joint in (False, True):
                head, spouse = ZERO.copy(), ZERO.copy() if joint else None
                for variable, single, head_amount, spouse_amount in (
                    ("short_term_capital_gains", -2_000, -4_000, 2_000),
                    ("collectibles_gain_or_loss", 7_000, 10_000, -3_000),
                    ("section_1202_gain", 4_000, 3_000, 1_000),
                    ("long_term_capital_loss_carryover", 2_000, 1_000, 1_000),
                ):
                    head[variable] = head_amount if joint else single
                    if joint:
                        spouse[variable] = spouse_amount
                if excess_losses:
                    head["collectibles_gain_or_loss"] -= 10_000
                unit = {
                    "head": head,
                    "spouse": spouse,
                    "dependents": [ZERO.copy()],
                    "gain": 10_000,
                    "reported": 0,
                }
                base.append(unit)
                changed_unit = deepcopy(unit)
                changed_unit["dependents"][0][name] = amount
                changed.append(changed_unit)
                expected_28.append(0 if excess_losses else 7_000)
                expected_1250.append(7_000 if excess_losses else 10_000)

    results = _simulate(base + changed)
    size = len(base)
    # The second regime's $3,000 excess loss reduces line 19. A dependent's
    # positive gain cannot absorb that loss; its losses cannot increase it.
    for name, expected in (
        ("capital_gains_28_percent_rate_gain", expected_28),
        ("schedule_d_unrecaptured_section_1250_gain", expected_1250),
    ):
        np.testing.assert_array_equal(results[name], np.tile(expected, 2))
    for name in OUTPUTS:
        np.testing.assert_array_equal(results[name][size:], results[name][:size])


# Whole-dollar inputs and small populations keep all sums exactly
# representable in float32; the comparisons need no rounding tolerance.
SIGNED = st.integers(min_value=-60_000, max_value=80_000)
NONNEGATIVE = st.integers(min_value=0, max_value=40_000)
PERSON_AMOUNTS = st.fixed_dictionaries(
    {
        name: SIGNED
        if name in ("collectibles_gain_or_loss", "short_term_capital_gains")
        else NONNEGATIVE
        for name in INPUTS
    }
)
UNITS = st.lists(
    st.fixed_dictionaries(
        {
            "head": PERSON_AMOUNTS,
            "spouse": st.one_of(st.none(), PERSON_AMOUNTS),
            "dependents": st.lists(PERSON_AMOUNTS, min_size=1, max_size=3),
            "gain": NONNEGATIVE,
            "reported": NONNEGATIVE,
        }
    ),
    min_size=1,
    max_size=5,
)


@settings(max_examples=60, deadline=None)
@given(units=UNITS)
def test_vectorized_worksheets_depend_only_on_non_dependents(units):
    """Perturbing dependents or redistributing spouses' amounts preserves outputs."""
    zero_dependents, collapsed = deepcopy(units), deepcopy(units)
    for unit in zero_dependents:
        unit["dependents"] = [ZERO.copy() for _ in unit["dependents"]]
    totals = []
    for unit, collapsed_unit in zip(units, collapsed):
        filers = [unit["head"]]
        if unit["spouse"] is not None:
            filers.append(unit["spouse"])
        total = {name: sum(person[name] for person in filers) for name in INPUTS}
        totals.append(total)
        collapsed_unit["head"] = total
        if unit["spouse"] is not None:
            collapsed_unit["spouse"] = ZERO.copy()

    results = _simulate(zero_dependents + units + collapsed)
    size = len(units)
    reordered = _simulate(units, reverse_members=True)
    for name in OUTPUTS:
        baseline, actual, pooled = np.split(results[name], 3)
        np.testing.assert_array_equal(actual, baseline, err_msg=name)
        np.testing.assert_array_equal(actual, pooled, err_msg=name)
        np.testing.assert_array_equal(actual, reordered[name], err_msg=name)

    # Independent worksheet lines from the non-dependents' raw inputs:
    # 28% lines 1-4 add gains; lines 5-6 subtract the return's losses.
    # Net short-term gains/losses are combined before taking the loss.
    expected_net, expected_28, expected_1250 = [], [], []
    for unit, total in zip(units, totals):
        gains = total["collectibles_gain_or_loss"] + total["section_1202_gain"]
        losses = total["long_term_capital_loss_carryover"] + max(
            0, -total["short_term_capital_gains"]
        )
        net = gains - losses
        line_18 = (
            total["long_term_capital_gains_on_collectibles"]
            + total["long_term_capital_gains_on_small_business_stock"]
            + max(0, net)
        )
        # Section 1250 lines 14-18 deduct only excess losses, and preserve
        # amounts already reported after netting on Schedule D line 19.
        excess_losses = 0 if line_18 > 0 else max(0, losses - gains)
        line_19 = unit["reported"] + max(0, unit["gain"] - excess_losses)
        expected_net.append(net)
        expected_28.append(line_18)
        expected_1250.append(line_19)
    for name, expected in zip(OUTPUTS, (expected_net, expected_28, expected_1250)):
        np.testing.assert_array_equal(
            results[name][size : 2 * size], expected, err_msg=name
        )

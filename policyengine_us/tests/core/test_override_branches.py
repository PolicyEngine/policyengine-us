"""Formula branches calculate under their overrides, whatever was cached first.

Several formulas compare a tax unit's liability under alternative choices by
calculating it in a branch with one input overridden: itemizing or not
(``tax_unit_itemizes``), Delaware and Virginia EITC refundability, the Idaho
aged or disabled credit or deduction, Missouri TANF caretaker inclusion and
Medicaid for SSI state supplements. A Core branch snapshots its parent's inputs
and results. Core now invalidates calculated values when an input changes;
``get_override_branch`` controls branch reuse for the requested period and
overrides. ``get_branch_for_period`` is the same without inputs.

The non-refundable CTC used to be limited by the tax liability recomputed
without the SALT deduction, in a "no_salt" branch. The branch usually inherited
the liability with SALT, so the CTC depended on which variables a caller asked
for first. 26 U.S.C. 26(a) limits the credit by the actual tax liability, SALT
deduction included, and Schedule 8812 Credit Limit Worksheet A starts from it
(line 1 is Form 1040 line 18); ``ctc_tax_liability_after_preceding_credits``
(line 3) now reads it directly.

A seeded sample of households shares one simulation; the tests check:

1. The CTC-limiting liability is Worksheet A line 5 computed from income tax
   before credits: less the credits that precede the CTC (line 3), then less
   the credits that follow it when Worksheet B applies; and the non-refundable
   and refundable parts add up to the credit.
2. Every reported variable is the same whichever variable is calculated first,
   on the seeded sample and on random households (Hypothesis).
3. Each comparison branch equals a fresh simulation that sets the overridden
   input before anything is calculated (a differential test of the branch
   against the reference path).
4. The same holds when the parent has already calculated the overridden
   input, and when an earlier year was calculated first.
5. When the branch drops what it copied, it keeps exactly the values set as
   inputs, each for the period it was set for: a variable that is an input in
   one year is calculated again in the others (Hypothesis, over random mixes
   of input years and formula years).
"""

import numpy as np
import pytest
from hypothesis import HealthCheck, example, given, settings
from hypothesis import strategies as st
from policyengine_core.periods import period

from policyengine_us import Simulation
from policyengine_us.tools.period_branch import (
    get_branch_for_period,
    get_override_branch,
)

YEAR = 2026
SEED = 20261001
N = 48
STATES = ["CA", "NY", "VA", "DE", "ID", "NJ", "MA", "IL", "TX", "OR"]
REPORTED = [
    "income_tax",
    "income_tax_before_credits",
    "ctc_limiting_tax_liability",
    "non_refundable_ctc",
    "refundable_ctc",
    "tax_unit_itemizes",
    "state_income_tax",
    "household_net_income",
]


def _sample():
    rng = np.random.default_rng(SEED)
    households = []
    for i in range(N):
        married = bool(rng.random() < 0.6)
        children = int(rng.integers(0, 4))
        earnings = float(np.round(np.exp(rng.uniform(np.log(8_000), np.log(300_000)))))
        households.append(
            dict(
                state=STATES[i % len(STATES)],
                married=married,
                children=children,
                earnings=earnings,
                spouse_share=float(rng.choice([0, 0.2, 0.5])) if married else 0,
                mortgage=float(rng.choice([0, 8_000, 18_000, 30_000])),
                property_tax=float(rng.choice([0, 3_000, 9_000, 16_000])),
                charity=float(rng.choice([0, 2_000, 9_000])),
                aged_parent=bool(rng.random() < 0.15),
            )
        )
    return households


def _situation(households, years=(YEAR,), itemizes=None):
    people, units, marital = {}, {}, {}
    for i, h in enumerate(households):
        members = []

        def add(name, **inputs):
            people[name] = {k: {y: v for y in years} for k, v in inputs.items()}
            members.append(name)

        head = f"h{i}"
        earnings = h["earnings"]
        add(
            head,
            age=40,
            employment_income=earnings * (1 - h["spouse_share"]),
            deductible_mortgage_interest=h["mortgage"],
            real_estate_taxes=h["property_tax"],
            charitable_cash_donations=h["charity"],
        )
        marital[f"mu_{head}"] = {"members": [head]}
        if h["married"]:
            add(f"s{i}", age=38, employment_income=earnings * h["spouse_share"])
            marital[f"mu_{head}"]["members"].append(f"s{i}")
        for c in range(h["children"]):
            add(f"c{i}_{c}", age=3 + 4 * c, is_tax_unit_dependent=True)
            marital[f"mu_c{i}_{c}"] = {"members": [f"c{i}_{c}"]}
        if h["aged_parent"]:
            add(
                f"p{i}",
                age=74,
                is_tax_unit_dependent=True,
                share_of_care_and_support_costs_paid_by_tax_filer=1.0,
            )
            marital[f"mu_p{i}"] = {"members": [f"p{i}"]}
        units[i] = members
    tax_units = {f"tu{i}": {"members": m} for i, m in units.items()}
    if itemizes is not None:
        for i, unit in enumerate(tax_units.values()):
            unit["tax_unit_itemizes"] = {y: bool(itemizes[i]) for y in years}
    return {
        "people": people,
        "tax_units": tax_units,
        "spm_units": {f"spm{i}": {"members": m} for i, m in units.items()},
        "families": {f"fam{i}": {"members": m} for i, m in units.items()},
        "marital_units": marital,
        "households": {
            f"hh{i}": {
                "members": m,
                "state_code": {y: households[i]["state"] for y in years},
            }
            for i, m in units.items()
        },
    }


@pytest.fixture(scope="module")
def households():
    return _sample()


@pytest.fixture(scope="module")
def baseline(households):
    simulation = Simulation(situation=_situation(households))
    return {v: simulation.calculate(v, YEAR) for v in REPORTED}


def test_ctc_limit_starts_from_actual_liability(households):
    simulation = Simulation(situation=_situation(households))
    limit = simulation.calculate("ctc_limiting_tax_liability", YEAR)
    before_credits = simulation.calculate("income_tax_before_credits", YEAR)
    p = simulation.tax_benefit_system.parameters(YEAR).gov.irs.credits
    preceding = sum(
        simulation.calculate(credit, YEAR)
        for credit in p.ctc_tax_liability_limit.preceding_credits
    )
    subsequent = sum(
        simulation.calculate(credit, YEAR)
        for credit in p.ctc_tax_liability_limit.subsequent_credits
    )
    worksheet_b = simulation.calculate("ctc_credit_limit_worksheet_b_applies", YEAR)
    line_3 = np.maximum(0, before_credits - preceding)
    np.testing.assert_allclose(
        simulation.calculate("ctc_tax_liability_after_preceding_credits", YEAR),
        line_3,
    )
    np.testing.assert_allclose(
        limit, np.maximum(0, line_3 - np.where(worksheet_b, subsequent, 0))
    )
    ctc = simulation.calculate("ctc", YEAR)
    non_refundable = simulation.calculate("non_refundable_ctc", YEAR)
    refundable = simulation.calculate("refundable_ctc", YEAR)
    # non_refundable_ctc is the credit less its refundable part; the tax
    # limit applies when non-refundable credits are capped.
    assert (refundable <= ctc + 0.01).all()
    np.testing.assert_allclose(non_refundable + refundable, ctc, atol=0.01)
    # The sample includes itemizers with SALT whose CTC the limit binds.
    salt = simulation.calculate("salt_deduction", YEAR)
    itemizes = simulation.calculate("tax_unit_itemizes", YEAR)
    assert (itemizes & (salt > 0) & (limit < ctc)).any()


@pytest.mark.parametrize(
    "first",
    [
        "income_tax",
        "refundable_ctc",
        "ctc_value",
        "state_income_tax",
        "tax_liability_if_itemizing",
        "spm_unit_net_income",
    ],
)
def test_results_do_not_depend_on_calculation_order(households, baseline, first):
    simulation = Simulation(situation=_situation(households))
    simulation.calculate(first, YEAR)
    for variable in REPORTED:
        np.testing.assert_array_equal(
            simulation.calculate(variable, YEAR),
            baseline[variable],
            err_msg=f"{variable} changes when {first} is calculated first",
        )


household_strategy = st.fixed_dictionaries(
    {
        "state": st.sampled_from(STATES),
        "married": st.booleans(),
        "children": st.integers(0, 3),
        "earnings": st.integers(8_000, 300_000),
        "spouse_share": st.sampled_from([0, 0.2, 0.5]),
        "mortgage": st.integers(0, 40_000),
        "property_tax": st.integers(0, 20_000),
        "charity": st.integers(0, 10_000),
        "aged_parent": st.booleans(),
    }
)


@settings(
    max_examples=4,
    deadline=None,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large],
)
@given(
    st.lists(household_strategy, min_size=1, max_size=8),
    st.sampled_from(
        ["income_tax", "refundable_ctc", "tax_liability_if_itemizing", "eitc"]
    ),
)
def test_random_households_do_not_depend_on_calculation_order(households, first):
    reference = Simulation(situation=_situation(households))
    reference.calculate("household_net_income", YEAR)
    simulation = Simulation(situation=_situation(households))
    simulation.calculate(first, YEAR)
    for variable in REPORTED:
        np.testing.assert_array_equal(
            simulation.calculate(variable, YEAR),
            reference.calculate(variable, YEAR),
            err_msg=f"{variable} changes when {first} is calculated first",
        )
    # Credit Limit Worksheet A, line 3 starts from the actual liability.
    p = simulation.tax_benefit_system.parameters(YEAR).gov.irs.credits
    preceding = sum(
        simulation.calculate(credit, YEAR)
        for credit in p.ctc_tax_liability_limit.preceding_credits
    )
    np.testing.assert_allclose(
        simulation.calculate("ctc_tax_liability_after_preceding_credits", YEAR),
        np.maximum(
            0, simulation.calculate("income_tax_before_credits", YEAR) - preceding
        ),
    )


def _fresh(households, variable, overrides, year=YEAR):
    simulation = Simulation(situation=_situation(households, years=(year,)))
    for name, value in overrides.items():
        simulation.set_input(name, year, value)
    return simulation.calculate(variable, year)


def test_itemization_branches_match_fresh_simulations(households):
    simulation = Simulation(situation=_situation(households))
    simulation.calculate("household_net_income", YEAR)
    n = len(households)
    for comparison, itemizes in (
        ("tax_liability_if_itemizing", True),
        ("tax_liability_if_not_itemizing", False),
    ):
        np.testing.assert_allclose(
            simulation.calculate(comparison, YEAR),
            _fresh(households, "income_tax", {"tax_unit_itemizes": [itemizes] * n}),
            atol=0.01,
            err_msg=comparison,
        )


@pytest.mark.parametrize(
    "comparison,variable,override,value",
    [
        (
            "de_income_tax_if_claiming_refundable_eitc",
            "de_income_tax",
            "de_claims_refundable_eitc",
            True,
        ),
        (
            "de_income_tax_if_claiming_non_refundable_eitc",
            "de_income_tax",
            "de_claims_refundable_eitc",
            False,
        ),
        (
            "va_income_tax_if_claiming_refundable_eitc",
            "va_income_tax",
            "va_claims_refundable_eitc",
            True,
        ),
        (
            "va_income_tax_if_claiming_non_refundable_eitc",
            "va_income_tax",
            "va_claims_refundable_eitc",
            False,
        ),
        (
            "id_income_tax_if_receiving_aged_or_disabled_credit",
            "id_income_tax",
            "id_receives_aged_or_disabled_credit",
            True,
        ),
        (
            "id_income_tax_if_receiving_aged_or_disabled_deduction",
            "id_income_tax",
            "id_receives_aged_or_disabled_credit",
            False,
        ),
    ],
)
def test_state_choice_branches_match_fresh_simulations(
    households, comparison, variable, override, value
):
    simulation = Simulation(situation=_situation(households))
    simulation.calculate("household_net_income", YEAR)
    np.testing.assert_allclose(
        simulation.calculate(comparison, YEAR),
        _fresh(households, variable, {override: [value] * len(households)}),
        atol=0.01,
    )


def test_branch_after_parent_calculated_the_overridden_input(households):
    # tax_unit_itemizes is an input here, so the parent calculates income tax
    # without the itemizing branch; the branch is created afterwards and must
    # not answer with the parent's income tax.
    n = len(households)
    situation = _situation(households, itemizes=[False] * n)
    simulation = Simulation(situation=situation)
    not_itemizing = simulation.calculate("income_tax", YEAR)
    itemizing = simulation.calculate("tax_liability_if_itemizing", YEAR)
    expected = _fresh(households, "income_tax", {"tax_unit_itemizes": [True] * n})
    np.testing.assert_allclose(itemizing, expected, atol=0.01)
    assert not np.allclose(itemizing, not_itemizing)


YEARS = (2025, YEAR)
# Formula variables between itemization and income tax that a situation can
# also supply as inputs, here for one year only.
MIXED_YEAR_INPUTS = [
    "taxable_income",
    "income_tax_main_rates",
    "adjusted_gross_income",
    "salt_deduction",
    "ctc",
]
# The household from review r2 of PolicyEngine/policyengine-us#9741.
REVIEW_HOUSEHOLD = dict(
    state="CA",
    married=True,
    children=2,
    earnings=160_000,
    spouse_share=0,
    mortgage=30_000,
    property_tax=14_000,
    charity=0,
    aged_parent=False,
)


def _with_tax_unit_inputs(situation, inputs):
    """Add each ``variable: (year, value)`` to every tax unit, for that year."""
    for unit in situation["tax_units"].values():
        for variable, (year, value) in inputs.items():
            unit[variable] = {year: value}
    return situation


def test_branch_recalculates_a_variable_that_is_an_input_in_another_year():
    # taxable_income is an input for 2025 only, so its 2026 value is
    # calculated: by the parent, without itemizing. The itemizing branch has
    # to calculate its own. Before the branch kept inputs by key and period,
    # it answered with the parent's ($13,140 of income tax instead of the
    # $8,191.05 an itemizing simulation gives).
    situation = _with_tax_unit_inputs(
        _situation([REVIEW_HOUSEHOLD], years=YEARS, itemizes=[False]),
        {"taxable_income": (2025, 1)},
    )
    simulation = Simulation(situation=situation)
    not_itemizing = simulation.calculate("income_tax", YEAR)
    itemizing = simulation.calculate("tax_liability_if_itemizing", YEAR)
    fresh = Simulation(situation=situation)
    fresh.set_input("tax_unit_itemizes", YEAR, np.array([True]))
    np.testing.assert_allclose(
        itemizing, fresh.calculate("income_tax", YEAR), atol=0.01
    )
    assert not np.allclose(itemizing, not_itemizing)


@settings(
    max_examples=4,
    deadline=None,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large],
)
@given(
    households=st.lists(household_strategy, min_size=1, max_size=4),
    inputs=st.dictionaries(
        st.sampled_from(MIXED_YEAR_INPUTS),
        st.tuples(st.sampled_from(YEARS), st.integers(0, 100_000)),
        min_size=1,
    ),
    year=st.sampled_from(YEARS),
    first=st.sampled_from(["income_tax", "taxable_income", "household_net_income"]),
    first_year=st.sampled_from(YEARS),
    parent_itemizes=st.sampled_from([None, False, True]),
)
@example(
    households=[REVIEW_HOUSEHOLD],
    inputs={"income_tax_main_rates": (2025, 1)},
    year=YEAR,
    first="income_tax",
    first_year=YEAR,
    parent_itemizes=False,
)
def test_branches_with_inputs_in_other_years_match_fresh_simulations(
    households, inputs, year, first, first_year, parent_itemizes
):
    # Each variable in ``inputs`` is an input in one year and a formula in
    # the other; tax_unit_itemizes is an input too unless parent_itemizes is
    # None. Both comparison branches equal a simulation with the same inputs
    # that sets itemization before calculating anything.
    n = len(households)
    itemizes = None if parent_itemizes is None else [parent_itemizes] * n
    situation = _with_tax_unit_inputs(
        _situation(households, years=YEARS, itemizes=itemizes), inputs
    )
    simulation = Simulation(situation=situation)
    simulation.calculate(first, first_year)
    for comparison, itemizing in (
        ("tax_liability_if_itemizing", True),
        ("tax_liability_if_not_itemizing", False),
    ):
        fresh = Simulation(situation=situation)
        fresh.set_input("tax_unit_itemizes", year, np.full(n, itemizing))
        np.testing.assert_allclose(
            simulation.calculate(comparison, year),
            fresh.calculate("income_tax", year),
            atol=0.01,
            err_msg=f"{comparison} for {year} after {first} for {first_year}",
        )


@settings(
    max_examples=6,
    deadline=None,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large],
)
@given(
    households=st.lists(household_strategy, min_size=1, max_size=3),
    situation_inputs=st.dictionaries(
        st.sampled_from(MIXED_YEAR_INPUTS), st.sampled_from(YEARS)
    ),
    branch_inputs=st.dictionaries(
        st.sampled_from(MIXED_YEAR_INPUTS + ["tax_unit_itemizes"]),
        st.sampled_from(YEARS),
    ),
    calculated=st.lists(
        st.tuples(
            st.sampled_from(["income_tax", "taxable_income", "tax_unit_itemizes"]),
            st.sampled_from(YEARS),
        ),
        min_size=1,
        max_size=3,
    ),
    head_input=st.sampled_from([None, "situation", "branch"]),
)
def test_clear_calculated_results_keeps_exactly_the_input_keys(
    households, situation_inputs, branch_inputs, calculated, head_input
):
    # Inputs in random years, on the simulation (from the situation) and on
    # a branch of it; values calculated in random years on both. A branch of
    # that branch, after clear_calculated_results, holds each input for the
    # period it was set for, the nearer branch's first, and nothing else.
    n = len(households)
    situation = _with_tax_unit_inputs(
        _situation(households, years=YEARS),
        {variable: (year, 1_000) for variable, year in situation_inputs.items()},
    )
    heads = np.array([name.startswith("h") for name in situation["people"]])
    if head_input == "situation":
        for name in situation["people"]:
            if name.startswith("h"):
                situation["people"][name]["is_household_head"] = {YEAR: True}
    simulation = Simulation(situation=situation)
    for variable, year in calculated:
        simulation.calculate(variable, year)
    parent = simulation.get_branch("parent")
    expected = {
        (variable, year): np.full(n, 1_000.0)
        for variable, year in situation_inputs.items()
    }
    for variable, year in branch_inputs.items():
        value = np.ones(n, dtype=bool) if variable == "tax_unit_itemizes" else 2_000.0
        parent.set_input(variable, year, np.broadcast_to(value, (n,)).copy())
        expected[(variable, year)] = np.broadcast_to(value, (n,))
    if head_input == "branch":
        parent.set_input("is_household_head", YEAR, heads)
    for variable, year in calculated:
        parent.calculate(variable, year)
    child = parent.get_branch("child")
    child.clear_calculated_results()
    for variable in MIXED_YEAR_INPUTS + [
        "tax_unit_itemizes",
        "income_tax",
        "income_tax_before_credits",
    ]:
        for year in YEARS:
            kept = child.get_array(variable, year)
            if (variable, year) in expected:
                np.testing.assert_array_equal(
                    kept, expected[(variable, year)], err_msg=f"{variable} {year}"
                )
            else:
                assert kept is None, f"calculated {variable} {year} was kept"
    # An eternal variable is stored once for every period.
    for year in YEARS:
        head = child.get_array("is_household_head", year)
        if head_input is None:
            assert head is None
        else:
            np.testing.assert_array_equal(head, heads)


def test_later_year_branches_match_single_year_simulation(households):
    years = (2025, YEAR)
    simulation = Simulation(situation=_situation(households, years=years))
    simulation.calculate("tax_liability_if_itemizing", 2025)
    simulation.calculate("income_tax", 2025)
    fresh = Simulation(situation=_situation(households, years=years))
    for variable in REPORTED + ["tax_liability_if_itemizing"]:
        np.testing.assert_array_equal(
            simulation.calculate(variable, YEAR),
            fresh.calculate(variable, YEAR),
            err_msg=f"{variable} for {YEAR} depends on 2025 being calculated first",
        )
    assert simulation.branches["itemizing"].branch_period.start.year == YEAR


def test_get_override_branch_reuses_within_period_and_recreates_otherwise(
    households,
):
    simulation = Simulation(situation=_situation(households, years=(2025, YEAR)))
    n = len(households)
    ones = np.ones(n, dtype=bool)
    first = get_override_branch(
        simulation, "test_branch", YEAR, {"tax_unit_itemizes": ones}
    )
    assert (
        get_override_branch(
            simulation, "test_branch", YEAR, {"tax_unit_itemizes": ones}
        )
        is first
    )
    other_inputs = get_override_branch(
        simulation, "test_branch", YEAR, {"tax_unit_itemizes": ~ones}
    )
    assert other_inputs is not first
    other_period = get_override_branch(
        simulation, "test_branch", 2025, {"tax_unit_itemizes": ones}
    )
    assert other_period is not other_inputs
    assert simulation.branches["test_branch"] is other_period


def test_get_branch_for_period_is_the_branch_without_inputs(households):
    simulation = Simulation(situation=_situation(households, years=(2025, YEAR)))
    # A branch of the same name that the helpers did not create is replaced.
    plain = simulation.get_branch("pinned_branch")
    first = get_branch_for_period(simulation, "pinned_branch", YEAR)
    assert first is not plain
    assert first.branch_period == period(YEAR)
    assert get_branch_for_period(simulation, "pinned_branch", YEAR) is first
    assert get_override_branch(simulation, "pinned_branch", YEAR, {}) is first
    later = get_branch_for_period(simulation, "pinned_branch", 2025)
    assert later is not first
    assert later.branch_period == period(2025)
    # Inside the branch itself, core's get_branch returns the simulation.
    assert get_branch_for_period(later, "pinned_branch", 2025) is later


def test_clear_calculated_results_keeps_inputs_only(households):
    n = len(households)
    itemizes = np.ones(n, dtype=bool)
    simulation = Simulation(situation=_situation(households))
    simulation.calculate("income_tax", YEAR)
    # A plain branch with an input of its own, and a branch nested in it.
    parent = simulation.get_branch("parent_with_input")
    parent.set_input("tax_unit_itemizes", YEAR, itemizes)
    child = parent.get_branch("child")
    child.clear_calculated_results()
    # Inputs survive: the situation's (its employment income is stored as
    # employment_income_before_lsr) and the one set on the parent branch.
    np.testing.assert_array_equal(
        child.get_array("employment_income_before_lsr", YEAR),
        simulation.get_array("employment_income_before_lsr", YEAR),
    )
    np.testing.assert_array_equal(child.get_array("tax_unit_itemizes", YEAR), itemizes)
    # Calculated values are gone, and are calculated again from the inputs.
    assert child.get_array("income_tax", YEAR) is None
    assert child.get_array("taxable_income", YEAR) is None
    np.testing.assert_allclose(
        child.calculate("taxable_income", YEAR),
        _fresh(households, "taxable_income", {"tax_unit_itemizes": itemizes}),
        atol=0.01,
    )

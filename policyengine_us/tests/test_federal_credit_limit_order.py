"""The federal non-refundable credits are applied in one order.

Each credit's own credit limit worksheet subtracts the credits that precede it
from income tax before credits. Read together, the 2013 to 2025 worksheets
give a single order (LEGAL_ORDER below, written from the worksheets and not
from the model's parameters):

- Form 2441, Credit Limit Worksheet: the foreign tax credit.
- Schedule R, Credit Limit Worksheet: Schedule 3 lines 1 and 2.
- Form 8863, Credit Limit Worksheet: Schedule 3 lines 1, 2 and 6d.
- Form 8880, Credit Limit Worksheet: Schedule 3 lines 1 through 3 and 6d.
- Form 5695, line 31 worksheet: those and Schedule 3 line 4.
- Form 8936, line 16: Schedule 3 lines 1 through 4, 5b and 6d.
- Form 8936, line 11: the same and line 6m.
- Schedule 8812, Credit Limit Worksheet A: lines 1 through 4, 5b, 6d, 6f, 6m.
- Form 5695, line 14 worksheet: every other credit, including the CTC.

These tests check that the parameters encode that order, and that the model's
credits match a direct sequential application of 26 U.S.C. 26(a) in that
order. The households take the standard deduction, so the CTC limit's no-SALT
liability equals actual liability.
"""

import numpy as np
import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from policyengine_us import CountryTaxBenefitSystem, Simulation
from policyengine_us.reforms.congress.afa.afa_other_dependent_credit import (
    create_afa_other_dependent_credit,
)
from policyengine_us.reforms.crfb.non_refundable_ss_credit import (
    non_refundable_ss_credit_reform,
)
from policyengine_us.tools.pinned_tbs import get_2020_irc_tbs

LEGAL_ORDER = [
    "foreign_tax_credit",
    "cdcc",
    "elderly_disabled_credit",
    "non_refundable_american_opportunity_credit",
    "lifetime_learning_credit",
    "savers_credit",
    "energy_efficient_home_improvement_credit",
    "used_clean_vehicle_credit",
    "new_clean_vehicle_credit",
    "non_refundable_ctc",
    "residential_clean_energy_credit",
]

# The parameter listing the credits that precede each credit. The foreign tax
# credit has none: its limit is the whole tax.
PRECEDING_CREDITS = {
    "cdcc": "cdcc.preceding_credits",
    "elderly_disabled_credit": "elderly_or_disabled.preceding_credits",
    "non_refundable_american_opportunity_credit": (
        "education.american_opportunity_credit.preceding_credits"
    ),
    "lifetime_learning_credit": "education.lifetime_learning_credit.preceding_credits",
    "savers_credit": "retirement_saving.preceding_credits",
    "energy_efficient_home_improvement_credit": (
        "energy_efficient_home_improvement.preceding_credits"
    ),
    "used_clean_vehicle_credit": "clean_vehicle.used.preceding_credits",
    "new_clean_vehicle_credit": "clean_vehicle.new.preceding_credits",
    "non_refundable_ctc": "ctc_tax_liability_limit.preceding_credits",
    "residential_clean_energy_credit": "residential_clean_energy.preceding_credits",
}

DATES = [
    "2013-01-01",
    "2017-06-01",
    "2020-06-01",
    "2021-06-01",
    "2022-06-01",
    "2023-06-01",
    "2025-06-01",
    "2026-06-01",
    "2035-06-01",
]


def credit_list(credits, path, date):
    node = credits
    for part in path.split("."):
        node = getattr(node, part)
    return list(node(date))


def expected_preceding(non_refundable, credit):
    before = non_refundable[: non_refundable.index(credit)]
    if credit == "residential_clean_energy_credit":
        # Its limit subtracts the CTC in the formula (Form 1040, line 19, or
        # Credit Limit Worksheet B, line 14), not through the list.
        before = [c for c in before if c != "non_refundable_ctc"]
    return before


@pytest.fixture(scope="module")
def baseline_system():
    return CountryTaxBenefitSystem()


@pytest.mark.parametrize("date", DATES)
def test_lists_follow_the_worksheet_order(baseline_system, date):
    credits = baseline_system.parameters.gov.irs.credits
    non_refundable = list(credits.non_refundable(date))
    assert non_refundable == [c for c in LEGAL_ORDER if c in non_refundable]
    assert non_refundable[0] == "foreign_tax_credit"
    for credit in non_refundable[1:]:
        assert credit in PRECEDING_CREDITS, f"{credit} has no preceding list"
        assert credit_list(
            credits, PRECEDING_CREDITS[credit], date
        ) == expected_preceding(non_refundable, credit), (credit, date)


def test_2020_irc_pin_keeps_the_order_in_2021(baseline_system):
    credits = get_2020_irc_tbs(baseline_system).parameters.gov.irs.credits
    date = "2021-06-01"
    non_refundable = list(credits.non_refundable(date))
    assert "cdcc" in non_refundable
    assert non_refundable == [c for c in LEGAL_ORDER if c in non_refundable]
    for credit in non_refundable[1:]:
        assert credit_list(
            credits, PRECEDING_CREDITS[credit], date
        ) == expected_preceding(non_refundable, credit), credit


@pytest.mark.parametrize(
    "reform, credit_before_25d",
    [
        (create_afa_other_dependent_credit(), "other_dependent_credit"),
        (non_refundable_ss_credit_reform(), "non_refundable_ctc"),
    ],
)
def test_reforms_order_the_ctc_and_25d_lists(reform, credit_before_25d):
    credits = reform(CountryTaxBenefitSystem()).parameters.gov.irs.credits
    date = "2026-06-01"
    non_refundable = list(credits.non_refundable(date))
    assert non_refundable[0] == "foreign_tax_credit"
    assert non_refundable[-2:] == [credit_before_25d, "residential_clean_energy_credit"]
    before_ctc = non_refundable[: non_refundable.index(credit_before_25d)]
    if credit_before_25d == "other_dependent_credit":
        # The separate credit for other dependents takes the CTC's place.
        before_ctc = before_ctc + ["other_dependent_credit"]
    for path in (
        "ctc_tax_liability_limit.preceding_credits",
        "residential_clean_energy.preceding_credits",
    ):
        assert credit_list(credits, path, date) == before_ctc, path


# Households with every modeled non-refundable credit at once. The potentials
# (each credit before its tax-liability limit) are inputs.
POTENTIALS = {
    "foreign_tax_credit": "foreign_tax_credit_potential",
    "cdcc": "cdcc_potential",
    "elderly_disabled_credit": "elderly_disabled_credit_potential",
    "non_refundable_american_opportunity_credit": (
        "non_refundable_american_opportunity_credit_potential"
    ),
    "lifetime_learning_credit": "lifetime_learning_credit_potential",
    "savers_credit": "savers_credit_potential",
    "energy_efficient_home_improvement_credit": (
        "energy_efficient_home_improvement_credit_potential"
    ),
    "used_clean_vehicle_credit": "used_clean_vehicle_credit_potential",
    "new_clean_vehicle_credit": "new_clean_vehicle_credit_potential",
}
ELIGIBILITY = {
    "used_clean_vehicle_credit": "used_clean_vehicle_credit_eligible",
    "new_clean_vehicle_credit": "new_clean_vehicle_credit_eligible",
}


def build_situation(households, year):
    people, tax_units, marital_units = {}, {}, {}
    groups = {"households": {}, "spm_units": {}, "families": {}}
    for i, h in enumerate(households):
        head = f"head_{i}"
        people[head] = {
            "age": {year: h["age"]},
            "employment_income": {year: h["wages"]},
            "taxable_interest_income": {year: h["interest"]},
        }
        members = [head]
        marital_units[f"marital_unit_{i}"] = {"members": [head]}
        if h["married"]:
            spouse = f"spouse_{i}"
            people[spouse] = {"age": {year: h["age"]}}
            members.append(spouse)
            marital_units[f"marital_unit_{i}"]["members"].append(spouse)
        for j, age in enumerate(h["dependent_ages"]):
            dependent = f"dependent_{i}_{j}"
            people[dependent] = {"age": {year: age}}
            members.append(dependent)
            marital_units[f"marital_unit_{i}_{j}"] = {"members": [dependent]}
        tax_unit = {
            "members": members,
            "solar_electric_property_expenditures": {year: h["solar"]},
        }
        for credit, potential in POTENTIALS.items():
            tax_unit[potential] = {year: h[credit]}
        for credit, eligible in ELIGIBILITY.items():
            tax_unit[eligible] = {year: h[credit] > 0}
        tax_units[f"tax_unit_{i}"] = tax_unit
        groups["households"][f"household_{i}"] = {
            "members": members,
            "state_code": {year: "TX"},
        }
        groups["spm_units"][f"spm_unit_{i}"] = {"members": members}
        groups["families"][f"family_{i}"] = {"members": members}
    return {
        "people": people,
        "tax_units": tax_units,
        "marital_units": marital_units,
        **groups,
    }


def check_households(households, year):
    simulation = Simulation(situation=build_situation(households, year))

    def calc(variable):
        return np.asarray(simulation.calculate(variable, year), dtype=float)

    credits = simulation.tax_benefit_system.parameters(year).gov.irs.credits
    non_refundable = list(credits.non_refundable)
    tax = calc("income_tax_before_credits")
    tol = 0.01

    # Apply 26(a) in the worksheet order: each credit is the smaller of its
    # potential and the tax the earlier credits leave.
    remaining = np.maximum(tax, 0)
    limited = {}
    for credit in LEGAL_ORDER:
        if credit not in non_refundable or credit not in POTENTIALS:
            continue
        potential = calc(POTENTIALS[credit])
        expected = np.minimum(potential, remaining)
        np.testing.assert_allclose(calc(credit), expected, atol=tol, err_msg=credit)
        limited[credit] = (expected > 0) & (expected < potential - tol)
        remaining = remaining - expected
    if "non_refundable_ctc" in non_refundable:
        # Schedule 8812 Credit Limit Worksheet A, line 3.
        np.testing.assert_allclose(
            calc("ctc_tax_liability_after_preceding_credits"), remaining, atol=tol
        )

    # The per-credit amounts add up to the capped total: no credit is allowed
    # tax that an earlier credit already used. non_refundable_ctc is the CTC
    # that is not refunded, before its tax limit (intended), so its applied
    # amount is the smaller of it and Credit Limit Worksheet A, line 5.
    applied = {credit: calc(credit) for credit in non_refundable}
    unused_ctc = 0
    if "non_refundable_ctc" in non_refundable:
        not_refunded = applied["non_refundable_ctc"]
        applied["non_refundable_ctc"] = np.minimum(
            not_refunded, calc("ctc_limiting_tax_liability")
        )
        unused_ctc = not_refunded - applied["non_refundable_ctc"]
    capped = calc("income_tax_capped_non_refundable_credits")
    np.testing.assert_allclose(sum(applied.values()), capped, atol=tol)
    assert (capped <= np.maximum(tax, 0) + tol).all()
    # The aggregate 26(a) cap removes only the unused CTC.
    np.testing.assert_allclose(
        calc("income_tax_unavailable_non_refundable_credits"), unused_ctc, atol=tol
    )
    return limited


credit_amount = st.one_of(st.just(0), st.integers(1, 5_000))
household_strategy = st.fixed_dictionaries(
    {
        "age": st.integers(25, 80),
        "married": st.booleans(),
        "dependent_ages": st.lists(st.integers(0, 18), max_size=3),
        "wages": st.integers(0, 150_000),
        "interest": st.integers(0, 60_000),
        "solar": st.one_of(st.just(0), st.integers(1, 30_000)),
        **{credit: credit_amount for credit in POTENTIALS},
    }
)

GRID = [
    {
        "age": 70,
        "married": married,
        "dependent_ages": ages,
        "wages": wages,
        "interest": 0,
        "solar": solar,
        **{credit: amount for credit in POTENTIALS},
    }
    for married in (True, False)
    for ages in ([], [5, 8], [17])
    for wages in (0, 25_000, 45_000, 80_000, 150_000)
    for solar in (0, 10_000)
    for amount in (0, 300, 2_000)
] + [
    # A wage ladder with 300 of every credit: tax rises by about 50 a step, so
    # it stops inside each credit's 300 slot in turn.
    {
        "age": 40,
        "married": False,
        "dependent_ages": [],
        "wages": wages,
        "interest": 0,
        "solar": 0,
        **{credit: 300 for credit in POTENTIALS},
    }
    for wages in range(12_000, 45_000, 500)
]


@pytest.mark.parametrize("year", [2018, 2021, 2025])
def test_grid_applies_credits_in_worksheet_order(year):
    limited = check_households(GRID, year)
    # The grid partly limits every credit, so each list binds.
    assert len(limited) >= 6
    for credit, partly_limited in limited.items():
        assert partly_limited.any(), credit


@settings(
    max_examples=10,
    deadline=None,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large],
)
@given(
    st.lists(household_strategy, min_size=1, max_size=20),
    st.sampled_from([2018, 2021, 2023, 2025, 2026]),
)
def test_random_households_apply_credits_in_worksheet_order(households, year):
    check_households(households, year)

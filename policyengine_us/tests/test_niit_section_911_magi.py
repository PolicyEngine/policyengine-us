"""Property and differential tests for the section 911 addition to NIIT MAGI.

26 U.S.C. 1411(d): "the term 'modified adjusted gross income' means adjusted
gross income increased by the excess of— (1) the amount excluded from gross
income under section 911(a)(1), over (2) the amount of any deductions (taken
into account in computing adjusted gross income) or exclusions disallowed
under section 911(d)(6) with respect to the amounts described in paragraph
(1)." The Form 8960 Line 13 MAGI Worksheet enters that excess on line 2c.

`niit_magi_section_911_addition` is that excess. It defaults to
`foreign_earned_income_exclusion` and can be entered directly, for a filer
whose exclusion includes housing amounts that section 1411(d) leaves out.

Properties that hold for every household:

1. Nothing added changes nothing, bit for bit. With no exclusion, or an
   entered addition of zero or less, AGI, `niit_magi`,
   `net_investment_income_tax` and income tax equal those of the formula
   before the section 911 addition (AGI plus the estate and trust code H
   change), run as a reform on the same households. A household without an
   exclusion also gets the same results whatever the other households in
   the batch exclude.
2. MAGI is AGI plus the positive code H change plus the addition, and the
   addition is the exclusion, or the entered amount, floored at zero.
3. MAGI and the tax never fall as the excluded amount rises.
4. The tax is 3.8% of the lesser of net investment income and the excess of
   MAGI over the threshold of section 1411(b) ($250,000 joint or surviving
   spouse, $125,000 separate, $200,000 otherwise, not indexed), computed
   here independently.

Households live in Texas.
"""

from functools import lru_cache

import numpy as np
import pytest

from policyengine_us import CountryTaxBenefitSystem, Simulation

# Hypothesis is a dev extra; skip rather than fail collection without it.
hypothesis = pytest.importorskip("hypothesis")
st = pytest.importorskip("hypothesis.strategies")

RATE = 0.038
THRESHOLD = {
    "SINGLE": 200_000,
    "HEAD_OF_HOUSEHOLD": 200_000,
    "JOINT": 250_000,
    "SEPARATE": 125_000,
    "SURVIVING_SPOUSE": 250_000,
}
STATUSES = list(THRESHOLD)
YEARS = [2018, 2022, 2025, 2026]

OUTPUTS = [
    "filing_status",
    "adjusted_gross_income",
    "foreign_earned_income_exclusion",
    "niit_magi_section_911_addition",
    "niit_magi",
    "net_investment_income",
    "net_investment_income_tax",
    "income_tax_before_refundable_credits",
    "income_tax",
]
# Every output other than the exclusion and the addition themselves, which
# the households set.
UNCHANGED_WITHOUT_EXCLUSION = [
    "adjusted_gross_income",
    "niit_magi",
    "net_investment_income",
    "net_investment_income_tax",
    "income_tax_before_refundable_credits",
    "income_tax",
]


def build_situation(households, year):
    people, tax_units, marital_units = {}, {}, {}
    groups = {"households": {}, "spm_units": {}, "families": {}}
    for i, h in enumerate(households):
        head = f"head_{i}"
        people[head] = {
            "age": {year: 45},
            "employment_income": {year: h["wages"]},
            "qualified_dividend_income": {year: h["qualified_dividends"]},
            "taxable_interest_income": {year: h["interest"]},
            "long_term_capital_gains": {year: h["long_term_gains"]},
            "estate_income": {year: h["estate_income"]},
            "estate_income_net_investment_income_adjustment": {year: h["code_h"]},
        }
        members = [head]
        marital_units[f"marital_unit_{i}"] = {"members": [head]}
        if h["status"] == "JOINT":
            spouse = f"spouse_{i}"
            people[spouse] = {
                "age": {year: 45},
                "employment_income": {year: h["spouse_wages"]},
            }
            members.append(spouse)
            marital_units[f"marital_unit_{i}"]["members"].append(spouse)
        if h["status"] == "HEAD_OF_HOUSEHOLD":
            child = f"child_{i}"
            people[child] = {"age": {year: 17}}
            members.append(child)
            marital_units[f"marital_unit_{i}_child"] = {"members": [child]}
        tax_unit = {
            "members": members,
            # Set for every tax unit: an input given to only some of them
            # leaves the rest at the default (single).
            "filing_status": {year: h["status"]},
            "foreign_earned_income_exclusion": {year: h["exclusion"]},
        }
        if h["entered_addition"] is not None:
            tax_unit["niit_magi_section_911_addition"] = {year: h["entered_addition"]}
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


def before_the_section_911_addition():
    """A reform restoring `niit_magi` as it was before this change."""
    from policyengine_core.reforms import Reform

    from policyengine_us.model_api import (
        USD,
        YEAR,
        TaxUnit,
        Variable,
    )

    class niit_magi(Variable):
        value_type = float
        entity = TaxUnit
        label = "NIIT MAGI before the section 911 addition"
        unit = USD
        definition_period = YEAR

        def formula(tax_unit, period, parameters):
            person = tax_unit.members
            not_dependent = ~person("is_tax_unit_dependent", period)
            estate_magi_adjustment = tax_unit.sum(
                not_dependent * person("estate_income_niit_magi_adjustment", period)
            )
            return tax_unit("adjusted_gross_income", period) + estate_magi_adjustment

    class reform(Reform):
        def apply(self):
            self.update_variable(niit_magi)

    return reform


@lru_cache(maxsize=None)
def system_before_the_section_911_addition():
    """Built once: constructing a reformed system takes seconds."""
    return CountryTaxBenefitSystem(reform=before_the_section_911_addition())


def calculate_batch(households, year, before):
    simulation = Simulation(
        situation=build_situation(households, year),
        **(
            {"tax_benefit_system": system_before_the_section_911_addition()}
            if before
            else {}
        ),
    )
    results = {}
    for v in OUTPUTS:
        values = simulation.calculate(v, year)
        results[v] = (
            values.decode_to_str() if v == "filing_status" else np.asarray(values)
        )
    return results


def calculate(households, year, before=False):
    """Households with and without an entered addition, as separate batches.

    An input given to only some tax units in a batch sets the rest to the
    default (zero), not to the value the formula would compute, so mixing
    them would hide the default.
    """
    entered = np.array([h["entered_addition"] is not None for h in households])
    results = {}
    for group in [entered, ~entered]:
        if not group.any():
            continue
        batch = calculate_batch(
            [h for h, g in zip(households, group) if g], year, before
        )
        for v, values in batch.items():
            if v not in results:
                results[v] = np.empty(len(households), dtype=values.dtype)
                if v == "filing_status":
                    results[v] = np.empty(len(households), dtype=object)
            results[v][group] = values
    return results


def with_exclusion(households, exclusion):
    """The same households with the exclusion replaced or transformed."""
    change = exclusion if callable(exclusion) else lambda _: exclusion
    return [{**h, "exclusion": change(h["exclusion"])} for h in households]


def tolerance(*amounts):
    """One cent, plus the rounding of single-precision arithmetic.

    The model stores amounts as 32-bit floats, which carry about seven
    significant digits.
    """
    return 0.01 + 5e-7 * np.max(np.abs(amounts), axis=0)


def expected_addition(household):
    entered = household["entered_addition"]
    amount = household["exclusion"] if entered is None else entered
    return max(0, amount)


def assert_invariants(households, year):
    law = calculate(households, year)
    before = calculate(households, year, before=True)
    unstacked = calculate(with_exclusion(households, 0), year)
    more_excluded = calculate(with_exclusion(households, lambda e: 1.5 * e + 500), year)
    assert list(law["filing_status"]) == [h["status"] for h in households]
    agi = law["adjusted_gross_income"]
    addition = np.array([expected_addition(h) for h in households])
    nothing_added = addition == 0

    # 1. Nothing excluded changes nothing, bit for bit: against the formula
    # before the section 911 addition, and against the same households in a
    # batch where no one excludes anything.
    for v in UNCHANGED_WITHOUT_EXCLUSION:
        assert np.array_equal(law[v][nothing_added], before[v][nothing_added]), v
    no_exclusion = np.array(
        [h["exclusion"] == 0 and h["entered_addition"] is None for h in households]
    )
    for v in OUTPUTS[1:]:
        assert np.array_equal(law[v][no_exclusion], unstacked[v][no_exclusion]), v
    assert not law["niit_magi_section_911_addition"][no_exclusion].any()

    # 2. MAGI is AGI plus the positive code H change plus the addition.
    code_h = np.array([max(0, h["code_h"]) for h in households])
    magi = agi + code_h + addition
    slack = tolerance(magi, law["niit_magi"])
    assert (np.abs(law["niit_magi"] - magi) <= slack).all()
    assert (np.abs(law["niit_magi"] - before["niit_magi"] - addition) <= slack).all()
    entered = np.array([h["entered_addition"] is not None for h in households])
    assert (
        np.abs(law["niit_magi_section_911_addition"][~entered] - addition[~entered])
        <= slack[~entered]
    ).all()

    # 3. MAGI and the tax never fall as the excluded amount rises. Rounding
    # is monotone, so this holds exactly.
    for v in ["niit_magi", "net_investment_income_tax"]:
        assert (more_excluded[v] >= law[v]).all(), v
        assert (law[v] >= unstacked[v]).all(), v

    # 4. The tax from the statute, computed independently of the model's
    # formula and parameters.
    threshold = np.array([THRESHOLD[h["status"]] for h in households])
    net_investment_income = law["net_investment_income"]
    niit = RATE * np.minimum(
        np.maximum(0, net_investment_income), np.maximum(0, magi - threshold)
    )
    assert (np.abs(law["net_investment_income_tax"] - niit) <= slack).all()
    assert (law["net_investment_income_tax"] >= 0).all()
    assert (
        law["net_investment_income_tax"]
        <= RATE * np.maximum(0, net_investment_income) + slack
    ).all()
    return law, before


def household(status, wages, exclusion, **amounts):
    return {
        "status": status,
        "wages": wages,
        "spouse_wages": amounts.get("spouse_wages", 0),
        "qualified_dividends": amounts.get("qualified_dividends", 0),
        "interest": amounts.get("interest", 0),
        "long_term_gains": amounts.get("long_term_gains", 0),
        "estate_income": amounts.get("estate_income", 0),
        "code_h": amounts.get("code_h", 0),
        "exclusion": exclusion,
        "entered_addition": amounts.get("entered_addition"),
    }


GRID = [
    household(
        status,
        wages,
        exclusion,
        spouse_wages=40_000 if status == "JOINT" else 0,
        qualified_dividends=dividends,
        long_term_gains=gains,
        estate_income=estate_income,
        code_h=code_h,
        entered_addition=entered,
    )
    for status in STATUSES
    for wages in (0, 120_000, 600_000)
    for dividends, gains in ((0, 0), (50_000, 0), (10_000, 120_000))
    for estate_income, code_h in ((0, 0), (12_000, 5_000))
    for exclusion in (0, 1, 60_000, 130_000, 260_000)
    for entered in (None, 40_000)
] + [
    # An entered negative amount, and an entered zero beside a positive
    # exclusion.
    household(
        "SINGLE", 150_000, 0, qualified_dividends=50_000, entered_addition=-5_000
    ),
    household(
        "SINGLE", 150_000, 100_000, qualified_dividends=50_000, entered_addition=0
    ),
]


@pytest.mark.parametrize("year", YEARS)
def test_grid_invariants(year):
    law, before = assert_invariants(GRID, year)
    # The grid reaches filers whose tax the addition raises and filers it
    # does not.
    raised = law["net_investment_income_tax"] > before["net_investment_income_tax"]
    assert raised.any()
    assert (~raised & (law["niit_magi_section_911_addition"] > 0)).any()


def test_review_example():
    # 2025, single, $150,000 of wages, $50,000 of qualified dividends and a
    # $100,000 section 911(a)(1) exclusion. MAGI is $300,000, $100,000 above
    # the threshold, so the tax is 3.8% of $50,000.
    example = household("SINGLE", 150_000, 100_000, qualified_dividends=50_000)
    law, before = assert_invariants([example], 2025)
    assert law["adjusted_gross_income"][0] == 200_000
    assert law["niit_magi"][0] == 300_000
    assert law["net_investment_income_tax"][0] == pytest.approx(1_900, abs=0.01)
    # Before the change, MAGI stayed at AGI and there was no tax.
    assert before["niit_magi"][0] == 200_000
    assert before["net_investment_income_tax"][0] == 0


household_strategy = st.fixed_dictionaries(
    {
        "status": st.sampled_from(STATUSES),
        "wages": st.integers(0, 900_000),
        "spouse_wages": st.one_of(st.just(0), st.integers(1, 400_000)),
        "qualified_dividends": st.one_of(st.just(0), st.integers(1, 300_000)),
        "interest": st.one_of(st.just(0), st.integers(1, 100_000)),
        "long_term_gains": st.one_of(st.just(0), st.integers(-50_000, 1_000_000)),
        "estate_income": st.one_of(st.just(0), st.integers(1, 100_000)),
        "code_h": st.one_of(st.just(0), st.integers(-50_000, 50_000)),
        "exclusion": st.one_of(st.just(0), st.integers(1, 300_000)),
        "entered_addition": st.one_of(
            st.none(), st.just(0), st.integers(-20_000, 300_000)
        ),
    }
)

SETTINGS = dict(
    max_examples=10,
    deadline=None,
    suppress_health_check=[
        hypothesis.HealthCheck.too_slow,
        hypothesis.HealthCheck.data_too_large,
    ],
)


@hypothesis.settings(**SETTINGS)
@hypothesis.given(
    st.lists(household_strategy, min_size=1, max_size=25),
    st.sampled_from(YEARS),
)
def test_random_households_keep_the_invariants(households, year):
    assert_invariants(households, year)

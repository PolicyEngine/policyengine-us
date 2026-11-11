"""Property and differential tests for strike and lockout benefits.

Publication 525 counts strike and lockout benefits a union pays as income
unless the facts clearly show the union meant them as gifts (IRC 102(a)).
Publication 596 makes the taxable benefits earned income for the EITC, and
Publication 503 for the child and dependent care credit. The model splits
strike_benefits into tax_exempt_strike_benefits (the gift part, an input) and
taxable_strike_benefits (the rest).

Hypothesis draws filers with wages, strike benefits, a gift share (above one
for a gift input larger than the benefits) and zero to three children, and an
adult dependent with its own wages, strike benefits and gift share. Each
example builds one 2025 simulation that holds every drawn household in several
variants:

- "base": the drawn wages W, strike benefits S and gift part G.
- "no_gift": W, max(0, S - G) of strike benefits and no gift part.
- "as_wages": W + max(0, S - G) of wages and no strike benefits.
- "state_base" and "state_split_free" in Utah, Montana and Arizona: no
  children, W + $60,000 of wages and S of strike benefits, and a full-time
  student dependent aged 20 with the drawn wages and strike benefits, with
  each person's gift part as drawn or none of it a gift.

Invariants, for every drawn household:

1. Split: taxable_strike_benefits = max(0, S - G), within [0, S].
2. Gross income: irs_gross_income = W + taxable_strike_benefits.
3. Gift neutrality (differential): the gift part enters federal income tax
   nowhere, so "base" and "no_gift" owe the same.
4. Wage parity (differential): with up to two children, federal income tax,
   the EITC and the refundable CTC are the same whether an amount comes as
   wages or as taxable strike benefits ("no_gift" against "as_wages"); the
   earned income each reads is the same too.
   Intended difference: with three or more children the refundable CTC can
   instead be the excess of social security taxes over the EITC (IRC
   24(d)(1)(B)(ii)); wages carry those taxes and strike benefits do not, so
   "as_wages" never owes more than "no_gift".
5. Counted once: Utah homeowner and renter relief household income (Utah Code
   59-2a-101(15), (17), (20)(a)(v)), Montana elderly homeowner/renter credit
   gross household income (MCA 15-30-2337(9)(a)(v)) and Arizona property tax
   credit household income (ARS 43-1072(H)(6)(c)) count every adult member's
   strike benefits once, the taxable part through adjusted gross income (an
   adult dependent's own) and the gift part, never more than the benefits, as
   nontaxable income, so the split leaves them unchanged and they equal the
   members' wages plus their whole strike benefits. Montana's measure also
   counts federal refundable credits, which move with adjusted gross income,
   so the state cases have $60,000 more wages, which keeps the EITC at zero
   in both (checked).
6. Personal services (differential): with alternative minimum taxable income
   held fixed, strike benefits change neither the kiddie tax support test nor
   the federal AMT child exemption cap (2017; IRC 59(j), 911(d)(2)), nor
   California's AMT child exemption (2025 Schedule P (540), Exemption
   Worksheet line 8), all of which count only payments for personal services.
"""

import numpy as np
from hypothesis import HealthCheck, Phase, given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation

YEAR = 2025

MONEY = st.sampled_from(["zero", "small", "large"]).flatmap(
    lambda size: {
        "zero": st.just(0.0),
        "small": st.floats(0, 15_000).map(lambda x: round(x, 2)),
        # Under $150,000 in all, far from the additional Medicare tax and
        # any other payroll threshold.
        "large": st.floats(15_000, 70_000).map(lambda x: round(x, 2)),
    }[size]
)

FILER = st.fixed_dictionaries(
    {
        "wages": MONEY,
        "strike": MONEY,
        "gift_share": st.sampled_from([0, 0, 0.5, 1, 1.5]),
        "children": st.integers(0, 3),
        "dependent_wages": MONEY,
        "dependent_strike": MONEY,
        "dependent_gift_share": st.sampled_from([0, 0.5, 1, 1.5]),
    }
)

FILERS = st.lists(FILER, min_size=4, max_size=6)

FEDERAL_VARIANTS = ["base", "no_gift", "as_wages"]
STATE_VARIANTS = ["state_base", "state_split_free"]
# Wages added in the state cases, enough to end the EITC of a head of
# household with one qualifying child (the dependent).
STATE_EXTRA_WAGES = 60_000
STATES = ["UT", "MT", "AZ"]


def _amounts(filer: dict, variant: str) -> dict:
    wages, strike = filer["wages"], filer["strike"]
    gift = round(strike * filer["gift_share"], 2)
    taxable = round(max(0.0, strike - gift), 2)
    if variant == "base":
        return {"employment_income": wages, "strike_benefits": strike, "gift": gift}
    if variant == "no_gift":
        return {
            "employment_income": wages,
            "strike_benefits": taxable,
            "gift": 0.0,
        }
    if variant == "as_wages":
        return {
            "employment_income": round(wages + taxable, 2),
            "strike_benefits": 0.0,
            "gift": 0.0,
        }
    if variant in STATE_VARIANTS:
        return {
            "employment_income": wages + STATE_EXTRA_WAGES,
            "strike_benefits": strike,
            "gift": gift if variant == "state_base" else 0.0,
        }
    raise ValueError(variant)


def _situation(filers: list) -> tuple:
    """One household per (filer, variant, state); returns the situation and
    the (filer index, variant, state) of each household in order."""
    year = str(YEAR)
    people, tax_units, households, index = {}, {}, {}, []
    cases = [(i, v, "TX") for i in range(len(filers)) for v in FEDERAL_VARIANTS]
    cases += [
        (i, v, s) for s in STATES for i in range(len(filers)) for v in STATE_VARIANTS
    ]
    for n, (i, variant, state) in enumerate(cases):
        filer = filers[i]
        amounts = _amounts(filer, variant)
        head = f"head_{n}"
        people[head] = {
            "age": {year: 40},
            "employment_income": {year: amounts["employment_income"]},
            "strike_benefits": {year: amounts["strike_benefits"]},
            "tax_exempt_strike_benefits": {year: amounts["gift"]},
        }
        members = [head]
        children = filer["children"] if state == "TX" else 0
        for c in range(children):
            child = f"child_{n}_{c}"
            people[child] = {"age": {year: 6 + c}}
            members.append(child)
        if state != "TX":
            strike = filer["dependent_strike"]
            gift = round(strike * filer["dependent_gift_share"], 2)
            people[f"dependent_{n}"] = {
                "age": {year: 20},
                "is_full_time_student": {year: True},
                # Without marital units every member shares the head's, which
                # would make this adult the spouse.
                "is_tax_unit_dependent": {year: True},
                "employment_income": {year: filer["dependent_wages"]},
                "strike_benefits": {year: strike},
                "tax_exempt_strike_benefits": {
                    year: gift if variant == "state_base" else 0.0
                },
            }
            members.append(f"dependent_{n}")
        tax_units[f"tax_unit_{n}"] = {
            "members": members,
            "filing_status": {
                year: "HEAD_OF_HOUSEHOLD" if len(members) > 1 else "SINGLE"
            },
        }
        households[f"household_{n}"] = {
            "members": members,
            "state_code": {year: state},
        }
        index.append((i, variant, state))
    situation = {"people": people, "tax_units": tax_units, "households": households}
    return situation, index


@settings(
    max_examples=5,
    deadline=None,
    derandomize=True,
    database=None,
    # Each example builds one large simulation, so shrinking a failure would
    # take many minutes; the failing draw is reported unshrunk.
    phases=[Phase.explicit, Phase.reuse, Phase.generate],
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large],
)
@given(filers=FILERS)
def test_strike_benefit_invariants(filers):
    situation, index = _situation(filers)
    sim = Simulation(situation=situation)
    position = {case: n for n, case in enumerate(index)}

    heads = sim.calculate("is_tax_unit_head", YEAR).astype(bool)

    def value(variable, i, variant, state="TX", household_total=False):
        # Each case has one tax unit, one household and one head, in case
        # order; a person-level variable is read for the head, or summed
        # over the household when household_total is set.
        if household_total:
            values = sim.calculate(variable, YEAR, map_to="household")
        else:
            values = sim.calculate(variable, YEAR)
            if sim.tax_benefit_system.variables[variable].entity.key == "person":
                values = values[heads]
        return values[position[(i, variant, state)]]

    for i, filer in enumerate(filers):
        wages, strike = filer["wages"], filer["strike"]
        gift = round(strike * filer["gift_share"], 2)
        taxable = max(0.0, strike - gift)

        # 1. Split.
        split = value("taxable_strike_benefits", i, "base")
        assert abs(split - taxable) < 0.01
        assert -0.01 <= split <= strike + 0.01

        # 2. Gross income.
        assert abs(value("irs_gross_income", i, "base") - (wages + taxable)) < 0.01

        # 3. Gift neutrality.
        for variable in ["income_tax", "adjusted_gross_income", "eitc"]:
            assert (
                abs(value(variable, i, "base") - value(variable, i, "no_gift")) < 0.01
            ), variable

        # 4. Wage parity.
        for variable in ["eitc_earned_income", "adjusted_gross_income"]:
            assert (
                abs(value(variable, i, "no_gift") - value(variable, i, "as_wages"))
                < 0.01
            ), variable
        assert (
            abs(
                value("adjusted_earnings", i, "no_gift")
                - value("adjusted_earnings", i, "as_wages")
            )
            < 0.01
        )
        if filer["children"] <= 2:
            for variable in ["income_tax", "eitc", "refundable_ctc"]:
                assert (
                    abs(value(variable, i, "no_gift") - value(variable, i, "as_wages"))
                    < 0.01
                ), variable
        else:
            assert (
                value("income_tax", i, "as_wages")
                <= value("income_tax", i, "no_gift") + 0.01
            )

        # 5. Counted once.
        for state, variable in [
            ("UT", "ut_homeowner_renter_relief_household_income"),
            ("MT", "mt_elderly_homeowner_or_renter_credit_gross_household_income"),
            ("AZ", "az_property_tax_credit_household_income"),
        ]:
            for variant in STATE_VARIANTS:
                assert value("eitc", i, variant, state) == 0
            # Montana's measure is per person, and Montana's net household
            # income sums it over the household, so the test sums it too.
            base = value(variable, i, "state_base", state, household_total=True)
            split_free = value(
                variable, i, "state_split_free", state, household_total=True
            )
            # float32 sums carry about 1e-7 of relative error.
            tolerance = max(0.01, 1e-6 * abs(base))
            assert abs(base - split_free) < tolerance, (state, base, split_free)
            # The measure holds both people's whole amounts, not just the
            # taxable parts, and nothing else: the drawn households have no
            # other income, and the extra wages keep every refundable credit
            # Montana counts at zero.
            total = (
                wages
                + STATE_EXTRA_WAGES
                + strike
                + filer["dependent_wages"]
                + filer["dependent_strike"]
            )
            assert abs(base - total) < tolerance, (state, base, total)
            # The dependent is a dependent, so their income is not in the
            # head's adjusted gross income.
            agi = value("adjusted_gross_income", i, "state_split_free", state)
            assert agi <= wages + STATE_EXTRA_WAGES + strike + tolerance, agi


CHILD = st.fixed_dictionaries(
    {
        "wages": MONEY,
        "strike": MONEY,
        "gift_share": st.sampled_from([0, 0.5, 1.5]),
        # Under 18; under 24 and a full-time student; or 19 and not a student,
        # who is outside the kiddie tax.
        "age": st.sampled_from([(16, False), (20, True), (19, False)]),
        "support": st.sampled_from([0, 10_000, 40_000]),
    }
)


def _child_situation(children: list, year: int, state: str) -> dict:
    """Two single-person tax units per drawn child, with and without the
    strike benefits, in the given year and state."""
    people, tax_units, households = {}, {}, {}
    y = str(year)
    for i, child in enumerate(children):
        age, student = child["age"]
        gift = round(child["strike"] * child["gift_share"], 2)
        for variant, strike in [("with", child["strike"]), ("without", 0.0)]:
            name = f"{variant}_{i}"
            people[name] = {
                "age": {y: age},
                "is_full_time_student": {y: student},
                "is_qualifying_child_dependent": {y: True},
                "employment_income": {y: child["wages"]},
                "strike_benefits": {y: strike},
                "tax_exempt_strike_benefits": {y: gift if strike else 0.0},
                "care_and_support_costs": {y: child["support"]},
            }
            tax_units[f"unit_{name}"] = {
                "members": [name],
                "filing_status": {y: "SINGLE"},
                # Held fixed, so only the earned income measures can differ.
                "amt_income": {y: 50_000},
                "ca_amti": {y: 50_000},
            }
            households[f"home_{name}"] = {
                "members": [name],
                "state_code": {y: state},
            }
    return {"people": people, "tax_units": tax_units, "households": households}


@settings(
    max_examples=5,
    deadline=None,
    derandomize=True,
    database=None,
    phases=[Phase.explicit, Phase.reuse, Phase.generate],
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large],
)
@given(children=st.lists(CHILD, min_size=4, max_size=6))
def test_strike_benefits_are_not_pay_for_personal_services(children):
    for year, state, variables in [
        (2017, "TX", ["amt_kiddie_tax_applies", "amt_exemption"]),
        (2025, "CA", ["ca_amt_exemption"]),
    ]:
        sim = Simulation(situation=_child_situation(children, year, state))
        for variable in variables:
            values = sim.calculate(variable, year)
            # Tax units alternate with and without strike benefits.
            assert np.allclose(values[0::2], values[1::2], atol=0.01), (
                year,
                variable,
                values,
            )

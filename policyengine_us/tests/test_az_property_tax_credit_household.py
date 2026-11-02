"""Property tests for Arizona property tax credit household income and claimant.

ARS 43-1072(H)(4) defines the household as "the household of the claimant and
such other persons as resided with the claimant in the claimant's homestead",
and (H)(5) household income as "all income received by all persons of a
household". A.A.C. R15-2C-502(A)(2) counts any person residing with the
claimant "whether or not the person is related to, or a dependent of, the
claimant". ARS 43-1072(G) allows "only one claimant per household per year".
Subsection (I) excludes Arizona unemployment insurance payments; Form 140PTC
line I counts other states' payments and tax-exempt strike benefits, and line
H all alimony received.

Hypothesis draws Arizona homes of one to three tax units, each with a head, an
optional spouse and an optional dependent, and with wages, Arizona and
other-state unemployment, strike benefits, alimony (taxable or not), rent and
property tax. Each example builds one simulation that holds the drawn homes
and the variants the properties compare them with, so few simulations run:

1. Every tax unit in a home sees the same household income, the sum of the
   tax units' own amounts, and each eligible unit's claim is the schedule
   amount at that income (Table 2 in a home of two or more), limited to the
   unit's own property taxes paid.
2. At most one tax unit per home has a positive credit.
3. The claimant's credit is at least what any other eligible tax unit in the
   home would get as claimant.
4. In a one-tax-unit home, household income equals the tax unit's income
   before this change (federal AGI plus dependents' gross income, here wages,
   all unemployment and taxable alimony), plus strike benefits and nontaxable
   alimony, minus Arizona unemployment. Other-state unemployment was already
   in the earlier income, as part of all unemployment, so it stays.
5. Raising a co-resident's wages never raises the home's total credit. Every
   member of a home of two or more lives with others and uses Table 2, which
   never rises with income (checked first).
6. Arizona unemployment never changes household income; other-state
   unemployment changes it dollar for dollar.
7. Changing any federal above-the-line deduction other than loss_ald,
   supplied as an input, never changes az_property_tax_credit_income
   (ruling us-az:ptc-above-the-line-deductions: A.A.C. R15-2C-502(A)(1)
   counts "the sum of all income not specifically excluded in A.R.S.
   § 43-1072", and Form 140PTC lines A to I subtract no adjustment). Federal
   AGI is checked to move, so the property is not vacuous.
"""

import numpy as np
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation

YEAR = 2025
# Form 140PTC line 13 for renters, modeled as
# gov.states.az.tax.income.credits.property_tax.rent_property_tax_rate.
RENT_PROPERTY_TAX_RATE = 0.15

# Most draws are zero or small, so that household income often stays under
# Table 2's $5,500 limit and credits are positive; some wages are large.
MONEY = st.sampled_from(["zero", "zero", "small", "large"]).flatmap(
    lambda size: {
        "zero": st.just(0.0),
        "small": st.floats(0, 2_000).map(lambda x: round(x, 2)),
        "large": st.floats(2_000, 40_000).map(lambda x: round(x, 2)),
    }[size]
)
SMALL = st.sampled_from([True, True, False]).flatmap(
    lambda zero: st.just(0.0) if zero else st.floats(0, 800).map(lambda x: round(x, 2))
)


@st.composite
def _person(draw, adult: bool) -> dict:
    unemployment = draw(SMALL)
    return {
        "age": draw(st.integers(60, 85) if adult else st.integers(5, 17)),
        "employment_income": draw(MONEY if adult else SMALL),
        "unemployment_compensation": unemployment,
        # The other-state part of the person's unemployment compensation.
        "az_other_state_unemployment_compensation": round(
            unemployment * draw(st.sampled_from([0, 0.5, 1])), 2
        ),
        "strike_benefits": draw(SMALL),
        "alimony_income": draw(SMALL),
        # 2010 is before the TCJA cutoff (taxable), 2020 after it (not).
        "divorce_year": draw(st.sampled_from([2010, 2020])),
    }


@st.composite
def _tax_unit(draw) -> dict:
    members = [("head", draw(_person(adult=True)))]
    if draw(st.booleans()):
        members.append(("spouse", draw(_person(adult=True))))
    if draw(st.integers(0, 3)) == 0:
        dependent = draw(_person(adult=False))
        dependent["is_tax_unit_dependent"] = True
        members.append(("dependent", dependent))
    return {
        "members": members,
        "rent": draw(st.sampled_from([0.0, 2_000.0, 6_000.0, 12_000.0])),
        "real_estate_taxes": draw(st.sampled_from([0.0, 0.0, 300.0, 1_000.0])),
    }


HOMES = st.lists(
    st.lists(_tax_unit(), min_size=1, max_size=3),
    min_size=4,
    max_size=6,
)


def _situation(homes: list) -> tuple:
    """A situation with one household per home, and the tax unit index of
    each household's tax units."""
    year = str(YEAR)
    people, tax_units, households = {}, {}, {}
    unit_home = []
    for h, home in enumerate(homes):
        home_members = []
        for u, unit in enumerate(home):
            names = []
            for role, values in unit["members"]:
                name = f"{role}_{h}_{u}"
                person = {k: {year: v} for k, v in values.items()}
                if role == "head":
                    person["rent"] = {year: unit["rent"]}
                    person["real_estate_taxes"] = {year: unit["real_estate_taxes"]}
                people[name] = person
                names.append(name)
            tax_units[f"tax_unit_{h}_{u}"] = {"members": names}
            unit_home.append(h)
            home_members += names
        households[f"household_{h}"] = {
            "members": home_members,
            "state_code": {year: "AZ"},
        }
    situation = {"people": people, "tax_units": tax_units, "households": households}
    return situation, np.array(unit_home)


def _changed(homes: list, change) -> list:
    """A deep copy of homes with change(person_values) applied to the first
    adult of the last tax unit of each home."""
    copied = [
        [
            {**unit, "members": [(r, dict(v)) for r, v in unit["members"]]}
            for unit in home
        ]
        for home in homes
    ]
    for home in copied:
        change(home[-1]["members"][0][1])
    return copied


def _reference_unit_income(unit: dict) -> float:
    """The tax unit's income before this change: wages, all unemployment and
    taxable alimony of every member (federal AGI for the filers, gross income
    for a dependent; no other income or deductions are drawn)."""
    return sum(
        v["employment_income"]
        + v["unemployment_compensation"]
        + (v["alimony_income"] if v["divorce_year"] < 2019 else 0)
        for _, v in unit["members"]
    )


def _added(unit: dict) -> float:
    """Strike benefits and nontaxable alimony."""
    return sum(
        v["strike_benefits"] + (v["alimony_income"] if v["divorce_year"] >= 2019 else 0)
        for _, v in unit["members"]
    )


def test_table_amounts_never_rise_with_income():
    from policyengine_us.system import system

    p = system.parameters(YEAR).gov.states.az.tax.income.credits.property_tax
    for table in [p.amount.living_alone, p.amount.cohabitating]:
        amounts = list(table.amounts)
        assert all(a >= b for a, b in zip(amounts, amounts[1:]))


@settings(
    max_examples=6,
    deadline=None,
    derandomize=True,
    database=None,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large],
)
@given(homes=HOMES, raise_by=st.floats(1, 20_000), uc=st.floats(1, 3_000))
def test_household_income_and_one_claimant(homes, raise_by, uc):
    raise_by, uc = round(raise_by, 2), round(uc, 2)

    def raise_wages(v):
        v["employment_income"] = round(v["employment_income"] + raise_by, 2)

    def add_arizona_uc(v):
        v["unemployment_compensation"] = round(v["unemployment_compensation"] + uc, 2)

    def add_other_state_uc(v):
        add_arizona_uc(v)
        v["az_other_state_unemployment_compensation"] = round(
            v["az_other_state_unemployment_compensation"] + uc, 2
        )

    variants = [
        homes,
        _changed(homes, raise_wages),
        _changed(homes, add_arizona_uc),
        _changed(homes, add_other_state_uc),
    ]
    n = len(homes)
    situation, unit_home = _situation([home for v in variants for home in v])
    sim = Simulation(situation=situation)
    unit_income = sim.calculate("az_property_tax_credit_income", YEAR)
    household_income = sim.calculate("az_property_tax_credit_household_income", YEAR)
    # The household income each tax unit reads, as
    # az_property_tax_credit_potential reads it.
    seen_income = sim.populations["tax_unit"].household(
        "az_property_tax_credit_household_income", YEAR
    )
    credit = sim.calculate("az_property_tax_credit", YEAR)
    potential = sim.calculate("az_property_tax_credit_potential", YEAR)
    eligible = sim.calculate("az_property_tax_credit_eligible", YEAR)
    total_credit = np.bincount(unit_home, weights=credit, minlength=4 * n)

    # 1. Each home's income is the sum of its tax units' amounts, and every
    # tax unit in the home sees it.
    np.testing.assert_allclose(
        household_income,
        np.bincount(unit_home, weights=unit_income, minlength=4 * n),
        atol=0.01,
    )
    np.testing.assert_allclose(seen_income, household_income[unit_home], atol=0.01)
    # Each eligible tax unit's claim is the lesser of its property taxes paid
    # and the schedule amount at the home's income, floored at zero: Table 2
    # for every unit in a home of two or more people, Table 1 otherwise.
    from policyengine_us.system import system

    p = system.parameters(YEAR).gov.states.az.tax.income.credits.property_tax
    all_units = [unit for v in variants for home in v for unit in home]
    home_size = np.bincount(
        unit_home,
        weights=[len(unit["members"]) for unit in all_units],
        minlength=4 * n,
    )[unit_home]
    schedule_income = np.maximum(household_income[unit_home], 0)
    table = np.where(
        home_size > 1,
        p.amount.cohabitating.calc(schedule_income),
        p.amount.living_alone.calc(schedule_income),
    )
    taxes_paid = np.array(
        [
            unit["real_estate_taxes"] + RENT_PROPERTY_TAX_RATE * unit["rent"]
            for unit in all_units
        ]
    )
    np.testing.assert_allclose(
        potential[eligible], np.minimum(table, taxes_paid)[eligible], atol=0.01
    )

    for h in range(4 * n):
        in_home = unit_home == h
        # 2. At most one tax unit per home has a positive credit.
        assert (credit[in_home] > 0).sum() <= 1
        # 3. The claimant's credit is the largest eligible claim.
        if eligible[in_home].any():
            assert credit[in_home].max() >= potential[in_home & eligible].max() - 0.01

    base = slice(0, n)
    base_units = [unit for home in homes for unit in home]
    base_unit_home = unit_home[unit_home < n]
    # 4. One-tax-unit homes: the earlier income plus the added items, less
    # Arizona unemployment (the drawn unemployment less its other-state part).
    for h, home in enumerate(homes):
        if len(home) == 1:
            unit = home[0]
            arizona_uc = sum(
                v["unemployment_compensation"]
                - v["az_other_state_unemployment_compensation"]
                for _, v in unit["members"]
            )
            expected = _reference_unit_income(unit) + _added(unit) - arizona_uc
            assert abs(household_income[h] - expected) < 0.01
            # The reference matches the model's federal AGI for the filers.
            filers = sum(
                v["employment_income"]
                + v["unemployment_compensation"]
                + (v["alimony_income"] if v["divorce_year"] < 2019 else 0)
                for r, v in unit["members"]
                if r != "dependent"
            )
            unit_index = base_units.index(unit)
            agi = sim.calculate("adjusted_gross_income", YEAR)[unit_index]
            assert abs(agi - filers) < 0.01
    assert len(base_unit_home) == len(base_units)

    # 5. Raising a co-resident's wages never raises a shared home's credit.
    shared = np.array([sum(len(u["members"]) for u in home) > 1 for home in homes])
    raised = slice(n, 2 * n)
    assert (total_credit[raised][shared] <= total_credit[base][shared] + 0.01).all()

    # 6. Arizona unemployment leaves household income unchanged; other-state
    # unemployment raises it dollar for dollar.
    np.testing.assert_allclose(
        household_income[2 * n : 3 * n], household_income[base], atol=0.01
    )
    np.testing.assert_allclose(
        household_income[3 * n : 4 * n], household_income[base] + uc, atol=0.01
    )


@settings(
    max_examples=4,
    deadline=None,
    derandomize=True,
    database=None,
    suppress_health_check=[HealthCheck.too_slow],
)
@given(
    wages=st.floats(0, 30_000),
    self_employment=st.floats(-5_000, 30_000),
    social_security=st.sampled_from([0.0, 12_000.0, 30_000.0]),
    dependent_wages=st.sampled_from([0.0, 3_000.0]),
    amount=st.floats(1, 5_000),
)
def test_above_the_line_deductions_do_not_change_income(
    wages, self_employment, social_security, dependent_wages, amount
):
    from policyengine_us.system import system

    p = system.parameters(YEAR).gov.irs.ald
    deductions = [d for d in p.deductions if d != "loss_ald"]
    year = str(YEAR)
    amount = round(amount, 2)
    people, tax_units, households = {}, {}, {}
    # Variant 0 is the base; variant i + 1 supplies deductions[i] as an input.
    # Every variant supplies every listed deduction, at zero unless varied, so
    # the base and the variant differ only in that one input.
    for i in range(len(deductions) + 1):
        varied = deductions[i - 1] if i else None
        head = {
            "age": {year: 70},
            "employment_income": {year: round(wages, 2)},
            "self_employment_income": {year: round(self_employment, 2)},
            "social_security": {year: social_security},
        }
        dependent = {
            "age": {year: 15},
            "is_tax_unit_dependent": {year: True},
            "employment_income": {year: dependent_wages},
        }
        unit = {"members": [f"head_{i}", f"dependent_{i}"]}
        for deduction in deductions:
            value = amount if deduction == varied else 0.0
            if system.variables[deduction].entity.key == "person":
                # On the dependent as well: federal AGI subtracts it only
                # for filer amounts recorded on a dependent, and the add-back
                # must match either way.
                head[deduction] = {year: value}
                dependent[deduction] = {year: value}
            else:
                unit[deduction] = {year: value}
        people[f"head_{i}"] = head
        people[f"dependent_{i}"] = dependent
        tax_units[f"tax_unit_{i}"] = unit
        households[f"household_{i}"] = {
            "members": [f"head_{i}", f"dependent_{i}"],
            "state_code": {year: "AZ"},
        }
    sim = Simulation(
        situation={"people": people, "tax_units": tax_units, "households": households}
    )
    income = sim.calculate("az_property_tax_credit_income", YEAR)
    agi = sim.calculate("adjusted_gross_income", YEAR)
    for i, deduction in enumerate(deductions, start=1):
        assert abs(income[i] - income[0]) < 0.01, deduction
        # Federal AGI moves, so the add-back is what keeps income still.
        assert agi[i] < agi[0] - 0.01, deduction

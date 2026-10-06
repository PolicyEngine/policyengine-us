"""Sampled property tests for Arizona property tax credit household income.

ARS 43-1072(H)(6) defines income for the credit, and A.A.C. R15-2C-502 and the
Form 140PTC instructions (2021-2025, page 4) apply it line by line: line D is
each member's gains and losses from the sale or exchange of property, combined,
with a net loss limited to $1,500 for each member. Federal AGI already holds
those gains, so az_property_tax_credit_income must count each dollar of gain
once. It used to add capital_gains_excluded_from_taxable_income as well, which
is the part of federal taxable income taxed at the capital gains rates (at zero
taxable income, the adjusted net capital gain), so gains and qualified dividends
counted twice. Federal AGI leaves out dependents' income, which Arizona counts
for every household member whether or not a dependent. Federal AGI also limits
a net capital loss to $3,000 per return rather than $1,500 per member, so line D
replaces its capital gains and losses. Household income (line J) can be
negative; the 2023-2025 instructions (page 5) then consider it zero for the
Schedule 1 and 2 amounts.

Invariants, checked on a seeded sample of Arizona tax units (some with a child
dependent who has income) whose members' net capital gains run from well below
-$1,500 to large gains, including units whose line J is negative:

1. Differential: the model equals an independent line A + B + D + E + F sum
   over every member from Form 140PTC Part 1, with Social Security excluded,
   rental losses netted (A.A.C. R15-2C-502(C)(2)) and each member's line D,
   capital gain distributions included, floored at -$1,500.
2. Counted once: adding d to a member's long-term gains changes household
   income by exactly the change in that member's line D, which is d when the
   member's net gain stays at or above -$1,500. The credit never rises.
3. Loss limit: lowering a member's gains changes household income by the
   change in that member's line D, which is 0 once the member's net gain is at
   or below -$1,500.
4. Schedule floor: the credit depends on line J only through max(line J, 0),
   so a negative line J gets the zero-income schedule amount.
5. The income does not depend on capital_gains_excluded_from_taxable_income.
"""

import numpy as np

from policyengine_us import Simulation

YEAR = 2025
N = 80
SEED = 43_1072
# A.A.C. R15-2C-502(C)(3): net capital losses are limited to $1,500 for each
# household member.
MEMBER_LOSS_LIMIT = 1_500
# Form 140PTC line 13 for renters: rent times the property tax factor,
# modeled as gov.states.az.tax.income.credits.property_tax.rent_property_tax_rate.
RENT_PROPERTY_TAX_RATE = 0.15


def _capital_gains(rng: np.random.Generator, can_be_large: bool) -> tuple:
    """Long- and short-term gains for one member."""
    draw = rng.random()
    if draw < 0.3:
        return 0.0, 0.0
    if draw < 0.55:
        # A net loss beyond the $1,500 member limit, some beyond federal AGI's
        # $3,000 per-return limit too.
        return (
            round(rng.uniform(-9_000, -1_600), 2),
            round(rng.uniform(-1_000, 500), 2),
        )
    # Some large gains, so federal taxable income is positive.
    large_gain = (
        round(rng.uniform(20_000, 80_000), 2)
        if can_be_large and rng.random() < 0.15
        else 0
    )
    return (
        round(rng.uniform(-1_000, 6_000), 2) + large_gain,
        round(rng.uniform(-500, 2_000), 2),
    )


def _distributions(rng: np.random.Generator) -> float:
    """Capital gain distributions reported without Schedule D, for some members."""
    return round(rng.uniform(0, 800), 2) if rng.random() < 0.25 else 0.0


def _rental_income(rng: np.random.Generator) -> float:
    """Net rent and royalty income or loss (Form 140PTC line F), for some members."""
    return round(rng.uniform(-3_000, 3_000), 2) if rng.random() < 0.2 else 0.0


def _sample_units(rng: np.random.Generator) -> list:
    units = []
    for _ in range(N):
        married = rng.random() < 0.4
        members = []
        for role in ["head", "spouse"] if married else ["head"]:
            long_term, short_term = _capital_gains(rng, can_be_large=True)
            members.append(
                {
                    "role": role,
                    "age": int(rng.integers(65, 86)),
                    "employment_income": float(
                        rng.choice([0, round(rng.uniform(0, 6_000), 2)])
                    ),
                    "taxable_interest_income": round(rng.uniform(0, 800), 2),
                    "tax_exempt_interest_income": round(rng.uniform(0, 500), 2),
                    "qualified_dividend_income": round(rng.uniform(0, 1_500), 2),
                    "long_term_capital_gains": long_term,
                    "short_term_capital_gains": short_term,
                    "non_sch_d_capital_gains": _distributions(rng),
                    "rental_income": _rental_income(rng),
                    "taxable_private_pension_income": float(
                        rng.choice([0, round(rng.uniform(0, 3_000), 2)])
                    ),
                    "tax_exempt_public_pension_income": float(
                        rng.choice([0, round(rng.uniform(0, 3_000), 2)])
                    ),
                    "social_security_retirement": float(
                        rng.choice([0, round(rng.uniform(0, 30_000), 2)])
                    ),
                }
            )
        if rng.random() < 0.35:
            # A child dependent with income of their own, including net
            # capital losses, which count up to the dependent's own limit.
            long_term, short_term = _capital_gains(rng, can_be_large=False)
            members.append(
                {
                    "role": "dependent",
                    "age": int(rng.integers(5, 18)),
                    "is_tax_unit_dependent": True,
                    "employment_income": float(
                        rng.choice([0, round(rng.uniform(0, 4_000), 2)])
                    ),
                    "taxable_interest_income": round(rng.uniform(0, 300), 2),
                    "tax_exempt_interest_income": round(rng.uniform(0, 200), 2),
                    "qualified_dividend_income": round(rng.uniform(0, 1_500), 2),
                    "long_term_capital_gains": long_term,
                    "short_term_capital_gains": short_term,
                    "non_sch_d_capital_gains": _distributions(rng),
                    "rental_income": _rental_income(rng),
                    "taxable_private_pension_income": 0.0,
                    "tax_exempt_public_pension_income": 0.0,
                    "social_security_survivors": float(
                        rng.choice([0, round(rng.uniform(0, 8_000), 2)])
                    ),
                }
            )
        if rng.random() < 0.15:
            # Little income besides a capital loss and a small tax-exempt
            # pension, so line J can be negative (2023-2025 instructions,
            # page 5, line J note).
            for member in members:
                for key in [
                    "employment_income",
                    "taxable_interest_income",
                    "qualified_dividend_income",
                    "non_sch_d_capital_gains",
                    "rental_income",
                    "taxable_private_pension_income",
                ]:
                    member[key] = 0.0
                member["tax_exempt_interest_income"] = round(rng.uniform(0, 200), 2)
            members[0]["long_term_capital_gains"] = round(
                rng.uniform(-6_000, -1_000), 2
            )
            members[0]["tax_exempt_public_pension_income"] = round(
                rng.uniform(0, 1_500), 2
            )
        units.append(
            {
                "members": members,
                "rent": round(rng.uniform(1_000, 12_000), 2),
                "gain_change": round(rng.uniform(1, 5_000), 2),
            }
        )
    return units


def _with_head_gains_changed(units: list, sign: int) -> list:
    changed = []
    for unit in units:
        members = [dict(m) for m in unit["members"]]
        members[0]["long_term_capital_gains"] = round(
            members[0]["long_term_capital_gains"] + sign * unit["gain_change"], 2
        )
        changed.append({**unit, "members": members})
    return changed


def _situation(units: list) -> dict:
    people, tax_units, households = {}, {}, {}
    year = str(YEAR)
    for i, unit in enumerate(units):
        names = []
        for member in unit["members"]:
            name = f"{member['role']}_{i}"
            names.append(name)
            person = {
                key: {year: value} for key, value in member.items() if key != "role"
            }
            if member["role"] == "head":
                person["rent"] = {year: unit["rent"]}
            people[name] = person
        tax_units[f"tax_unit_{i}"] = {"members": names}
        households[f"household_{i}"] = {
            "members": names,
            "state_code": {year: "AZ"},
        }
    return {"people": people, "tax_units": tax_units, "households": households}


def _net_gain(member: dict) -> float:
    # Capital gain distributions are long-term capital gains (26 U.S.C.
    # 852(b)(3)(B)), combined with the member's other gains and losses.
    return (
        member["long_term_capital_gains"]
        + member["short_term_capital_gains"]
        + member["non_sch_d_capital_gains"]
    )


def _line_d(member: dict) -> float:
    """Form 140PTC line D for one member: a net loss is limited to (1,500)."""
    return max(_net_gain(member), -MEMBER_LOSS_LIMIT)


def _form_140ptc_line_j(units: list) -> np.ndarray:
    """Form 140PTC Part 1 line J from the line A to I instructions."""
    totals = []
    for unit in units:
        total = 0.0
        for m in unit["members"]:
            line_a = m["employment_income"]
            line_b = (
                m["taxable_interest_income"]
                + m["tax_exempt_interest_income"]
                + m["qualified_dividend_income"]
            )
            line_e = (
                m["taxable_private_pension_income"]
                + m["tax_exempt_public_pension_income"]
            )
            # A rental loss counts in full (A.A.C. R15-2C-502(C)(2)).
            line_f = m["rental_income"]
            # Social Security benefits are not income for the credit. Every
            # member counts, dependent or not (A.A.C. R15-2C-502(A)(2), (B)).
            total += line_a + line_b + _line_d(m) + line_e + line_f
        totals.append(total)
    return np.array(totals)


UNITS = _sample_units(np.random.default_rng(SEED))
RAISED = _with_head_gains_changed(UNITS, sign=1)
LOWERED = _with_head_gains_changed(UNITS, sign=-1)
LINE_J = _form_140ptc_line_j(UNITS)


def test_sample_covers_the_loss_limit_and_negative_line_j():
    members = [m for unit in UNITS for m in unit["members"]]
    beyond_limit = [m for m in members if _net_gain(m) < -MEMBER_LOSS_LIMIT]
    assert len(beyond_limit) >= 20
    assert any(m["role"] == "dependent" for m in beyond_limit)

    # Units where federal AGI's capital gains and losses (non-dependents'
    # positive gains and distributions, less their losses limited to $3,000
    # per return) differ from every member's line D.
    def federal_capital(unit: dict) -> float:
        filers = [m for m in unit["members"] if m["role"] != "dependent"]
        gains = sum(
            max(0, m["long_term_capital_gains"] + m["short_term_capital_gains"])
            + m["non_sch_d_capital_gains"]
            for m in filers
        )
        losses = sum(
            max(0, -(m["long_term_capital_gains"] + m["short_term_capital_gains"]))
            for m in filers
        )
        return gains - min(3_000, losses)

    federal = np.array([federal_capital(unit) for unit in UNITS])
    line_d = np.array([sum(_line_d(m) for m in unit["members"]) for unit in UNITS])
    assert (np.abs(federal - line_d) > 0.01).sum() >= 20
    assert (LINE_J < 0).sum() >= 3
    # Distributions alongside a net capital loss, and rental losses, including
    # dependents'.
    assert any(
        m["non_sch_d_capital_gains"] > 0
        and m["long_term_capital_gains"] + m["short_term_capital_gains"] < 0
        for m in members
    )
    assert any(m["rental_income"] < 0 for m in members if m["role"] == "dependent")


def test_household_income_matches_form_140ptc_lines():
    sim = Simulation(situation=_situation(UNITS))
    income = sim.calculate("az_property_tax_credit_income", YEAR)
    np.testing.assert_allclose(income, LINE_J, atol=0.01)


def test_gains_count_once_up_to_the_loss_limit():
    base = Simulation(situation=_situation(UNITS))
    raised = Simulation(situation=_situation(RAISED))
    expected = np.array(
        [
            _line_d(r["members"][0]) - _line_d(u["members"][0])
            for u, r in zip(UNITS, RAISED)
        ]
    )
    income_change = raised.calculate(
        "az_property_tax_credit_income", YEAR
    ) - base.calculate("az_property_tax_credit_income", YEAR)
    np.testing.assert_allclose(income_change, expected, atol=0.01)
    # Where the head's net gain stays at or above the limit, the change is d.
    stays_above = np.array(
        [_net_gain(u["members"][0]) >= -MEMBER_LOSS_LIMIT for u in UNITS]
    )
    increase = np.array([unit["gain_change"] for unit in UNITS])
    assert stays_above.sum() >= 20
    np.testing.assert_allclose(
        income_change[stays_above], increase[stays_above], atol=0.01
    )
    credit_change = raised.calculate("az_property_tax_credit", YEAR) - base.calculate(
        "az_property_tax_credit", YEAR
    )
    assert (credit_change <= 0.01).all()


def test_member_loss_limit():
    base = Simulation(situation=_situation(UNITS))
    lowered = Simulation(situation=_situation(LOWERED))
    income_change = lowered.calculate(
        "az_property_tax_credit_income", YEAR
    ) - base.calculate("az_property_tax_credit_income", YEAR)
    expected = np.array(
        [
            _line_d(w["members"][0]) - _line_d(u["members"][0])
            for u, w in zip(UNITS, LOWERED)
        ]
    )
    np.testing.assert_allclose(income_change, expected, atol=0.01)
    # Once a member's net gain is at or below the limit, more loss is ignored.
    at_limit = np.array(
        [_net_gain(u["members"][0]) <= -MEMBER_LOSS_LIMIT for u in UNITS]
    )
    assert at_limit.sum() >= 10
    np.testing.assert_allclose(income_change[at_limit], 0, atol=0.01)
    # Each member's line D is bounded below by the limit.
    line_d = base.calculate("az_property_tax_credit_capital_gains", YEAR)
    assert (line_d >= -MEMBER_LOSS_LIMIT - 0.01).all()


def test_credit_uses_zero_for_negative_household_income():
    sim = Simulation(situation=_situation(UNITS))
    credit = sim.calculate("az_property_tax_credit", YEAR)
    floored = Simulation(situation=_situation(UNITS))
    floored.set_input("az_property_tax_credit_income", YEAR, np.maximum(LINE_J, 0))
    np.testing.assert_allclose(
        credit, floored.calculate("az_property_tax_credit", YEAR), atol=0.01
    )
    # A negative line J gets the zero-income schedule amount ($502 on both
    # schedules), limited by the renter's property taxes.
    negative = LINE_J < 0
    rent = np.array([unit["rent"] for unit in UNITS])
    np.testing.assert_allclose(
        credit[negative],
        np.minimum(502, RENT_PROPERTY_TAX_RATE * rent[negative]),
        atol=0.01,
    )


def test_income_does_not_read_preferential_rate_amount():
    base = Simulation(situation=_situation(UNITS))
    sim = Simulation(situation=_situation(UNITS))
    rng = np.random.default_rng(SEED + 1)
    sim.set_input(
        "capital_gains_excluded_from_taxable_income",
        YEAR,
        rng.uniform(0, 50_000, len(UNITS)),
    )
    np.testing.assert_allclose(
        sim.calculate("az_property_tax_credit_income", YEAR),
        base.calculate("az_property_tax_credit_income", YEAR),
        atol=0.01,
    )


def test_line_d_survives_a_loss_deduction_without_capital_losses():
    """A reform whose loss_ald holds only rental losses leaves line J whole.

    az_property_tax_credit_agi adds back only the capital part of loss_ald
    (loss_ald less limited_business_loss), so a federal loss deduction with no
    capital loss in it is not reversed as one.
    """
    from policyengine_core.reforms import Reform
    from policyengine_us.model_api import YEAR as ANNUAL
    from policyengine_us.model_api import TaxUnit, USD, Variable, max_

    class rental_losses_only(Reform):
        def apply(self):
            class loss_ald(Variable):
                value_type = float
                entity = TaxUnit
                label = "Rental losses only"
                unit = USD
                definition_period = ANNUAL

                def formula(tax_unit, period, parameters):
                    person = tax_unit.members
                    not_dependent = ~person("is_tax_unit_dependent", period)
                    rental_loss = max_(0, -person("rental_income", period))
                    return tax_unit.sum(not_dependent * rental_loss)

            self.update_variable(loss_ald)

    year = str(YEAR)
    situation = {
        "people": {
            "head": {
                "age": {year: 70},
                "employment_income": {year: 4_000},
                "long_term_capital_gains": {year: -5_000},
                "rental_income": {year: -1_000},
                "rent": {year: 5_000},
            }
        },
        "tax_units": {"tax_unit": {"members": ["head"]}},
        "households": {"household": {"members": ["head"], "state_code": {year: "AZ"}}},
    }
    sim = Simulation(situation=situation, reform=rental_losses_only)
    # Federal AGI takes the rental loss only: 4,000 - 1,000.
    assert sim.calculate("adjusted_gross_income", YEAR)[0] == 3_000
    # Form 140PTC: line A 4,000 + line D (1,500) + line F (1,000) = 1,500.
    np.testing.assert_allclose(
        sim.calculate("az_property_tax_credit_income", YEAR), [1_500], atol=0.01
    )
    # Schedule 1, 0 - 1,750 -> 502; property taxes 0.15 x 5,000 = 750.
    np.testing.assert_allclose(
        sim.calculate("az_property_tax_credit", YEAR), [502], atol=0.01
    )

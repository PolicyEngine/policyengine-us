"""Sampled property tests for Arizona property tax credit household income.

ARS 43-1072(H)(6) defines income for the credit, and A.A.C. R15-2C-502 and the
Form 140PTC instructions (2021-2025, page 4) apply it line by line: line D is
each member's gains and losses from the sale or exchange of property, combined,
with a net loss limited to $1,500. Federal AGI already holds those gains, so
az_property_tax_credit_income must count each dollar of gain once. It used to
add capital_gains_excluded_from_taxable_income as well, which is the part of
federal taxable income taxed at the capital gains rates (at zero taxable
income, the adjusted net capital gain), so gains and qualified dividends
counted twice. Federal AGI leaves out dependents' income, which Arizona counts
for every household member whether or not a dependent. Federal AGI deducts
every member's losses, so it is not floored before dependents' income is added.

Invariants, checked on a seeded sample of Arizona tax units (some with a child
dependent who has income). The sample stays where the federal and Arizona
capital loss rules agree: each member's net capital gain is at least -$1,500
and a tax unit's net losses total at most $3,000, the federal limit per return.

1. Differential: the model equals an independent line A + B + D + E sum over
   every member from Form 140PTC Part 1, with Social Security excluded.
2. Counted once: adding d to one member's long-term gains (the dependent's
   where there is one, else the head's) raises household income by exactly d.
3. The income does not depend on capital_gains_excluded_from_taxable_income.
4. The credit never rises when gains rise.
"""

import numpy as np

from policyengine_us import Simulation

YEAR = 2025
N = 60
SEED = 43_1072
# A.A.C. R15-2C-502(C)(3): net capital losses are limited to $1,500 for each
# household member. The sample stays at or above it, and keeps each tax unit's
# net losses within federal AGI's $3,000-per-return limit, so both rules give
# the same answer.
MEMBER_LOSS_LIMIT = 1_500
RETURN_LOSS_LIMIT = 3_000


def _sample_units(rng: np.random.Generator) -> list:
    units = []
    for _ in range(N):
        married = rng.random() < 0.4
        members = []
        for role in ["head", "spouse"] if married else ["head"]:
            gains = rng.random() < 0.7
            # Some large gains, so federal taxable income is positive.
            large_gain = (
                round(rng.uniform(20_000, 80_000), 2) if rng.random() < 0.15 else 0
            )
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
                    "long_term_capital_gains": (
                        round(rng.uniform(-1_000, 6_000), 2) + large_gain
                        if gains
                        else 0.0
                    ),
                    "short_term_capital_gains": (
                        round(rng.uniform(-500, 2_000), 2) if gains else 0.0
                    ),
                    "taxable_private_pension_income": round(rng.uniform(0, 3_000), 2),
                    "tax_exempt_public_pension_income": round(rng.uniform(0, 1_000), 2),
                    "social_security_retirement": float(
                        rng.choice([0, round(rng.uniform(0, 30_000), 2)])
                    ),
                }
            )
        if rng.random() < 0.35:
            # A child dependent with income of their own, sometimes with a net
            # capital loss. A couple can already reach the federal limit, so
            # only a single head's dependent gets a loss.
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
                    "long_term_capital_gains": round(
                        rng.uniform(0 if married else -1_500, 4_000), 2
                    ),
                    "short_term_capital_gains": round(rng.uniform(0, 1_000), 2),
                    "taxable_private_pension_income": 0.0,
                    "tax_exempt_public_pension_income": 0.0,
                    "social_security_survivors": float(
                        rng.choice([0, round(rng.uniform(0, 8_000), 2)])
                    ),
                }
            )
        for member in members:
            net_gain = (
                member["long_term_capital_gains"] + member["short_term_capital_gains"]
            )
            assert net_gain >= -MEMBER_LOSS_LIMIT
        net_losses = sum(
            max(0, -(m["long_term_capital_gains"] + m["short_term_capital_gains"]))
            for m in members
        )
        assert net_losses <= RETURN_LOSS_LIMIT
        units.append(
            {
                "members": members,
                "rent": round(rng.uniform(1_000, 12_000), 2),
                "gain_increase": round(rng.uniform(1, 5_000), 2),
            }
        )
    return units


def _raised_role(unit: dict) -> str:
    roles = [member["role"] for member in unit["members"]]
    return "dependent" if "dependent" in roles else "head"


def _situation(units: list, raise_gains: bool) -> dict:
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
            if raise_gains and member["role"] == _raised_role(unit):
                person["long_term_capital_gains"] = {
                    year: member["long_term_capital_gains"] + unit["gain_increase"]
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
            line_d = max(
                m["long_term_capital_gains"] + m["short_term_capital_gains"],
                -MEMBER_LOSS_LIMIT,
            )
            line_e = (
                m["taxable_private_pension_income"]
                + m["tax_exempt_public_pension_income"]
            )
            # Social Security benefits are not income for the credit. Every
            # member counts, dependent or not (A.A.C. R15-2C-502(A)(2), (B)).
            total += line_a + line_b + line_d + line_e
        totals.append(total)
    return np.array(totals)


UNITS = _sample_units(np.random.default_rng(SEED))


def test_household_income_matches_form_140ptc_lines():
    sim = Simulation(situation=_situation(UNITS, raise_gains=False))
    income = sim.calculate("az_property_tax_credit_income", YEAR)
    np.testing.assert_allclose(income, _form_140ptc_line_j(UNITS), atol=0.01)


def test_gains_count_once():
    base = Simulation(situation=_situation(UNITS, raise_gains=False))
    raised = Simulation(situation=_situation(UNITS, raise_gains=True))
    increase = np.array([unit["gain_increase"] for unit in UNITS])
    income_change = raised.calculate(
        "az_property_tax_credit_income", YEAR
    ) - base.calculate("az_property_tax_credit_income", YEAR)
    np.testing.assert_allclose(income_change, increase, atol=0.01)
    credit_change = raised.calculate("az_property_tax_credit", YEAR) - base.calculate(
        "az_property_tax_credit", YEAR
    )
    assert (credit_change <= 0.01).all()


def test_income_does_not_read_preferential_rate_amount():
    sim = Simulation(situation=_situation(UNITS, raise_gains=False))
    rng = np.random.default_rng(SEED + 1)
    sim.set_input(
        "capital_gains_excluded_from_taxable_income",
        YEAR,
        rng.uniform(0, 50_000, len(UNITS)),
    )
    income = sim.calculate("az_property_tax_credit_income", YEAR)
    np.testing.assert_allclose(income, _form_140ptc_line_j(UNITS), atol=0.01)

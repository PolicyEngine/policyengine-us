"""Invariants for Maryland's State and local poverty level credits.

Md. Code, Tax-General § 10-709(c) and (d) set each credit to the lesser of
remaining tax and a share of § 32(c)(2) earned income. A self-employment
loss can make net earnings negative, and before this fix that turned both
credits negative, which raised tax. The properties below must hold for
every household, so they are checked over two vectorized simulations per
tax year (baseline and credits neutralized): a seeded random sample plus an
edge grid of self-employment losses, profits and wages around the poverty
level, for tax years 2021 to 2025.
"""

import numpy as np
import pytest

from policyengine_core.reforms import Reform

from policyengine_us import Simulation

YEARS = [2021, 2022, 2023, 2024, 2025]
SAMPLE_SIZE = 150
# Cents of float32 noise allowed in comparisons.
TOLERANCE = 0.01


class neutralize_md_poverty_line_credits(Reform):
    def apply(self):
        self.neutralize_variable("md_poverty_line_credit")
        self.neutralize_variable("md_local_poverty_line_credit")


def _households(year):
    """Return (wages, spouse_wages, se, spouse_se, interest, joint, kids)."""
    rng = np.random.default_rng(year)
    rows = []
    # Edge grid: losses, zero, and profits around the poverty level, with
    # and without wages that net against them.
    for se in [-30_000, -10_000, -500, 0, 500, 3_000, 15_000, 16_000]:
        for wages in [0, 3_000, 9_000]:
            for interest in [0, 4_000, 20_000]:
                rows.append((wages, 0, se, 0, interest, False, 0))
                rows.append((wages, 0, 0, se, interest, True, 2))
    for _ in range(SAMPLE_SIZE):
        joint = bool(rng.integers(0, 2))
        rows.append(
            (
                int(rng.choice([0, rng.integers(0, 30_000)])),
                int(rng.integers(0, 15_000)) if joint else 0,
                int(rng.integers(-40_000, 30_000)),
                int(rng.integers(-20_000, 20_000)) if joint else 0,
                int(rng.choice([0, rng.integers(0, 30_000)])),
                joint,
                int(rng.integers(0, 3)),
            )
        )
    return rows


def _situation(year, rows):
    y = str(year)
    people, tax_units, spm_units, households = {}, {}, {}, {}
    marital_units, families = {}, {}
    for i, (wages, spouse_wages, se, spouse_se, interest, joint, kids) in enumerate(
        rows
    ):
        head = f"head_{i}"
        members = [head]
        people[head] = {
            "age": {y: 40},
            "employment_income": {y: wages},
            "self_employment_income": {y: se},
            "taxable_interest_income": {y: interest / 2 if joint else interest},
        }
        marital_units[f"mu_{i}"] = {"members": [head]}
        if joint:
            spouse = f"spouse_{i}"
            people[spouse] = {
                "age": {y: 40},
                "employment_income": {y: spouse_wages},
                "self_employment_income": {y: spouse_se},
                "taxable_interest_income": {y: interest / 2},
            }
            members.append(spouse)
            marital_units[f"mu_{i}"] = {"members": [head, spouse]}
        for k in range(kids):
            child = f"child_{i}_{k}"
            people[child] = {"age": {y: 5 + k}}
            members.append(child)
            marital_units[f"mu_{i}_{k}"] = {"members": [child]}
        tax_units[f"tu_{i}"] = {"members": members}
        spm_units[f"spm_{i}"] = {"members": members}
        families[f"fam_{i}"] = {"members": members}
        households[f"hh_{i}"] = {
            "members": members,
            "state_code": {y: "MD"},
        }
    return {
        "people": people,
        "tax_units": tax_units,
        "spm_units": spm_units,
        "families": families,
        "marital_units": marital_units,
        "households": households,
    }


@pytest.fixture(scope="module", params=YEARS)
def results(request):
    year = request.param
    situation = _situation(year, _households(year))
    baseline = Simulation(situation=situation)
    without = Simulation(situation=situation, reform=neutralize_md_poverty_line_credits)

    def calc(sim, variable):
        return sim.calculate(variable, year).astype(float)

    return year, {
        "earned": calc(baseline, "eitc_earned_income"),
        "net_earnings": calc(baseline, "tax_unit_earned_income"),
        "eligible": baseline.calculate("is_eligible_md_poverty_line_credit", year),
        "potential": calc(baseline, "md_poverty_line_credit_potential"),
        "state": calc(baseline, "md_poverty_line_credit"),
        "local": calc(baseline, "md_local_poverty_line_credit"),
        "rate": calc(baseline, "md_applicable_local_tax_rate"),
        "tax_before": calc(baseline, "md_income_tax_before_credits"),
        "local_before": calc(baseline, "md_local_income_tax_before_credits"),
        "local_after": calc(baseline, "md_local_income_tax_before_refundable_credits"),
        "md_tax": calc(baseline, "md_income_tax"),
        "md_tax_without": calc(without, "md_income_tax"),
        "local_after_without": calc(
            without, "md_local_income_tax_before_refundable_credits"
        ),
    }


def test_sample_includes_net_losses(results):
    _, r = results
    # Guard the fixture: the property checks below are only meaningful if
    # eligible households with negative net earnings are in the sample.
    assert ((r["net_earnings"] < 0) & r["eligible"]).sum() > 0


def test_earned_income_is_never_negative(results):
    _, r = results
    assert (r["earned"] >= 0).all()


def test_credits_are_never_negative(results):
    _, r = results
    assert (r["potential"] >= -TOLERANCE).all()
    assert (r["state"] >= -TOLERANCE).all()
    assert (r["local"] >= -TOLERANCE).all()


def test_credits_are_bounded_by_earned_income_share(results):
    _, r = results
    assert (r["potential"] <= 0.05 * r["earned"] + TOLERANCE).all()
    assert (r["local"] <= r["rate"] * r["earned"] + TOLERANCE).all()


def test_credits_are_bounded_by_tax(results):
    _, r = results
    assert (r["state"] <= r["tax_before"] + TOLERANCE).all()
    assert (r["local_after"] >= -TOLERANCE).all()
    assert (r["local_after"] <= r["local_before"] + TOLERANCE).all()


def test_no_earned_income_means_no_credit(results):
    _, r = results
    zero = r["earned"] == 0
    assert (np.abs(r["state"][zero]) <= TOLERANCE).all()
    assert (np.abs(r["local"][zero]) <= TOLERANCE).all()


def test_ineligible_households_get_no_credit(results):
    _, r = results
    ineligible = ~r["eligible"]
    assert (np.abs(r["potential"][ineligible]) <= TOLERANCE).all()
    assert (np.abs(r["local"][ineligible]) <= TOLERANCE).all()


def test_credits_never_raise_tax(results):
    _, r = results
    assert (r["md_tax"] <= r["md_tax_without"] + TOLERANCE).all()
    assert (r["local_after"] <= r["local_after_without"] + TOLERANCE).all()

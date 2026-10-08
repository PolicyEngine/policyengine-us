"""Invariants of the overall limitation on itemized deductions (26 U.S.C. 68).

Before P.L. 119-21, section 68(a) reduced itemized deductions by the lesser of
3 percent of AGI over the applicable amount or 80 percent of "the itemized
deductions otherwise allowable", and section 68(c) excluded from that term the
deduction for medical expenses (section 213), any deduction for investment
interest (section 163(d)), and casualty, theft and wagering losses (section
165(c)(2), (c)(3) and (d)). The Itemized Deductions Worksheet—Line 29 in the
Instructions for Schedule A (Form 1040) implements this. P.L. 119-21, sec.
70111(a), rewrote section 68 for taxable years beginning after 2025 without
subsection (c).

Tax units with seeded random incomes, filing statuses and deduction mixes share
one simulation per case. The tests check:

1. PolicyEngine matches an independent restatement of worksheet lines 1-10 for
   2015-2017, with the line 6 applicable amounts restated from the worksheets.
   (The limitation's rate parameters do not resolve before 2015.)
2. The reduction lies between 0 and both the 3 percent amount and 80 percent of
   the deductions that section 68(c) does not exclude.
3. Excluded deductions are never reduced: allowed deductions are at least the
   excluded amount plus 20 percent of the rest.
4. Raising an excluded deduction leaves the reduction unchanged, so allowed
   deductions rise one for one.
5. Allowed deductions never fall when any component rises, and the reduction
   never falls when AGI rises.
6. From 2026 the reduction depends only on total itemized deductions, not on
   how they split between formerly excluded and other categories.
7. With the OBBB structure switched off in 2026 (the prior-law counterfactual),
   the pre-2026 worksheet logic applies with the 2026 applicable amounts.

Gambling losses are deducted outside total_itemized_taxable_income_deductions
(wagering_losses_deduction), so they never enter the limited base; they are
not generated here.
"""

import numpy as np
import pytest

from policyengine_us import Simulation
from policyengine_us.system import system
from policyengine_core.reforms import Reform

N = 600
STATUSES = ("SINGLE", "JOINT", "SEPARATE", "HEAD_OF_HOUSEHOLD", "SURVIVING_SPOUSE")

# Worksheet line 6: "Enter $X if married filing jointly or qualifying
# widow(er); $Y if head of household; $Z if single; or $W if married filing
# separately" (Instructions for Schedule A, Itemized Deductions Worksheet—Line
# 29, 2015-2017 editions).
APPLICABLE_AMOUNTS = {
    2015: {"JOINT": 309_900, "HEAD_OF_HOUSEHOLD": 284_050, "SINGLE": 258_250},
    2016: {"JOINT": 311_300, "HEAD_OF_HOUSEHOLD": 285_350, "SINGLE": 259_400},
    2017: {"JOINT": 313_800, "HEAD_OF_HOUSEHOLD": 287_650, "SINGLE": 261_500},
}
SEPARATE_AMOUNTS = {2015: 154_950, 2016: 155_650, 2017: 156_900}

# Components of total_itemized_taxable_income_deductions, split by whether
# section 68(c) excludes them. Mortgage and investment interest are person
# inputs that interest_deduction adds up.
EXCLUDED = ("medical_expense_deduction", "casualty_loss_deduction")
EXCLUDED_PERSON = ("investment_interest_expense",)
OTHER = ("charitable_deduction", "salt_deduction", "misc_deduction")
OTHER_PERSON = ("deductible_mortgage_interest",)
COMPONENTS = EXCLUDED + OTHER
PERSON_COMPONENTS = EXCLUDED_PERSON + OTHER_PERSON
ALL_COMPONENTS = COMPONENTS + PERSON_COMPONENTS
# PolicyEngine computes in float32, whose spacing near $1 million is 6 cents,
# so tolerances scale with the size of the operands (not of the result: the
# 80 percent base is a difference of two such sums).
RTOL = 1e-6
ATOL = 0.01


def _slack(scale):
    return ATOL + RTOL * np.abs(scale)


def _close(actual, desired, scale, message=""):
    gap = np.abs(np.asarray(actual, dtype=float) - desired)
    worst = int(np.argmax(gap - _slack(scale)))
    assert np.all(gap <= _slack(scale)), (
        f"{message} unit {worst}: {actual[worst]} vs {desired[worst]}"
    )


OUTPUTS = (
    "itemized_taxable_income_deductions_reduction",
    "itemized_taxable_income_deductions",
    "total_itemized_taxable_income_deductions",
)


def _draw(seed):
    """Seeded tax units: filing status, AGI and each deduction component."""
    rng = np.random.default_rng(seed)
    units = {
        "filing_status": rng.choice(STATUSES, N),
        "adjusted_gross_income": np.round(rng.uniform(0, 1_500_000, N), 2),
    }
    for name in ALL_COMPONENTS:
        amount = np.round(rng.uniform(0, 150_000, N), 2)
        units[name] = np.where(rng.random(N) < 0.5, 0, amount)
    # Every fifth unit has only excluded deductions (worksheet line 3 "No").
    only_excluded = np.arange(N) % 5 == 0
    for name in OTHER + OTHER_PERSON:
        units[name] = np.where(only_excluded, 0, units[name])
    return units


def _simulate(year, units, reform=None):
    period = str(year)
    people, tax_units, households = {}, {}, {}
    for i in range(N):
        person = f"p{i}"
        people[person] = {"age": {period: 50}}
        for name in PERSON_COMPONENTS:
            people[person][name] = {period: float(units[name][i])}
        tax_units[f"t{i}"] = {
            "members": [person],
            "filing_status": {period: str(units["filing_status"][i])},
            "adjusted_gross_income": {period: float(units["adjusted_gross_income"][i])},
            **{name: {period: float(units[name][i])} for name in COMPONENTS},
        }
        households[f"h{i}"] = {"members": [person]}
    situation = {"people": people, "tax_units": tax_units, "households": households}
    simulation = Simulation(situation=situation, reform=reform)
    return {name: simulation.calculate(name, period) for name in OUTPUTS}


def _split(units):
    excluded = sum(units[name] for name in EXCLUDED + EXCLUDED_PERSON)
    other = sum(units[name] for name in OTHER + OTHER_PERSON)
    return excluded, other


def _worksheet_line_9(units, applicable_amount):
    """Itemized Deductions Worksheet—Line 29, lines 1-9, restated."""
    excluded, other = _split(units)
    line_1 = excluded + other
    line_2 = excluded
    line_3 = np.where(line_2 < line_1, line_1 - line_2, 0)
    line_4 = line_3 * 0.8
    line_5 = units["adjusted_gross_income"]
    line_6 = applicable_amount
    line_7 = np.where(line_6 < line_5, line_5 - line_6, 0)
    line_8 = line_7 * 0.03
    return np.minimum(line_4, line_8)


def _worksheet_amounts(year, statuses):
    amounts = APPLICABLE_AMOUNTS[year]
    return np.array(
        [
            SEPARATE_AMOUNTS[year]
            if status == "SEPARATE"
            else amounts["JOINT" if status == "SURVIVING_SPOUSE" else status]
            for status in statuses
        ]
    )


def _parameter_amounts(year, statuses):
    p = system.parameters(f"{year}-01-01").gov.irs.deductions.itemized.limitation
    return np.asarray(p.applicable_amount[np.asarray(statuses)])


def _check_pre_2026_structure(units, results, applicable_amount):
    reduction = results["itemized_taxable_income_deductions_reduction"]
    allowed = results["itemized_taxable_income_deductions"]
    excluded, other = _split(units)
    scale = excluded + other + units["adjusted_gross_income"]

    # PolicyEngine's total is the sum of the generated components.
    _close(
        results["total_itemized_taxable_income_deductions"],
        excluded + other,
        scale,
        "total",
    )

    # 1. Worksheet line 9 and line 10.
    line_9 = _worksheet_line_9(units, applicable_amount)
    _close(reduction, line_9, scale, "line 9")
    _close(allowed, excluded + other - line_9, scale, "line 10")

    # 2. Bounds on the reduction.
    agi_excess = np.maximum(0, units["adjusted_gross_income"] - applicable_amount)
    assert np.all(reduction >= 0)
    assert np.all(reduction <= 0.03 * agi_excess + _slack(scale))
    assert np.all(reduction <= 0.8 * other + _slack(scale))

    # 3. Excluded deductions are never reduced.
    assert np.all(allowed >= excluded + 0.2 * other - _slack(scale))


@pytest.mark.parametrize("year", sorted(APPLICABLE_AMOUNTS))
def test_reduction_matches_the_line_29_worksheet(year):
    units = _draw(seed=year)
    results = _simulate(year, units)
    amounts = _worksheet_amounts(year, units["filing_status"])
    # The parameter file carries the same applicable amounts.
    np.testing.assert_array_equal(
        _parameter_amounts(year, units["filing_status"]), amounts
    )
    _check_pre_2026_structure(units, results, amounts)


@pytest.mark.parametrize("year", sorted(APPLICABLE_AMOUNTS))
def test_reduction_responds_to_components_and_income(year):
    units = _draw(seed=year + 1)
    base = _simulate(year, units)
    base_reduction = base["itemized_taxable_income_deductions_reduction"]
    base_allowed = base["itemized_taxable_income_deductions"]
    excluded, other = _split(units)
    scale = excluded + other + units["adjusted_gross_income"] + 10_000

    for name in ALL_COMPONENTS:
        raised = dict(units, **{name: units[name] + 1_000})
        results = _simulate(year, raised)
        allowed = results["itemized_taxable_income_deductions"]
        # 5. More of any deduction never lowers allowed deductions.
        assert np.all(allowed >= base_allowed - _slack(scale)), name
        if name in EXCLUDED + EXCLUDED_PERSON:
            # 4. Excluded deductions pass through without reduction.
            _close(
                results["itemized_taxable_income_deductions_reduction"],
                base_reduction,
                scale,
                name,
            )
            _close(allowed, base_allowed + 1_000, scale, name)

    # 5. More AGI never lowers the reduction.
    richer = dict(units, adjusted_gross_income=units["adjusted_gross_income"] + 10_000)
    richer_reduction = _simulate(year, richer)[
        "itemized_taxable_income_deductions_reduction"
    ]
    assert np.all(richer_reduction >= base_reduction - _slack(scale))


def test_2026_reduction_ignores_the_mix_of_deductions():
    # 6. Section 68 as amended by P.L. 119-21 has no subsection (c), so moving
    # amounts from formerly excluded deductions into charity changes nothing.
    units = _draw(seed=2026)
    excluded, other = _split(units)
    moved = dict(units)
    for name in ALL_COMPONENTS:
        moved[name] = np.zeros(N)
    moved["charitable_deduction"] = excluded + other
    base = _simulate(2026, units)
    results = _simulate(2026, moved)
    total = excluded + other
    scale = total + units["adjusted_gross_income"]
    reduction = base["itemized_taxable_income_deductions_reduction"]
    _close(
        results["itemized_taxable_income_deductions_reduction"],
        reduction,
        scale,
    )
    assert np.all(reduction >= 0)
    assert np.all(reduction <= total * 2 / 37 + _slack(scale))
    assert np.any(reduction > 0)


def test_2026_prior_law_counterfactual_uses_the_worksheet():
    # 7. Without the OBBB structure, 2026 reverts to the pre-2026 section 68,
    # including subsection (c), at the 2026 applicable amounts.
    reform = Reform.from_dict(
        {
            "gov.irs.deductions.itemized.limitation.obbb.applies": {
                "2026-01-01.2100-12-31": False
            }
        },
        country_id="us",
    )
    units = _draw(seed=2025)
    results = _simulate(2026, units, reform=reform)
    amounts = _parameter_amounts(2026, units["filing_status"])
    _check_pre_2026_structure(units, results, amounts)
    assert np.any(results["itemized_taxable_income_deductions_reduction"] > 0)

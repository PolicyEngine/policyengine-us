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

From 2026 section 68(a) reduces itemized deductions by 2/37 of the lesser of
(1) the itemized deductions and (2) "so much of the taxable income ...
(determined without regard to this section and increased by such amount of
itemized deductions) as exceeds the dollar amount at which the 37 percent rate
bracket under section 1 begins". Leg (2) is AGI less personal exemptions and
the deductions section 63(b) allows besides itemized deductions (section
63(d)(2)): the section 199A, 224 and 225 deductions, the section 151(d)(5)(C)
senior deduction and qualified passenger vehicle loan interest. Section
199A(e)(1), as amended by P.L. 119-21, sec. 70111(b), computes the QBI
deduction's taxable income without regard to section 68. The tests check:

8. The reduction equals 2/37 of the lesser of the itemized deductions and
   AGI less those deductions over the Rev. Proc. 2025-32 bracket start,
   restated independently, and lies between 0 and 2/37 of the itemized
   deductions.
9. Each of those deductions lowers leg (2) one for one, and so never raises
   the reduction or lowers it by more than 2/37 of itself; wagering losses,
   an itemized deduction, leave leg (2) unchanged. More AGI never lowers the
   reduction, and more of any itemized deduction never lowers the allowed
   deductions.
10. With the QBI deduction calculated from qualified REIT dividends, it is the
    lesser of 20 percent of the dividends and 20 percent of AGI less the
    itemized deductions before section 68, and the reduction nets it out of
    leg (2), whether the itemization choice is set or calculated.

Gambling losses are deducted outside total_itemized_taxable_income_deductions
(wagering_losses_deduction), so they never enter the limited base; they are
not generated here.
"""

from functools import cache

import numpy as np
import pytest

from policyengine_us import CountryTaxBenefitSystem, Simulation
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


def _simulate(
    year, units, reform=None, tax_unit_inputs=(), person_inputs=(), outputs=OUTPUTS
):
    period = str(year)
    people, tax_units, households = {}, {}, {}
    for i in range(N):
        person = f"p{i}"
        people[person] = {"age": {period: 50}}
        for name in PERSON_COMPONENTS + tuple(person_inputs):
            people[person][name] = {period: float(units[name][i])}
        tax_units[f"t{i}"] = {
            "members": [person],
            "filing_status": {period: str(units["filing_status"][i])},
            "adjusted_gross_income": {period: float(units["adjusted_gross_income"][i])},
            **{
                name: {period: units[name][i].item()}
                for name in COMPONENTS + tuple(tax_unit_inputs)
            },
        }
        households[f"h{i}"] = {"members": [person]}
    situation = {"people": people, "tax_units": tax_units, "households": households}
    simulation = Simulation(situation=situation, reform=reform)
    return {name: simulation.calculate(name, period) for name in outputs}


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


@cache
def _system():
    return CountryTaxBenefitSystem()


def _parameter_amounts(year, statuses):
    p = _system().parameters(f"{year}-01-01").gov.irs.deductions.itemized.limitation
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


# Rev. Proc. 2025-32, sec. 4.01, Tables 1-4: the 2026 37 percent rate bracket
# begins over these amounts of taxable income.
TOP_BRACKET_STARTS_2026 = {
    "JOINT": 768_700,
    "SURVIVING_SPOUSE": 768_700,
    "HEAD_OF_HOUSEHOLD": 640_600,
    "SINGLE": 640_600,
    "SEPARATE": 384_350,
}
# Deductions section 63(b) allows whether or not the filer itemizes, which
# section 63(d)(2) keeps out of itemized deductions.
NON_ITEMIZED = (
    "qualified_business_income_deduction",
    "tip_income_deduction",
    "overtime_income_deduction",
    "additional_senior_deduction",
    "auto_loan_interest_deduction",
)
OUTPUTS_2026 = OUTPUTS + (
    "taxable_income_before_itemized_deductions",
    "taxable_income_less_qbid",
    "qualified_business_income_deduction",
    "exemptions",
)


def _top_bracket_starts(statuses):
    return np.array([TOP_BRACKET_STARTS_2026[status] for status in statuses])


def _draw_2026(seed):
    """Seeded 2026 itemizers with deductions other than itemized deductions."""
    units = _draw(seed)
    rng = np.random.default_rng(seed + 1)
    for name in NON_ITEMIZED:
        cap = 150_000 if name == "qualified_business_income_deduction" else 25_000
        amount = np.round(rng.uniform(0, cap, N), 2)
        units[name] = np.where(rng.random(N) < 0.5, 0, amount)
    units["wagering_losses_deduction"] = np.zeros(N)
    units["tax_unit_itemizes"] = np.ones(N, dtype=bool)
    return units


def _simulate_2026(units, **kwargs):
    inputs = NON_ITEMIZED + ("wagering_losses_deduction", "tax_unit_itemizes")
    return _simulate(
        2026, units, tax_unit_inputs=inputs, outputs=OUTPUTS_2026, **kwargs
    )


def _section_68_reduction(itemized, income_before_itemized, statuses):
    """2/37 of the lesser of section 68(a)(1) and (a)(2), restated."""
    excess = np.maximum(0, income_before_itemized - _top_bracket_starts(statuses))
    return np.minimum(itemized, excess) * 2 / 37


def _check_2026_structure(units, results, non_itemized_total):
    statuses = units["filing_status"]
    itemized = results["total_itemized_taxable_income_deductions"]
    reduction = results["itemized_taxable_income_deductions_reduction"]
    allowed = results["itemized_taxable_income_deductions"]
    agi = units["adjusted_gross_income"]
    scale = agi + itemized + non_itemized_total
    # Section 151(d)(5)(A): the exemption amount is zero after 2017.
    assert np.all(results["exemptions"] == 0)

    # 8. Leg (2) and the reduction, restated from the statute.
    _close(
        results["taxable_income_before_itemized_deductions"],
        agi - non_itemized_total,
        scale,
        "leg (2)",
    )
    expected = _section_68_reduction(itemized, agi - non_itemized_total, statuses)
    _close(reduction, expected, scale, "reduction")
    _close(allowed, itemized - expected, scale, "allowed")
    assert np.all(reduction >= 0)
    assert np.all(reduction <= itemized * 2 / 37 + _slack(scale))
    return expected


def test_2026_bracket_starts_match_the_parameters():
    p = _system().parameters("2026-01-01").gov.irs.income.bracket.thresholds
    statuses = np.array(list(TOP_BRACKET_STARTS_2026))
    np.testing.assert_array_equal(
        np.asarray(p["6"][statuses]), _top_bracket_starts(statuses)
    )


def test_2026_taxable_income_leg_nets_non_itemized_deductions():
    units = _draw_2026(seed=2126)
    results = _simulate_2026(units)
    non_itemized_total = sum(units[name] for name in NON_ITEMIZED)
    expected = _check_2026_structure(units, results, non_itemized_total)
    # The draws cover both legs binding and no reduction.
    itemized = results["total_itemized_taxable_income_deductions"]
    excess = (
        units["adjusted_gross_income"]
        - non_itemized_total
        - _top_bracket_starts(units["filing_status"])
    )
    assert np.any((expected > 0) & (excess < itemized))
    assert np.any((expected > 0) & (excess > itemized))
    assert np.any(expected == 0)
    # Without the 63(b) deductions some of these units would be reduced.
    assert np.any(
        (expected == 0)
        & (
            _section_68_reduction(
                itemized, units["adjusted_gross_income"], units["filing_status"]
            )
            > 0
        )
    )


def test_2026_reduction_responds_to_each_deduction_and_income():
    # 9. One for one in leg (2); never a larger reduction.
    units = _draw_2026(seed=2127)
    base = _simulate_2026(units)
    base_leg = base["taxable_income_before_itemized_deductions"]
    base_reduction = base["itemized_taxable_income_deductions_reduction"]
    base_allowed = base["itemized_taxable_income_deductions"]
    non_itemized_total = sum(units[name] for name in NON_ITEMIZED)
    scale = (
        units["adjusted_gross_income"]
        + base["total_itemized_taxable_income_deductions"]
        + non_itemized_total
        + 10_000
    )
    step = 1_000
    for name in NON_ITEMIZED + ("wagering_losses_deduction",):
        raised = dict(units, **{name: units[name] + step})
        results = _simulate_2026(raised)
        leg = results["taxable_income_before_itemized_deductions"]
        reduction = results["itemized_taxable_income_deductions_reduction"]
        if name == "wagering_losses_deduction":
            # Wagering losses are itemized deductions: section 68(a)(2) adds
            # them back, so leg (2) does not move.
            _close(leg, base_leg, scale, name)
            continue
        _close(leg, base_leg - step, scale, name)
        assert np.all(reduction <= base_reduction + _slack(scale)), name
        assert np.all(reduction >= base_reduction - step * 2 / 37 - _slack(scale)), name
        assert np.any(reduction < base_reduction - 1), name

    for name in ALL_COMPONENTS:
        raised = dict(units, **{name: units[name] + step})
        allowed = _simulate_2026(raised)["itemized_taxable_income_deductions"]
        assert np.all(allowed >= base_allowed - _slack(scale)), name

    richer = dict(units, adjusted_gross_income=units["adjusted_gross_income"] + 10_000)
    richer_reduction = _simulate_2026(richer)[
        "itemized_taxable_income_deductions_reduction"
    ]
    assert np.all(richer_reduction >= base_reduction - _slack(scale))


@pytest.mark.parametrize("choice", ["set", "calculated"])
def test_2026_calculated_qbi_deduction_ignores_section_68(choice):
    # 10. The QBI deduction from qualified REIT dividends (section
    # 199A(b)(1)(B)), capped at 20 percent of taxable income computed without
    # regard to section 68 (199A(a)(2), (e)(1)), and the reduction net of it.
    units = _draw(seed=2128)
    rng = np.random.default_rng(2129)
    units["qualified_reit_and_ptp_income"] = np.round(rng.uniform(0, 1_000_000, N), 2)
    tax_unit_inputs = ()
    if choice == "set":
        units["tax_unit_itemizes"] = np.ones(N, dtype=bool)
        tax_unit_inputs = ("tax_unit_itemizes",)
    results = _simulate(
        2026,
        units,
        tax_unit_inputs=tax_unit_inputs,
        person_inputs=("qualified_reit_and_ptp_income",),
        outputs=OUTPUTS_2026 + ("tax_unit_itemizes",),
    )
    itemizes = results["tax_unit_itemizes"]
    if choice == "calculated":
        # High-income itemizers with these deductions mostly itemize.
        assert itemizes.mean() > 0.5
    agi = units["adjusted_gross_income"]
    itemized = results["total_itemized_taxable_income_deductions"]
    qbid = results["qualified_business_income_deduction"]
    scale = agi + itemized + units["qualified_reit_and_ptp_income"]
    expected_qbid = np.minimum(
        0.2 * units["qualified_reit_and_ptp_income"],
        0.2 * np.maximum(0, agi - itemized),
    )
    _close(
        results["taxable_income_less_qbid"][itemizes],
        np.maximum(0, agi - itemized)[itemizes],
        scale[itemizes],
        "199A taxable income",
    )
    _close(qbid[itemizes], expected_qbid[itemizes], scale[itemizes], "QBID")
    expected = _section_68_reduction(itemized, agi - qbid, units["filing_status"])
    _close(
        results["itemized_taxable_income_deductions_reduction"][itemizes],
        expected[itemizes],
        scale[itemizes],
        "reduction",
    )
    assert np.any(expected[itemizes] > 0)

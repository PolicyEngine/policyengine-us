"""Invariants of Hawaii's overall limitation on itemized deductions and tips deduction.

HRS 235-2.4 keeps section 68 of the Internal Revenue Code operative with the
thresholds "operative for federal tax year 2009" ($166,800, or $83,400 for a
married individual filing separately). Act 35, SLH 2026 keeps section 68 "in
the form that it existed as of December 31, 2024" for taxable years beginning
after December 31, 2025, so the 3 percent and 80 percent rates and the section
68(c) exclusions (medical expenses, investment interest, casualty losses) do
not change in 2026. The Total Itemized Deductions Worksheet in the Form N-11
instructions implements this.

Act 35 also conforms Hawaii to the section 224 deduction for qualified tips
from 2026 (section 224(h) ends it after 2028).

Batches of tax units share one simulation per example. The tests check:

1. hi_itemized_deductions_reduction matches an independent restatement of
   worksheet lines 1-10, and hi_itemized_deductions equals line 11.
2. The reduction lies between 0 and both the 3 percent amount and 80 percent
   of the deductions that section 68(c) does not exclude, so the excluded
   deductions are never reduced.
3. The 2025 and 2026 results are identical for the same inputs.
4. Raising an excluded deduction leaves the reduction unchanged; raising any
   deduction never lowers the allowed amount; raising Hawaii AGI never lowers
   the reduction.
5. The tips deduction lies between 0 and the smaller of $25,000 and the
   qualified tips, never rises with Hawaii AGI, is zero for married filing
   separately, and is zero in 2025 and 2029. An independent oracle checks
   the $100 reduction for each whole $1,000 above the filing threshold.
6. Each single-category charitable deduction applies its percentage ceiling
   before the 2026 floor and uses Hawaii AGI in both calculations.
7. Miscellaneous expenses and repayments outside section 1341 share one
   2 percent floor through 2025 and allow no deduction in 2026.
"""

import numpy as np
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation

STATUSES = ("SINGLE", "JOINT", "SEPARATE", "HEAD_OF_HOUSEHOLD", "SURVIVING_SPOUSE")
# Worksheet line 7: "Enter $166,800 ($83,400 if married filing separately)".
THRESHOLD = 166_800
SEPARATE_THRESHOLD = 83_400

# Components of hi_total_itemized_deductions, split by whether section 68(c)
# excludes them. Investment interest and mortgage interest are person inputs
# that hi_interest_deduction adds up.
EXCLUDED = ("hi_medical_expense_deduction", "hi_casualty_loss_deduction")
EXCLUDED_PERSON = ("investment_interest_expense",)
OTHER = ("hi_charitable_deduction", "hi_salt_deduction", "hi_misc_deduction")
OTHER_PERSON = ("home_mortgage_interest",)
TAX_UNIT_COMPONENTS = EXCLUDED + OTHER
PERSON_COMPONENTS = EXCLUDED_PERSON + OTHER_PERSON
ALL_COMPONENTS = TAX_UNIT_COMPONENTS + PERSON_COMPONENTS
# PolicyEngine computes in float32, whose spacing near $1 million is 6 cents.
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


money = st.one_of(st.just(0.0), st.integers(1, 120_000).map(float))


@st.composite
def tax_units(draw):
    unit = {
        "filing_status": draw(st.sampled_from(STATUSES)),
        # Hawaii AGI near the thresholds, far above them, and negative.
        "hi_agi": float(
            draw(
                st.one_of(
                    st.integers(-50_000, 1_500_000),
                    st.integers(SEPARATE_THRESHOLD - 2, SEPARATE_THRESHOLD + 2),
                    st.integers(THRESHOLD - 2, THRESHOLD + 2),
                )
            )
        ),
    }
    only_excluded = draw(st.booleans())
    for name in ALL_COMPONENTS:
        excluded = name in EXCLUDED + EXCLUDED_PERSON
        unit[name] = draw(money) if excluded or not only_excluded else 0.0
    return unit


def _arrays(units):
    return {key: np.array([unit[key] for unit in units]) for key in units[0]}


def _simulate(year, units, outputs):
    period = str(year)
    people, groups, households = {}, {}, {}
    for i, unit in enumerate(units):
        person = f"p{i}"
        people[person] = {"age": {period: 45}}
        for name in PERSON_COMPONENTS:
            people[person][name] = {period: unit[name]}
        groups[f"t{i}"] = {
            "members": [person],
            "filing_status": {period: unit["filing_status"]},
            "hi_agi": {period: unit["hi_agi"]},
            **{name: {period: unit[name]} for name in TAX_UNIT_COMPONENTS},
        }
        households[f"h{i}"] = {"members": [person], "state_code": {period: "HI"}}
    simulation = Simulation(
        situation={"people": people, "tax_units": groups, "households": households}
    )
    return {name: simulation.calculate(name, period) for name in outputs}


def _thresholds(statuses):
    return np.where(statuses == "SEPARATE", SEPARATE_THRESHOLD, THRESHOLD)


def _split(units):
    excluded = sum(units[name] for name in EXCLUDED + EXCLUDED_PERSON)
    other = sum(units[name] for name in OTHER + OTHER_PERSON)
    return excluded, other


def _worksheet_line_10(units):
    """Total Itemized Deductions Worksheet, lines 1-10, restated."""
    excluded, other = _split(units)
    line_1 = excluded + other
    line_3 = excluded
    line_4 = np.where(line_3 < line_1, line_1 - line_3, 0)
    line_5 = line_4 * 0.8
    line_6 = units["hi_agi"]
    line_7 = _thresholds(units["filing_status"])
    line_8 = np.where(line_7 < line_6, line_6 - line_7, 0)
    line_9 = line_8 * 0.03
    return np.minimum(line_5, line_9)


LIMITATION_OUTPUTS = (
    "hi_total_itemized_deductions",
    "hi_itemized_deductions_reduction",
    "hi_itemized_deductions",
)

# A batch's cost is mostly per-variable overhead, so each example is a large
# batch and there are few examples.
SETTINGS = dict(
    max_examples=5,
    deadline=None,
    derandomize=True,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large],
)


@settings(**SETTINGS)
@given(st.lists(tax_units(), min_size=20, max_size=60))
def test_limitation_matches_the_worksheet_in_2025_and_2026(units):
    arrays = _arrays(units)
    excluded, other = _split(arrays)
    scale = excluded + other + np.abs(arrays["hi_agi"])
    line_10 = _worksheet_line_10(arrays)
    results = {}
    for year in (2025, 2026):
        run = _simulate(year, units, LIMITATION_OUTPUTS)
        results[year] = run
        total = run["hi_total_itemized_deductions"]
        reduction = run["hi_itemized_deductions_reduction"]
        allowed = run["hi_itemized_deductions"]
        _close(total, excluded + other, scale, f"{year} total")
        # 1. Worksheet lines 10 and 11.
        _close(reduction, line_10, scale, f"{year} line 10")
        _close(allowed, excluded + other - line_10, scale, f"{year} line 11")
        # 2. Bounds; excluded deductions are never reduced.
        agi_excess = np.maximum(
            0, arrays["hi_agi"] - _thresholds(arrays["filing_status"])
        )
        assert np.all(reduction >= 0)
        assert np.all(reduction <= 0.03 * agi_excess + _slack(scale))
        assert np.all(reduction <= 0.8 * other + _slack(scale))
        assert np.all(allowed >= excluded + 0.2 * other - _slack(scale))
    # 3. Act 35 leaves the limitation unchanged in 2026.
    for name in LIMITATION_OUTPUTS:
        np.testing.assert_array_equal(results[2025][name], results[2026][name])


def test_limitation_responds_to_components_and_income():
    rng = np.random.default_rng(2026)
    n = 200
    units = []
    for i in range(n):
        unit = {
            "filing_status": str(STATUSES[i % len(STATUSES)]),
            "hi_agi": float(np.round(rng.uniform(-20_000, 800_000), 2)),
        }
        for name in ALL_COMPONENTS:
            amount = float(np.round(rng.uniform(0, 60_000), 2))
            unit[name] = amount if rng.random() < 0.6 else 0.0
        units.append(unit)
    outputs = ("hi_itemized_deductions_reduction", "hi_itemized_deductions")
    base = _simulate(2026, units, outputs)
    arrays = _arrays(units)
    excluded, other = _split(arrays)
    scale = excluded + other + np.abs(arrays["hi_agi"]) + 10_000
    assert np.any(base["hi_itemized_deductions_reduction"] > 0)
    for name in ALL_COMPONENTS:
        raised = [dict(unit, **{name: unit[name] + 1_000}) for unit in units]
        run = _simulate(2026, raised, outputs)
        # 4. More of any deduction never lowers the allowed amount.
        assert np.all(
            run["hi_itemized_deductions"]
            >= base["hi_itemized_deductions"] - _slack(scale)
        ), name
        if name in EXCLUDED + EXCLUDED_PERSON:
            # Excluded deductions pass through without reduction.
            _close(
                run["hi_itemized_deductions_reduction"],
                base["hi_itemized_deductions_reduction"],
                scale,
                name,
            )
            _close(
                run["hi_itemized_deductions"],
                base["hi_itemized_deductions"] + 1_000,
                scale,
                name,
            )
    richer = [dict(unit, hi_agi=unit["hi_agi"] + 10_000) for unit in units]
    richer_reduction = _simulate(2026, richer, outputs)[
        "hi_itemized_deductions_reduction"
    ]
    assert np.all(
        richer_reduction >= base["hi_itemized_deductions_reduction"] - _slack(scale)
    )


def _tips_situation(units, period):
    people, groups, households = {}, {}, {}
    for i, unit in enumerate(units):
        person = f"p{i}"
        people[person] = {
            "age": {period: 30},
            "tip_income": {period: unit["tip_income"]},
            "treasury_tipped_occupation_code": {period: unit["occupation_code"]},
        }
        groups[f"t{i}"] = {
            "members": [person],
            "filing_status": {period: unit["filing_status"]},
            "hi_agi": {period: unit["hi_agi"]},
        }
        households[f"h{i}"] = {"members": [person], "state_code": {period: "HI"}}
    return {"people": people, "tax_units": groups, "households": households}


def test_tips_deduction_bounds_and_years():
    rng = np.random.default_rng(224)
    n = 250
    units = [
        {
            "filing_status": str(STATUSES[i % len(STATUSES)]),
            "hi_agi": float(np.round(rng.uniform(-10_000, 600_000), 2)),
            "tip_income": float(np.round(rng.uniform(0, 40_000), 2)),
            "occupation_code": int(rng.choice([0, 102])),
        }
        for i in range(n)
    ]
    units.extend(
        {
            "filing_status": status,
            "hi_agi": threshold + excess,
            "tip_income": 10_000.0,
            "occupation_code": 102,
        }
        for status in STATUSES
        for threshold in (300_000 if status == "JOINT" else 150_000,)
        for excess in (0, 500, 999, 1_000, 1_001, 1_999, 2_000)
    )
    arrays = _arrays(units)
    qualified = arrays["tip_income"] * (arrays["occupation_code"] > 0)
    separate = arrays["filing_status"] == "SEPARATE"
    for year in (2025, 2029):
        period = str(year)
        deduction = Simulation(situation=_tips_situation(units, period)).calculate(
            "hi_tip_income_deduction", period
        )
        # 5. No deduction before Act 35 or after section 224(h) ends it.
        assert np.all(deduction == 0), year
    for year in (2026, 2028):
        period = str(year)
        base = Simulation(situation=_tips_situation(units, period)).calculate(
            "hi_tip_income_deduction", period
        )
        richer_units = [dict(unit, hi_agi=unit["hi_agi"] + 5_000) for unit in units]
        richer = Simulation(situation=_tips_situation(richer_units, period)).calculate(
            "hi_tip_income_deduction", period
        )
        scale = qualified + np.abs(arrays["hi_agi"])
        expected = []
        richer_expected = []
        for unit in units:
            threshold = 300_000 if unit["filing_status"] == "JOINT" else 150_000
            tips = unit["tip_income"] if unit["occupation_code"] == 102 else 0
            for income_increase, oracle in ((0, expected), (5_000, richer_expected)):
                excess = max(0, unit["hi_agi"] + income_increase - threshold)
                whole_increments = int(excess // 1_000)
                allowed = max(0, min(25_000, tips) - 100 * whole_increments)
                oracle.append(0 if unit["filing_status"] == "SEPARATE" else allowed)
        _close(base, np.array(expected), scale, f"{year} whole increments")
        _close(richer, np.array(richer_expected), scale, f"{year} richer increments")
        assert np.all(base >= 0)
        assert np.all(base <= np.minimum(25_000, qualified) + _slack(scale))
        assert np.all(base[separate] == 0)
        assert np.all(richer <= base + _slack(scale))
        assert np.any(base > 0)


CHARITY_CATEGORIES = (
    ("resolved_charitable_cash_donations_50_pct", 0.60),
    ("resolved_charitable_non_cash_donations_50_pct", 0.50),
    ("resolved_charitable_cash_donations_non_50_pct", 0.30),
    ("resolved_charitable_non_cash_donations_non_50_pct", 0.30),
    ("resolved_charitable_capital_gain_donations_50_pct", 0.30),
    ("resolved_charitable_capital_gain_donations_non_50_pct", 0.20),
)


def _charity_situation(cases, period):
    people, groups, households = {}, {}, {}
    for i, (agi, donation, category, _) in enumerate(cases):
        person = f"p{i}"
        people[person] = {
            "age": {period: 45},
            **{
                name: {period: donation if name == category else 0}
                for name, _ in CHARITY_CATEGORIES
            },
        }
        groups[f"t{i}"] = {
            "members": [person],
            "filing_status": {period: "SINGLE"},
            "hi_agi": {period: agi},
            "adjusted_gross_income": {period: agi + 100_000},
        }
        households[f"h{i}"] = {"members": [person], "state_code": {period: "HI"}}
    return {"people": people, "tax_units": groups, "households": households}


@settings(**SETTINGS)
@given(
    st.lists(
        st.tuples(st.integers(-50_000, 400_000), st.integers(0, 300_000)),
        min_size=8,
        max_size=20,
    )
)
def test_charity_single_category_ceilings_precede_the_2026_floor(amounts):
    amounts = amounts + [(-10_000, 1_000), (0, 1_000), (50_000, 40_000), (100_000, 300)]
    cases = [
        (agi, donation, category, ceiling)
        for agi, donation in amounts
        for category, ceiling in CHARITY_CATEGORIES
    ]
    scale = np.array([abs(agi) + donation for agi, donation, _, _ in cases])
    for year in (2025, 2026):
        period = str(year)
        deduction = Simulation(situation=_charity_situation(cases, period)).calculate(
            "hi_charitable_deduction", period
        )
        expected = []
        for agi, donation, _, ceiling in cases:
            positive_agi = max(0, agi)
            allowed_before_floor = min(donation, ceiling * positive_agi)
            floor = 0.005 * positive_agi if year == 2026 else 0
            expected.append(max(0, allowed_before_floor - floor))
        _close(
            deduction, np.array(expected), scale, f"{year} charity ceiling and floor"
        )


def _misc_situation(units, period):
    people, groups, households = {}, {}, {}
    for i, unit in enumerate(units):
        person = f"p{i}"
        people[person] = {
            "age": {period: 45},
            "tax_preparation_fees": {period: unit["expenses"]},
        }
        groups[f"t{i}"] = {
            "members": [person],
            "hi_agi": {period: unit["hi_agi"]},
            "hi_claim_of_right_repayment": {period: unit["repayment"]},
        }
        households[f"h{i}"] = {"members": [person], "state_code": {period: "HI"}}
    return {"people": people, "tax_units": groups, "households": households}


def test_miscellaneous_expenses_and_repayments_share_one_floor():
    rng = np.random.default_rng(67)
    units = [
        {
            "hi_agi": float(rng.integers(-20_000, 250_000)),
            "expenses": float(rng.integers(0, 10_000)),
            "repayment": float(rng.integers(0, 3_001)),
        }
        for _ in range(120)
    ]
    units.extend(
        {"hi_agi": 50_000, "expenses": expenses, "repayment": repayment}
        for expenses, repayment in (
            (800, 800),
            (800, 1_500),
            (0, 1_500),
            (800, 0),
            (0, 0),
            (1_000, 0),
            (0, 1_000),
            (500, 500),
        )
    )
    arrays = _arrays(units)
    scale = np.abs(arrays["hi_agi"]) + arrays["expenses"] + arrays["repayment"]
    for year in (2025, 2026):
        period = str(year)
        simulation = Simulation(situation=_misc_situation(units, period))
        misc = simulation.calculate("hi_misc_deduction", period)
        repayment = simulation.calculate("hi_claim_of_right_deduction", period)
        eligible = simulation.calculate(
            "hi_claim_of_right_section_1341_eligible", period
        )
        assert np.all(~eligible)
        expected = np.array(
            [
                max(
                    0,
                    unit["expenses"]
                    + unit["repayment"]
                    - 0.02 * max(unit["hi_agi"], 0),
                )
                for unit in units
            ]
        )
        if year == 2026:
            assert np.all(misc == 0)
            assert np.all(repayment == 0)
            expected.fill(0)
        _close(misc + repayment, expected, scale, f"{year} pooled miscellaneous floor")

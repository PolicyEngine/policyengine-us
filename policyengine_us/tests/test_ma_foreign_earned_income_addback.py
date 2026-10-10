"""Property and differential tests for the Massachusetts addition of foreign
earned income excluded under section 911.

M.G.L. c. 62 s. 2(a)(1)(C) adds to federal gross income "Earned income from
foreign sources excluded under section nine hundred and eleven of the Code",
and s. 2(b)(2) makes Part B gross income the Massachusetts gross income "not
included in Part A or Part C gross income". Part B removes the dividends and
positive net capital gain included in federal gross income; capital losses do
not reduce Part B under s. 2(d)(1)(M). Massachusetts Part A and Part C netting
can differ from federal netting, so their separate gross amounts are not the
subtraction used to isolate Part B. The excluded amount is
`ma_foreign_earned_income_exclusion_addback` (Form 2555 line 43). It defaults
to `foreign_earned_income_exclusion`, floored at zero, and can be entered
directly. Before this change, `ma_gross_income` subtracted the exclusion instead.

Write B for federal gross income plus `ma_gross_income_loss_adjustment`, less
taxable Social Security, state and local tax refunds and exempt public
pensions. Properties for nonnegative exclusions and entered addbacks:

1. Massachusetts gross income is max(0, B + addback), where the addback is
   the entered amount or, when none is entered, the nonnegative exclusion.
   Against the formula before this change, max(0, B - exclusion), gross income
   rises by the addback plus the exclusion wherever neither zero floor binds.
   Outside Massachusetts, or with no exclusion and no entered addback, gross
   income, Part B and the taxes are bit-for-bit unchanged. Massachusetts tax
   before credits never falls.
2. Raising the addback by D leaves federal gross income, the loss adjustment
   and Parts A and C unchanged, and leaves AGI unchanged for these
   households, none of which has an AGI item that reads the exclusion. It
   raises gross income by max(0, B + addback + D) - max(0, B + addback) and
   Part B by the matching change past its own floor, so by exactly D where
   neither floor binds. The same holds when the exclusion rises and no
   addback is entered.
3. Gross income is never negative, is zero while B + addback is at most
   zero, equals B + addback where the addback lifts a negative B above zero,
   and never falls as the addback rises.
4. An entered addback, including zero, replaces the default. An entered zero
   beside a positive exclusion gives the Massachusetts gross income results
   of a household with no exclusion, and an entered amount gives the same
   results whatever the exclusion.
"""

import gc
from functools import lru_cache

import numpy as np
import pytest

from policyengine_us import CountryTaxBenefitSystem, Simulation

# Hypothesis is a dev extra; skip rather than fail collection without it.
hypothesis = pytest.importorskip("hypothesis")
st = pytest.importorskip("hypothesis.strategies")

YEARS = [2025, 2026]
DELTA = 7_500

GROSS = [
    "ma_foreign_earned_income_exclusion_addback",
    "ma_gross_income",
    "ma_part_a_gross_income",
    "ma_part_b_gross_income",
    "ma_part_c_gross_income",
]
TAX_UNIT_COMPONENTS = ["adjusted_gross_income", "ma_gross_income_loss_adjustment"]
PERSON_COMPONENTS = [
    "irs_gross_income",
    "taxable_social_security",
    "salt_refund_income",
    "taxable_public_pension_income",
]
TAXES = [
    "ma_income_tax_before_credits",
    "ma_income_tax",
    "state_income_tax",
    "income_tax",
]
# Federal and Part A and C amounts the addback must not move.
FIXED_BY_ADDBACK = [
    "irs_gross_income",
    "adjusted_gross_income",
    "ma_gross_income_loss_adjustment",
    "ma_part_a_gross_income",
    "ma_part_c_gross_income",
]


def household(state, status, wages, exclusion, **amounts):
    return {
        "state": state,
        "status": status,
        "wages": wages,
        "spouse_wages": amounts.get("spouse_wages", 0),
        "dividends": amounts.get("dividends", 0),
        "short_term_gains": amounts.get("short_term_gains", 0),
        "long_term_gains": amounts.get("long_term_gains", 0),
        "self_employment": amounts.get("self_employment", 0),
        "public_pension": amounts.get("public_pension", 0),
        "salt_refund": amounts.get("salt_refund", 0),
        "exclusion": exclusion,
        "entered": amounts.get("entered"),
    }


def build_situation(households, year):
    people, tax_units, marital_units = {}, {}, {}
    groups = {"households": {}, "spm_units": {}, "families": {}}
    person_tax_unit = []
    for i, h in enumerate(households):
        head = f"head_{i}"
        people[head] = {
            "age": {year: 45},
            "employment_income": {year: h["wages"]},
            "qualified_dividend_income": {year: h["dividends"]},
            "short_term_capital_gains": {year: h["short_term_gains"]},
            "long_term_capital_gains": {year: h["long_term_gains"]},
            "self_employment_income": {year: h["self_employment"]},
            "taxable_public_pension_income": {year: h["public_pension"]},
            "salt_refund_income": {year: h["salt_refund"]},
        }
        members = [head]
        person_tax_unit.append(i)
        if h["status"] == "JOINT":
            spouse = f"spouse_{i}"
            people[spouse] = {
                "age": {year: 45},
                "employment_income": {year: h["spouse_wages"]},
            }
            members.append(spouse)
            person_tax_unit.append(i)
        marital_units[f"marital_unit_{i}"] = {"members": list(members)}
        tax_unit = {
            "members": members,
            # Set for every tax unit: an input given to only some of them
            # leaves the rest at the default (single).
            "filing_status": {year: h["status"]},
            "foreign_earned_income_exclusion": {year: h["exclusion"]},
        }
        if h["entered"] is not None:
            tax_unit["ma_foreign_earned_income_exclusion_addback"] = {
                year: h["entered"]
            }
        tax_units[f"tax_unit_{i}"] = tax_unit
        groups["households"][f"household_{i}"] = {
            "members": members,
            "state_code": {year: h["state"]},
        }
        groups["spm_units"][f"spm_unit_{i}"] = {"members": members}
        groups["families"][f"family_{i}"] = {"members": members}
    situation = {
        "people": people,
        "tax_units": tax_units,
        "marital_units": marital_units,
        **groups,
    }
    return situation, np.array(person_tax_unit)


def before_the_addition():
    """A reform restoring `ma_gross_income` as it was before this change."""
    from policyengine_core.reforms import Reform

    from policyengine_us.model_api import (
        USD,
        YEAR,
        StateCode,
        TaxUnit,
        Variable,
        add,
        max_,
    )

    class ma_gross_income(Variable):
        value_type = float
        entity = TaxUnit
        label = "MA gross income before the section 911 addition"
        unit = USD
        definition_period = YEAR
        defined_for = StateCode.MA

        def formula(tax_unit, period, parameters):
            federal_gross_income = add(tax_unit, period, ["irs_gross_income"])
            loss_adjustment = tax_unit("ma_gross_income_loss_adjustment", period)
            foreign_earned_income = tax_unit("foreign_earned_income_exclusion", period)
            social_security_in_agi = add(tax_unit, period, ["taxable_social_security"])
            salt_refund_income = add(tax_unit, period, ["salt_refund_income"])
            public_pension = add(tax_unit, period, ["taxable_public_pension_income"])
            deductions = (
                foreign_earned_income
                + social_security_in_agi
                + salt_refund_income
                + public_pension
            )
            return max_(0, federal_gross_income + loss_adjustment - deductions)

    class reform(Reform):
        def apply(self):
            self.update_variable(ma_gross_income)

    return reform


@lru_cache(maxsize=None)
def system_before_the_addition():
    """Built once: constructing a reformed system takes seconds."""
    return CountryTaxBenefitSystem(reform=before_the_addition())


@pytest.fixture(scope="module", autouse=True)
def release_cached_systems():
    """Release the reformed system and cached results when the module ends,
    so the rest of the pytest process does not keep a second full system
    resident."""
    yield
    system_before_the_addition.cache_clear()
    _calculate.cache_clear()
    gc.collect()


def calculate_batch(households, year, before, taxes):
    situation, person_tax_unit = build_situation(households, year)
    simulation = Simulation(
        situation=situation,
        **({"tax_benefit_system": system_before_the_addition()} if before else {}),
    )
    results = {}
    for v in GROSS + TAX_UNIT_COMPONENTS + (TAXES if taxes else []):
        results[v] = np.asarray(simulation.calculate(v, year), dtype=float)
    for v in PERSON_COMPONENTS:
        values = np.asarray(simulation.calculate(v, year), dtype=float)
        results[v] = np.bincount(
            person_tax_unit, weights=values, minlength=len(households)
        )
    return results


def freeze(households):
    return tuple(tuple(sorted(h.items())) for h in households)


@lru_cache(maxsize=None)
def _calculate(frozen, year, before, taxes):
    households = [dict(h) for h in frozen]
    # An input given to only some tax units in a batch sets the rest to the
    # default (zero), not to the value the formula would compute, so
    # households with and without an entered addback run as separate batches.
    entered = np.array([h["entered"] is not None for h in households])
    results = {}
    for group in [entered, ~entered]:
        if not group.any():
            continue
        batch = calculate_batch(
            [h for h, g in zip(households, group) if g], year, before, taxes
        )
        for v, values in batch.items():
            results.setdefault(v, np.empty(len(households)))
            results[v][group] = values
    return results


def calculate(households, year, before=False, taxes=False):
    return _calculate(freeze(households), year, before, taxes)


def calculate_variants(variants, year):
    """Several versions of the same households, run as one batch.

    Households are independent, so stacking the versions in one simulation
    gives each the results it would get alone, with fewer simulations.
    """
    results = calculate([h for variant in variants for h in variant], year)
    sizes = np.cumsum([0] + [len(variant) for variant in variants])
    return [
        {v: values[start:end] for v, values in results.items()}
        for start, end in zip(sizes[:-1], sizes[1:])
    ]


def tolerance(*amounts):
    """One cent, plus the rounding of single-precision arithmetic.

    The model stores amounts as 32-bit floats, which carry about seven
    significant digits.
    """
    return 0.01 + 5e-7 * np.max(np.abs(np.array(amounts, dtype=float)), axis=0)


def in_massachusetts(households):
    return np.array([h["state"] == "MA" for h in households])


def expected_addback(households):
    """The entered addback, or else the exclusion (Massachusetts only)."""
    return np.array(
        [
            (h["exclusion"] if h["entered"] is None else h["entered"])
            if h["state"] == "MA"
            else 0
            for h in households
        ],
        dtype=float,
    )


def exclusions(households):
    return np.array([h["exclusion"] for h in households], dtype=float)


def federally_included_capital_income(households):
    """Independent capital-income reference from the household input amounts.

    This fixture puts all dividends and gains on the head; spouses have only
    wages, and no capital gain distributions are supplied outside Schedule D.
    """
    # M.G.L. c. 62 § 2(b)(2) excludes capital income from Part B, and
    # § 2(d)(1)(M) disallows the federal capital-loss deduction. Remove the
    # dividends and positive net gain included federally, rather than Part A
    # and Part C amounts whose Massachusetts loss netting can differ (#9954).
    return np.array(
        [
            h["dividends"] + max(0, h["short_term_gains"] + h["long_term_gains"])
            for h in households
        ],
        dtype=float,
    )


def base_income(results):
    """B: federal gross income and the loss adjustment, less the exclusions."""
    return (
        results["irs_gross_income"]
        + results["ma_gross_income_loss_adjustment"]
        - results["taxable_social_security"]
        - results["salt_refund_income"]
        - results["taxable_public_pension_income"]
    )


def with_entered(households, change):
    """The same households with the entered addback set from each one."""
    return [{**h, "entered": change(h)} for h in households]


def default_addback(h):
    return h["exclusion"] if h["entered"] is None else h["entered"]


def check_gross_income_adds_back_foreign_earnings(households, year):
    law = calculate(households, year, taxes=True)
    before = calculate(households, year, before=True, taxes=True)
    ma = in_massachusetts(households)
    addback = expected_addback(households)
    exclusion = exclusions(households)
    base = base_income(law)

    # The default is the exclusion; an entered amount replaces it.
    slack = tolerance(addback, law["ma_foreign_earned_income_exclusion_addback"])
    assert (
        np.abs(law["ma_foreign_earned_income_exclusion_addback"][ma] - addback[ma])
        <= slack[ma]
    ).all()

    # Gross income is max(0, B + addback) in Massachusetts and zero elsewhere.
    gross = np.where(ma, np.maximum(0, base + addback), 0)
    slack = tolerance(base, addback, gross, law["ma_gross_income"])
    assert (np.abs(law["ma_gross_income"] - gross) <= slack).all()

    # Differential: the formula before this change subtracted the exclusion.
    gross_before = np.where(ma, np.maximum(0, base - exclusion), 0)
    assert (np.abs(before["ma_gross_income"] - gross_before) <= slack).all()
    unfloored = ma & (base - exclusion >= 0) & (base + addback >= 0)
    change = law["ma_gross_income"] - before["ma_gross_income"]
    assert (
        np.abs(change - (addback + exclusion))[unfloored] <= 2 * slack[unfloored]
    ).all()
    assert (law["ma_gross_income"] >= before["ma_gross_income"]).all()

    # Massachusetts tax before credits never falls when gross income rises.
    assert (
        law["ma_income_tax_before_credits"]
        >= before["ma_income_tax_before_credits"]
        - tolerance(law["ma_income_tax_before_credits"])
    ).all()

    # Outside Massachusetts, or with nothing excluded or entered, nothing
    # changes, bit for bit.
    untouched = ~ma | ((exclusion == 0) & (addback == 0))
    for v in ["ma_gross_income", "ma_part_b_gross_income"] + TAXES:
        assert np.array_equal(law[v][untouched], before[v][untouched]), v
    assert not law["ma_gross_income"][~ma].any()
    return law, before, unfloored, untouched


def check_foreign_earnings_enter_part_b_only(households, year):
    ma = in_massachusetts(households)
    for low_households, high_households in [
        # Raise an entered addback; the exclusion stays put.
        (
            with_entered(households, default_addback),
            with_entered(households, lambda h: default_addback(h) + DELTA),
        ),
        # Raise the exclusion with nothing entered.
        (
            [{**h, "entered": None} for h in households],
            [
                {**h, "exclusion": h["exclusion"] + DELTA, "entered": None}
                for h in households
            ],
        ),
    ]:
        low, high = calculate_variants([low_households, high_households], year)
        for v in FIXED_BY_ADDBACK:
            assert np.array_equal(low[v], high[v]), v
        base = base_income(low)
        addback = expected_addback(low_households)
        gross_change = np.where(
            ma,
            np.maximum(0, base + addback + DELTA) - np.maximum(0, base + addback),
            0,
        )
        slack = tolerance(base, addback, high["ma_gross_income"])
        assert (
            np.abs(high["ma_gross_income"] - low["ma_gross_income"] - gross_change)
            <= 2 * slack
        ).all()
        # c.62 § 2(b)(2), § 2(d)(1)(M): remove the capital income included
        # federally; different Massachusetts netting cannot reduce Part B.
        capital_income = federally_included_capital_income(low_households)
        residual_low = low["ma_gross_income"] - capital_income
        residual_high = high["ma_gross_income"] - capital_income
        part_b_change = np.maximum(0, residual_high) - np.maximum(0, residual_low)
        assert (
            np.abs(
                high["ma_part_b_gross_income"]
                - low["ma_part_b_gross_income"]
                - part_b_change
            )
            <= 2 * slack
        ).all()
        # Where neither floor binds, both rise by exactly the change.
        outside = ma & (base + addback >= 0) & (residual_low >= 0)
        for v in ["ma_gross_income", "ma_part_b_gross_income"]:
            rise = high[v] - low[v]
            assert (np.abs(rise - DELTA)[outside] <= 2 * slack[outside]).all(), v
        assert not (high["ma_gross_income"] - low["ma_gross_income"])[~ma].any()
    return outside


def check_addition_respects_zero_floor(households, year):
    ma = in_massachusetts(households)
    law = calculate(households, year, taxes=True)
    base = base_income(law)
    addback = expected_addback(households)
    assert (law["ma_gross_income"] >= 0).all()
    assert (law["ma_part_b_gross_income"] >= 0).all()
    floored = ma & (base + addback <= 0)
    assert not law["ma_gross_income"][floored].any()
    # The addition offsets losses before the floor applies: where B is
    # negative but B + addback is not, gross income is B + addback.
    lifted = ma & (base < 0) & (base + addback > 0)
    slack = tolerance(base, addback, law["ma_gross_income"])
    assert (
        np.abs(law["ma_gross_income"] - (base + addback))[lifted] <= slack[lifted]
    ).all()
    # Gross income never falls as the addback rises. Rounding is monotone,
    # so this holds exactly.
    steps = [(0, 0), (0.5, 0), (1, 0), (1, 10_000), (2, 50_000)]
    scaled = calculate_variants(
        [
            with_entered(households, lambda h: scale * default_addback(h) + shift)
            for scale, shift in steps
        ],
        year,
    )
    for lower, higher, step in zip(scaled, scaled[1:], steps[1:]):
        assert (higher["ma_gross_income"] >= lower["ma_gross_income"]).all(), step
    return floored, lifted


def check_entered_addback_overrides_default(households, year):
    ma = in_massachusetts(households)
    zero_entered, entered, entered_without_exclusion = calculate_variants(
        [
            with_entered(households, lambda h: 0),
            with_entered(households, lambda h: 12_345),
            [{**h, "exclusion": 0, "entered": 12_345} for h in households],
        ],
        year,
    )
    default, no_exclusion = calculate_variants(
        [
            [{**h, "entered": None} for h in households],
            [{**h, "exclusion": 0, "entered": None} for h in households],
        ],
        year,
    )
    # An entered zero beside a positive exclusion counts nothing, as with no
    # exclusion at all.
    assert not zero_entered["ma_foreign_earned_income_exclusion_addback"].any()
    for v in GROSS[1:]:
        assert np.array_equal(zero_entered[v], no_exclusion[v]), v
    # An entered amount does not depend on the exclusion.
    for v in GROSS + TAX_UNIT_COMPONENTS:
        assert np.array_equal(entered[v], entered_without_exclusion[v]), v
    assert (entered["ma_foreign_earned_income_exclusion_addback"][ma] == 12_345).all()
    # The default follows the exclusion.
    assert np.array_equal(
        default["ma_foreign_earned_income_exclusion_addback"],
        np.where(ma, exclusions(households), 0),
    )


GRID = [
    household(
        state,
        status,
        wages,
        exclusion,
        spouse_wages=40_000 if status == "JOINT" else 0,
        dividends=dividends,
        short_term_gains=short_term_gains,
        long_term_gains=long_term_gains,
        self_employment=self_employment,
        public_pension=public_pension,
        salt_refund=salt_refund,
        entered=entered,
    )
    for state in ("MA", "NY")
    for status in ("SINGLE", "JOINT")
    for wages in (0, 60_000)
    for dividends, short_term_gains, long_term_gains in (
        (0, 0, 0),
        (6_000, 3_000, 4_000),
        (0, 5_000, -2_000),
    )
    for self_employment in (0, -150_000)
    for public_pension, salt_refund in ((0, 0), (10_000, 2_000))
    for exclusion in (0, 10_000, 130_000)
    for entered in (None, 0, 25_000)
]


@pytest.mark.parametrize("year", YEARS)
def test_ma_gross_income_adds_back_foreign_earnings(year):
    law, before, unfloored, untouched = check_gross_income_adds_back_foreign_earnings(
        GRID, year
    )
    # The grid reaches households the addition changes and ones it does not.
    assert (unfloored & (expected_addback(GRID) > 0)).any()
    assert (
        law["ma_income_tax_before_credits"] > before["ma_income_tax_before_credits"]
    ).any()
    assert untouched.any() and (~untouched).any()


@pytest.mark.parametrize("year", YEARS)
def test_ma_foreign_earnings_enter_part_b_only(year):
    outside = check_foreign_earnings_enter_part_b_only(GRID, year)
    assert outside.any()


@pytest.mark.parametrize("year", YEARS)
def test_ma_foreign_earnings_addition_respects_zero_floor(year):
    floored, lifted = check_addition_respects_zero_floor(GRID, year)
    # The grid reaches households held at the floor and ones the addition
    # lifts off it.
    assert floored.any() and lifted.any()


@pytest.mark.parametrize("year", YEARS)
def test_explicit_zero_addback_overrides_fallback(year):
    check_entered_addback_overrides_default(GRID, year)


def test_review_example():
    # 2025, single, $32,000 of wages, $6,000 of dividends, $3,000 of
    # short-term and $4,000 of long-term gains, and a $10,000 exclusion.
    # Federal gross income is $45,000; Massachusetts gross income is $55,000,
    # with $9,000 in Part A, $4,000 in Part C and $42,000 in Part B. Before
    # this change it was $35,000, with $22,000 in Part B.
    example = household(
        "MA",
        "SINGLE",
        32_000,
        10_000,
        dividends=6_000,
        short_term_gains=3_000,
        long_term_gains=4_000,
    )
    law, before, _, _ = check_gross_income_adds_back_foreign_earnings([example], 2025)
    assert law["irs_gross_income"][0] == 45_000
    assert law["ma_gross_income"][0] == 55_000
    assert law["ma_part_a_gross_income"][0] == 9_000
    assert law["ma_part_c_gross_income"][0] == 4_000
    assert law["ma_part_b_gross_income"][0] == 42_000
    assert before["ma_gross_income"][0] == 35_000
    assert before["ma_part_b_gross_income"][0] == 22_000


household_strategy = st.fixed_dictionaries(
    {
        "state": st.sampled_from(["MA", "MA", "MA", "NY"]),
        "status": st.sampled_from(["SINGLE", "JOINT"]),
        "wages": st.integers(0, 400_000),
        "spouse_wages": st.one_of(st.just(0), st.integers(1, 200_000)),
        "dividends": st.one_of(st.just(0), st.integers(1, 100_000)),
        "short_term_gains": st.one_of(st.just(0), st.integers(-30_000, 100_000)),
        "long_term_gains": st.one_of(st.just(0), st.integers(-30_000, 300_000)),
        "self_employment": st.one_of(st.just(0), st.integers(-300_000, 150_000)),
        "public_pension": st.one_of(st.just(0), st.integers(1, 80_000)),
        "salt_refund": st.one_of(st.just(0), st.integers(1, 10_000)),
        "exclusion": st.one_of(st.just(0), st.integers(1, 300_000)),
        "entered": st.one_of(st.none(), st.just(0), st.integers(1, 300_000)),
    }
)

SETTINGS = dict(
    max_examples=5,
    deadline=None,
    derandomize=True,
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
    check_gross_income_adds_back_foreign_earnings(households, year)
    check_foreign_earnings_enter_part_b_only(households, year)
    check_addition_respects_zero_floor(households, year)
    check_entered_addback_overrides_default(households, year)

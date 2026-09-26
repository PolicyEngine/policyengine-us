"""Arkansas regular income tax schedule: differential and invariant tests.

`ar_main_income_tax` (shared by the indiv and joint tax variables and
`ar_uses_low_income_tax_tables`) has two paths:

- Years with a published DFA Indexed Tax Brackets card (2021-2025) compute
  `rate.calc(ti) * ti - reduction.calc(ti)` from two single_amount scales
  whose rows are shared across years, so a mis-keyed row in one year's column
  (a skipped DFA row, an ignored asterisked two-row range, a duplicated
  threshold) silently shifts every later bracket.
- Later years apply the statutory tables of A.C.A. 26-51-201(a)(4) (Act 1 of
  2026): (A) marginal rates up to the high-income threshold, and above it the
  (B) marginal rates less the (C) bracket adjustment. 26-51-201(a)(5) and
  (d)(1) index every bracket bound each year, "rounding to the nearest one
  hundred dollars ($100)"; the (C) dollar amounts are not bracket bounds and
  stay fixed. The reduction is derived from the same indexed tables, so it
  moves with the thresholds (a stored reduction would not).

Differential tests compare every integer taxable income against an
independent transcription of each year's source:

- 2021-2025: DFA Indexed Tax Brackets cards, e.g.
  https://www.dfa.arkansas.gov/wp-content/uploads/2025_TaxBrackets.pdf#page=1
  Rows from the top of the flat rate bracket upward form a $100 ladder whose
  minus adjustment falls $10 per row. Asterisked rows span $200, so the next
  row's start is skipped.
- 2026: Act 1 of 2026 (1st Extraordinary Session), A.C.A. 26-51-201(a)(4).
- 2027-2035: Act 1 of 2026's tables with every bracket bound indexed from
  2026 by PolicyEngine's uprating index and rounded to the nearest $100.

Invariants:
- reduction.yaml rows carry strictly increasing finite thresholds, with every
  .inf row after them (published years).
- At every integer taxable income, tax is non-negative and never falls as
  income rises (2021-2040, 2050, 2075, 2100), except where the statute's own
  (A) and (B)-(C) tables meet. In 2026 that seam drops: (a)(4)(A) taxes
  $94,700 at $3,136.70, while (a)(4)(B) less the $290 (a)(4)(C) adjustment
  taxes $94,701 at $3,134.04. Once indexing raises the (A) bounds, the seam
  rises instead.
- The (C) ladder starts at the high-income threshold, its bounds strictly
  increase, and its amounts stay Act 1's $290-$10 steps; the (B) top rate
  equals the (A) top rate (2026-2040, 2050, 2075, 2100).
- Property tests over random tables: the derived (A) tax equals
  rate x income - the sum of (rate step x row start), is continuous at every
  row start, and tax never falls within either regime.
- A reform to the rate table in a projected year keeps the schedule
  continuous, because the reduction is derived rather than stored.
"""

from types import SimpleNamespace

import numpy as np
import pytest
from policyengine_core.taxscales import MarginalRateTaxScale, SingleAmountTaxScale

from policyengine_us.system import system
from policyengine_us.variables.gov.states.ar.tax.income.ar_income_tax_helpers import (
    ar_main_income_tax,
)

P = system.parameters.gov.states.ar.tax.income.rates.main
UPRATING = system.parameters.gov.irs.uprating
PUBLISHED_YEARS = range(2021, 2026)
SOURCE_YEARS = range(2021, 2036)
LONG_RUN_YEARS = [2050, 2075, 2100]
INVARIANT_YEARS = list(range(2021, 2041)) + LONG_RUN_YEARS
DERIVED_YEARS = list(range(2026, 2041)) + LONG_RUN_YEARS
TAXABLE_INCOME = np.concatenate(
    [np.arange(0, 150_001, dtype=float), [250_000.0, 1_000_000.0]]
)


def ladder(first_threshold, last_threshold, first_adjustment, wide_rows=()):
    """$100 rows from first to last threshold, $10 less adjustment per row.

    `wide_rows` are the starts of asterisked rows that span $200.
    """
    skipped = {start + 100 for start in wide_rows}
    starts = [
        t for t in range(first_threshold, last_threshold + 1, 100) if t not in skipped
    ]
    return [(t, first_adjustment - 10 * k) for k, t in enumerate(starts)]


# (From, rate, minus adjustment) as printed on each DFA card.
DFA_CARDS = {
    2021: [
        (0, 0, 0),
        (4_800, 0.02, 95.98),
        (9_500, 0.03, 190.97),
        (14_300, 0.034, 248.17),
        (23_600, 0.05, 439.96),
        (39_700, 0.059, 797.25),
        (84_501, 0.059, 687.50),
        (85_501, 0.059, 587.50),
        (86_501, 0.059, 487.50),
        (87_901, 0.059, 387.50),
        (89_001, 0.059, 287.50),
        (90_101, 0.059, 247.50),
    ],
    2022: [
        (0, 0, 0),
        (5_100, 0.02, 101.98),
        (10_300, 0.03, 204.97),
        (14_700, 0.034, 263.77),
        (24_300, 0.049, 628.25),
    ]
    + [
        (t, 0.049, a)
        for t, a in ladder(87_001, 91_801, 627.20, wide_rows=(87_401, 90_901))
    ],
    2023: [
        (0, 0, 0),
        (5_300, 0.02, 105.98),
        (10_600, 0.03, 211.97),
        (15_100, 0.034, 272.37),
        (25_000, 0.047, 597.35),
    ]
    + [
        (t, 0.047, a)
        for t, a in ladder(89_601, 94_201, 583.70, wide_rows=(90_001, 90_901, 93_601))
    ],
    2024: [
        (0, 0, 0),
        (5_500, 0.02, 109.98),
        (10_900, 0.03, 218.97),
        (15_600, 0.034, 281.37),
        (25_700, 0.039, 409.86),
    ]
    + [(t, 0.039, a) for t, a in ladder(92_301, 95_501, 397.40, wide_rows=(94_301,))],
    2025: [
        (0, 0, 0),
        (5_600, 0.02, 111.98),
        (11_200, 0.03, 223.97),
        (16_000, 0.034, 287.97),
        (26_400, 0.039, 419.96),
    ]
    + [(t, 0.039, a) for t, a in ladder(94_701, 97_801, 399.30)],
}


def card_tax(year, ti):
    rows = DFA_CARDS[year]
    starts = np.array([r[0] for r in rows])
    i = np.searchsorted(starts, ti, side="right") - 1
    rate = np.array([r[1] for r in rows])[i]
    adjustment = np.array([r[2] for r in rows])[i]
    return rate * ti - adjustment


def act_1_of_2026_tax(ti):
    # (a)(4)(A), net income <= $94,700: marginal rates from each row's "From".
    low = sum(
        rate * np.clip(ti - start, 0, end - start)
        for start, end, rate in [
            (5_600, 11_200, 0.02),
            (11_200, 16_000, 0.03),
            (16_000, 26_400, 0.034),
            (26_400, np.inf, 0.037),
        ]
    )
    # (a)(4)(B), net income > $94,700: 2% on the first $4,700, 3.7% above.
    high = 0.02 * 4_700 + 0.037 * (ti - 4_700)
    # (a)(4)(C): $290 at $94,701-$94,800, $10 less per $100, $0 from $97,601.
    step = np.floor((np.ceil(ti) - 94_701) / 100)
    high -= np.where(ti <= 97_600, 290 - 10 * step, 0)
    return np.where(ti <= 94_700, low, high)


# Act 1 of 2026, A.C.A. 26-51-201(a)(4): (A) row starts and rates; the
# (A)/(B) threshold; the top of (B)'s 2% row; and each (C) row as the bound it
# starts above ("From" - 1) with its bracket adjustment amount.
ACT_1_TABLE_A = [(5_600, 0.02), (11_200, 0.03), (16_000, 0.034), (26_400, 0.037)]
ACT_1_THRESHOLD = 94_700
ACT_1_TABLE_B_2_PERCENT_TOP = 4_700
ACT_1_LADDER = [(94_700 + 100 * k, 290 - 10 * k) for k in range(29)] + [(97_600, 0)]


def nearest_100(amount):
    # 26-51-201(d)(1): "rounding to the nearest one hundred dollars ($100)".
    return np.floor(amount / 100 + 0.5) * 100


def indexed_act_1_of_2026_tax(year, ti):
    """Act 1 of 2026's tables, every bracket bound indexed from 2026."""
    factor = UPRATING(f"{year}-01-01") / UPRATING("2026-01-01")
    starts = [nearest_100(start * factor) for start, _ in ACT_1_TABLE_A]
    ends = starts[1:] + [np.inf]
    rates = [rate for _, rate in ACT_1_TABLE_A]
    table_a = sum(
        rate * np.clip(ti - start, 0, end - start)
        for start, end, rate in zip(starts, ends, rates)
    )
    top_2_percent = nearest_100(ACT_1_TABLE_B_2_PERCENT_TOP * factor)
    table_b = 0.02 * np.minimum(ti, top_2_percent) + 0.037 * np.maximum(
        ti - top_2_percent, 0
    )
    bounds = np.array([nearest_100(bound * factor) for bound, _ in ACT_1_LADDER])
    amounts = np.array([amount for _, amount in ACT_1_LADDER])
    # Row k covers income above bounds[k] up to and including bounds[k + 1].
    row = np.searchsorted(bounds, ti, side="left") - 1
    adjustment = np.where(row >= 0, amounts[np.maximum(row, 0)], 0)
    threshold = nearest_100(ACT_1_THRESHOLD * factor)
    return np.where(ti <= threshold, table_a, table_b - adjustment)


def model_tax(year, ti, parameters=P):
    return ar_main_income_tax(ti, parameters(f"{year}-01-01"))


def source_tax(year, ti):
    if year in PUBLISHED_YEARS:
        return card_tax(year, ti)
    if year == 2026:
        return act_1_of_2026_tax(ti)
    return indexed_act_1_of_2026_tax(year, ti)


@pytest.mark.parametrize("year", SOURCE_YEARS)
def test_ar_schedule_matches_source_at_every_integer_income(year):
    diff = model_tax(year, TAXABLE_INCOME) - source_tax(year, TAXABLE_INCOME)
    bad = np.flatnonzero(np.abs(diff) > 0.005)
    assert bad.size == 0, (
        f"{year}: {bad.size} incomes differ from the source, first at "
        f"{TAXABLE_INCOME[bad[0]]:,.0f} (model - source = {diff[bad[0]]:+.2f})"
    )


def test_ar_indexed_reference_is_act_1_of_2026_in_2026():
    diff = indexed_act_1_of_2026_tax(2026, TAXABLE_INCOME) - act_1_of_2026_tax(
        TAXABLE_INCOME
    )
    assert np.abs(diff).max() < 1e-6


def test_ar_published_reduction_applies_through_2025_only():
    assert [
        bool(P.use_published_reduction(f"{y}-01-01")) for y in range(2021, 2028)
    ] == [True] * 5 + [False] * 2


# {income: change in tax from income to income + 1} where the statute itself
# makes tax fall: A.C.A. 26-51-201(a)(4)(A) vs (a)(4)(B)-(C), Act 1 of 2026.
STATUTORY_DROPS = {2026: {94_700: -2.66}}


def invariant_grid(year):
    # Every integer up to well past the (C) ladder, which indexing moves up.
    top = 150_000
    if year not in PUBLISHED_YEARS:
        top = max(top, int(1.6 * P.high_income.threshold(f"{year}-01-01")))
    extra = [x for x in (250_000.0, 1_000_000.0, 1e7) if x > top]
    return np.concatenate([np.arange(0, top + 1, dtype=float), extra])


@pytest.mark.parametrize("year", INVARIANT_YEARS)
def test_ar_schedule_tax_is_nonnegative_and_nondecreasing(year):
    ti = invariant_grid(year)
    tax = model_tax(year, ti)
    assert tax.min() >= -1e-9
    change = np.diff(tax)
    falls = {
        int(ti[i]): round(float(change[i]), 2) for i in np.flatnonzero(change < -1e-9)
    }
    if year in STATUTORY_DROPS or year in PUBLISHED_YEARS:
        assert falls == STATUTORY_DROPS.get(year, {})
    else:
        # Only where the statute's (A) and (B)-(C) tables meet.
        seam = P.high_income.threshold(f"{year}-01-01")
        assert set(falls) <= {seam}, falls


@pytest.mark.parametrize("year", PUBLISHED_YEARS)
def test_ar_reduction_rows_have_strictly_increasing_thresholds(year):
    # Read each YAML row's own threshold: the loaded scale can't show a
    # mis-keyed row, because add_bracket sorts thresholds and sums the amounts
    # of duplicates.
    instant = f"{year}-01-01"
    thresholds = [bracket.threshold(instant) for bracket in P.reduction.brackets]
    finite = [t for t in thresholds if t < np.inf]
    assert thresholds[: len(finite)] == finite, thresholds
    assert all(a < b for a, b in zip(finite, finite[1:])), finite


@pytest.mark.parametrize("year", DERIVED_YEARS)
def test_ar_bracket_adjustment_ladder_follows_the_indexed_threshold(year):
    # Read each YAML row, as above: the loaded scale would hide a duplicate.
    instant = f"{year}-01-01"
    rows = P.high_income.bracket_adjustment.brackets
    bounds = [row.threshold(instant) for row in rows]
    amounts = [row.amount(instant) for row in rows]
    assert bounds[0] == P.high_income.threshold(instant)
    widths = np.diff(bounds)
    assert (widths >= 100).all() and (widths % 100 == 0).all(), bounds
    assert amounts == [amount for _, amount in ACT_1_LADDER]


@pytest.mark.parametrize("year", DERIVED_YEARS)
def test_ar_high_income_top_rate_matches_rate_table(year):
    p = P(f"{year}-01-01")
    finite_rates = [
        rate
        for threshold, rate in zip(p.rate.thresholds, p.rate.amounts)
        if threshold < np.inf
    ]
    assert p.high_income.rate.rates[-1] == finite_rates[-1]


def random_statutory_tables(rng):
    """Random (A), (B) and (C) tables shaped like 26-51-201(a)(4)."""
    starts = np.sort(rng.choice(np.arange(1, 500), rng.integers(1, 7), replace=False))
    table_a = SingleAmountTaxScale()
    table_a.add_bracket(0, 0)
    for start, rate in zip(100 * starts, np.sort(rng.uniform(0, 0.1, starts.size))):
        table_a.add_bracket(int(start), float(rate))
    threshold = 100 * int(starts[-1] + rng.integers(1, 1_000))
    table_b = MarginalRateTaxScale()
    low_rate, high_rate = np.sort(rng.uniform(0, 0.1, 2))
    table_b.add_bracket(0, float(low_rate))
    table_b.add_bracket(100 * int(rng.integers(1, threshold // 100)), float(high_rate))
    rows = int(rng.integers(1, 40))
    bounds = threshold + np.concatenate([[0], np.cumsum(rng.choice([100, 200], rows))])
    amounts = np.append(np.sort(rng.uniform(0, 500, rows))[::-1], 0)
    ladder = SingleAmountTaxScale()
    for bound, amount in zip(bounds, amounts):
        ladder.add_bracket(int(bound), float(amount))
    return SimpleNamespace(
        use_published_reduction=False,
        rate=table_a,
        high_income=SimpleNamespace(
            threshold=threshold, rate=table_b, bracket_adjustment=ladder
        ),
    )


@pytest.mark.parametrize("seed", range(200))
def test_ar_derived_schedule_properties_on_random_tables(seed):
    p = random_statutory_tables(np.random.default_rng(seed))
    threshold = p.high_income.threshold
    ti = np.arange(0, threshold + 10_000, dtype=float)
    tax = ar_main_income_tax(ti, p)
    table_a = ti <= threshold
    # The derived (A) tax is the card form: rate x income minus the reduction
    # that the indexed row starts imply.
    starts = np.array(p.rate.thresholds)
    steps = np.diff(p.rate.amounts, prepend=0)
    reduction = (steps * starts * (ti[:, None] >= starts)).sum(axis=1)
    card_form = p.rate.calc(ti) * ti - reduction
    assert np.abs(tax[table_a] - card_form[table_a]).max() < 1e-9
    # Continuous at every (A) row start: the step there is the prior rate.
    for start, prior_rate in zip(starts[1:], p.rate.amounts[:-1]):
        if 0 < start <= threshold:
            step = tax[int(start)] - tax[int(start) - 1]
            assert abs(step - prior_rate) < 1e-9
    # (A) is never negative. Above the threshold that depends on the (C)
    # amounts being small next to the (B) tax, which the statute's are (checked
    # per year above) but random ones need not be. Neither regime ever falls.
    assert tax[table_a].min() >= -1e-9
    change = np.diff(tax)
    within_regime = table_a[1:] == table_a[:-1]
    assert (change[within_regime] >= -1e-9).all()


def test_ar_rate_table_reform_keeps_projected_schedule_continuous():
    # A stored 2027 reduction would ignore this reform and make tax fall at
    # the moved bounds; the derived one follows it.
    reformed = P.clone()
    reformed.rate.brackets[1].threshold.update(period="year:2027-01-01:1", value=7_000)
    reformed.rate.brackets[4].amount.update(period="year:2027-01-01:1", value=0.035)
    reformed.high_income.rate.brackets[1].rate.update(
        period="year:2027-01-01:1", value=0.035
    )
    ti = np.arange(0, 150_001, dtype=float)
    tax = model_tax(2027, ti, reformed)
    assert tax[7_000] == pytest.approx(0)
    assert tax[7_100] == pytest.approx(2)
    change = np.diff(tax)
    falls = ti[:-1][change < -1e-9]
    seam = reformed.high_income.threshold("2027-01-01")
    assert set(falls) <= {seam}, falls

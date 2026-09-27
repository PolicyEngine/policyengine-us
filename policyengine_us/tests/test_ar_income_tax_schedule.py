"""Arkansas regular income tax schedule: differential and invariant tests.

`ar_income_tax_before_non_refundable_credits_indiv` computes
`rate.calc(ti) * ti - reduction.calc(ti)` from two single_amount scales whose
rows are shared across years, so a mis-keyed row in one year's column (a
skipped DFA row, an ignored asterisked two-row range, a duplicated
threshold) silently shifts every later bracket. These tests compare every
integer taxable income against an independent transcription of each year's
source:

- 2021-2025: DFA Indexed Tax Brackets cards, e.g.
  https://www.dfa.arkansas.gov/wp-content/uploads/2025_TaxBrackets.pdf#page=1
  Rows from the top of the flat rate bracket upward form a $100 ladder whose
  minus adjustment falls $10 per row. Asterisked rows span $200, so the next
  row's start is skipped.
- 2026: Act 1 of 2026 (1st Extraordinary Session), A.C.A. 26-51-201(a)(4).

Invariants (2021-2026): reduction.yaml rows carry strictly increasing
finite thresholds, with every .inf row after them. At every integer taxable
income, tax is non-negative and never falls as income rises, except the one
drop Act 1 of 2026 writes into the statute:
(a)(4)(A) taxes $94,700 at $3,136.70, while (a)(4)(B) less the $290
(a)(4)(C) adjustment taxes $94,701 at $3,134.04.
"""

import numpy as np
import pytest

from policyengine_us.system import system

P = system.parameters.gov.states.ar.tax.income.rates.main
YEARS = range(2021, 2027)
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


def model_tax(year, ti):
    instant = f"{year}-01-01"
    return P.rate(instant).calc(ti) * ti - P.reduction(instant).calc(ti)


def source_tax(year, ti):
    return act_1_of_2026_tax(ti) if year == 2026 else card_tax(year, ti)


@pytest.mark.parametrize("year", YEARS)
def test_ar_schedule_matches_source_at_every_integer_income(year):
    diff = model_tax(year, TAXABLE_INCOME) - source_tax(year, TAXABLE_INCOME)
    bad = np.flatnonzero(np.abs(diff) > 0.005)
    assert bad.size == 0, (
        f"{year}: {bad.size} incomes differ from the source, first at "
        f"{TAXABLE_INCOME[bad[0]]:,.0f} (model - source = {diff[bad[0]]:+.2f})"
    )


# {income: change in tax from income to income + 1} where the statute itself
# makes tax fall: A.C.A. 26-51-201(a)(4)(A) vs (a)(4)(B)-(C), Act 1 of 2026.
STATUTORY_DROPS = {2026: {94_700: -2.66}}


@pytest.mark.parametrize("year", YEARS)
def test_ar_schedule_tax_is_nonnegative_and_nondecreasing(year):
    tax = model_tax(year, TAXABLE_INCOME)
    assert tax.min() >= -1e-9
    change = np.diff(tax)
    falls = {
        int(TAXABLE_INCOME[i]): round(float(change[i]), 2)
        for i in np.flatnonzero(change < -1e-9)
    }
    assert falls == STATUTORY_DROPS.get(year, {})


@pytest.mark.parametrize("year", YEARS)
def test_ar_reduction_rows_have_strictly_increasing_thresholds(year):
    # Read each YAML row's own threshold: the loaded scale can't show a
    # mis-keyed row, because add_bracket sorts thresholds and sums the amounts
    # of duplicates.
    instant = f"{year}-01-01"
    thresholds = [bracket.threshold(instant) for bracket in P.reduction.brackets]
    finite = [t for t in thresholds if t < np.inf]
    assert thresholds[: len(finite)] == finite, thresholds
    assert all(a < b for a, b in zip(finite, finite[1:])), finite

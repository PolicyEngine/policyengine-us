"""Property and differential tests for the section 911(f) tax computation.

26 U.S.C. 911(f)(1): if any amount is excluded from gross income under
section 911(a), "the tax imposed by section 1 for such taxable year shall
be equal to the excess (if any) of (i) the tax which would be imposed by
section 1 for such taxable year if the taxpayer's taxable income were
increased by the amount excluded under subsection (a) for such taxable
year, over (ii) the tax which would be imposed by section 1 for such
taxable year if the taxpayer's taxable income were equal to the amount
excluded". Subparagraph (B) applies the same rule to the alternative
minimum tax, and paragraph (2) keeps capital gains from exceeding taxable
income (the "capital gain excess").

Two kinds of test:

- Differential. The 2025 IRS worksheets are transcribed below line by line
  (Foreign Earned Income Tax Worksheet, Qualified Dividends and Capital
  Gain Tax Worksheet, and Form 6251 with its own Foreign Earned Income Tax
  Worksheet and Part III) and compared with the model, household by
  household. The model reaches the same tax by a different route: the
  section 1(h) formulas in `capital_gains_excluded_from_taxable_income`,
  `income_tax_main_rates` and `capital_gains_tax`.
- Properties that hold for every household: with nothing excluded, every
  amount that section 911(f) replaces is unchanged, bit for bit; the stacked
  tax is never below the unstacked tax; zero taxable income gives zero
  regular tax; and the tax never falls as the excluded amount rises.

Households live in Texas; some itemize.

The model takes the section 1(h)(1) cap at the tax on all taxable income
at ordinary rates (worksheet line 25, "the smaller of line 23 or line 24"),
so it is compared with line 25. The cap binds only where the 15% rate
applies inside the 12% bracket, a band of $100 to $250 of income in 2025,
so line 25 is checked to be within $7.50 of line 23.

One limit of the model sets the scope of these tests, and it does not come
from section 911: `capital_gains_tax` taxes 28-percent rate gain in full
even when it exceeds taxable income, so the households here have no
28-percent rate or unrecaptured section 1250 gain. YAML unit tests cover how
the capital gain excess reduces those two amounts.
"""

import numpy as np
import pytest

from policyengine_us import Simulation

# Hypothesis is a dev extra; skip rather than fail collection without it.
hypothesis = pytest.importorskip("hypothesis")
st = pytest.importorskip("hypothesis.strategies")

# ---------------------------------------------------------------------------
# The 2025 IRS worksheets, transcribed. Dollar amounts are from the 2025
# Instructions for Form 1040 (Tax Table, Tax Computation Worksheet and the
# worksheets on pages 37 and 38) and the 2025 Form 6251 and its instructions.
# ---------------------------------------------------------------------------

INF = float("inf")
# Top of each rate bracket.
TAX_RATE_SCHEDULE_2025 = {
    "SINGLE": [
        (11_925, 0.10),
        (48_475, 0.12),
        (103_350, 0.22),
        (197_300, 0.24),
        (250_525, 0.32),
        (626_350, 0.35),
        (INF, 0.37),
    ],
    "JOINT": [
        (23_850, 0.10),
        (96_950, 0.12),
        (206_700, 0.22),
        (394_600, 0.24),
        (501_050, 0.32),
        (751_600, 0.35),
        (INF, 0.37),
    ],
    "SEPARATE": [
        (11_925, 0.10),
        (48_475, 0.12),
        (103_350, 0.22),
        (197_300, 0.24),
        (250_525, 0.32),
        (375_800, 0.35),
        (INF, 0.37),
    ],
    "HEAD_OF_HOUSEHOLD": [
        (17_000, 0.10),
        (64_850, 0.12),
        (103_350, 0.22),
        (197_300, 0.24),
        (250_500, 0.32),
        (626_350, 0.35),
        (INF, 0.37),
    ],
}
# Qualified Dividends and Capital Gain Tax Worksheet, lines 6 and 13.
ZERO_RATE_AMOUNT_2025 = {
    "SINGLE": 48_350,
    "JOINT": 96_700,
    "SEPARATE": 48_350,
    "HEAD_OF_HOUSEHOLD": 64_750,
}
FIFTEEN_PERCENT_RATE_AMOUNT_2025 = {
    "SINGLE": 533_400,
    "JOINT": 600_050,
    "SEPARATE": 300_000,
    "HEAD_OF_HOUSEHOLD": 566_700,
}


def tax_rate_schedule(amount, status):
    """Tax on an amount at the ordinary rates (Tax Computation Worksheet)."""
    tax, bottom = 0.0, 0.0
    for top, rate in TAX_RATE_SCHEDULE_2025[status]:
        if amount > bottom:
            tax += rate * (min(amount, top) - bottom)
        bottom = top
    return tax


def qualified_dividends_and_capital_gain_tax_worksheet(line_1, line_2, line_3, status):
    """2025 Form 1040 instructions, page 38. Returns lines 5, 23 and 25."""
    line_4 = line_2 + line_3
    line_5 = max(0, line_1 - line_4)
    line_6 = ZERO_RATE_AMOUNT_2025[status]
    line_7 = min(line_1, line_6)
    line_8 = min(line_5, line_7)
    line_9 = line_7 - line_8
    line_10 = min(line_1, line_4)
    line_11 = line_9
    line_12 = line_10 - line_11
    line_13 = FIFTEEN_PERCENT_RATE_AMOUNT_2025[status]
    line_14 = min(line_1, line_13)
    line_15 = line_5 + line_9
    line_16 = max(0, line_14 - line_15)
    line_17 = min(line_12, line_16)
    line_18 = 0.15 * line_17
    line_19 = line_9 + line_17
    line_20 = line_10 - line_19
    line_21 = 0.20 * line_20
    line_22 = tax_rate_schedule(line_5, status)
    line_23 = line_18 + line_21 + line_22
    line_24 = tax_rate_schedule(line_1, status)
    line_25 = min(line_23, line_24)
    return line_5, line_23, line_25


def reduce_by_capital_gain_excess(excess, qualified_dividends, net_gain):
    """Footnote to the Foreign Earned Income Tax Worksheet, items 1 and 2.

    Returns the amounts for lines 2 and 3 of the Qualified Dividends and
    Capital Gain Tax Worksheet.
    """
    # 1. Reduce (but not below zero) line 3 by the capital gain excess.
    line_3 = max(0, net_gain - excess)
    # 2. Reduce (but not below zero) line 2 by any excess not used in (1).
    line_2 = max(0, qualified_dividends - max(0, excess - net_gain))
    return line_2, line_3


def foreign_earned_income_tax_worksheet(
    taxable_income, excluded, qualified_dividends, net_gain, status
):
    """2025 Form 1040 instructions, page 37.

    Returns line 6 figured with line 23 of the capital gains worksheet (the
    tax before the section 1(h)(1) cap), line 6 figured with its line 25
    (what the form says and the model computes), and line 5 of the capital
    gains worksheet, which Form 6251 needs.
    A filer with no exclusion gets the ordinary line 16 tax.
    """
    line_1 = taxable_income
    line_2c = max(0, excluded)
    line_3 = line_1 + line_2c
    # "subtract Form 1040 or 1040-SR, line 15, from line 4 of your Qualified
    # Dividends and Capital Gain Tax Worksheet ... If the result is more than
    # zero, that amount is your capital gain excess."
    excess = max(0, qualified_dividends + net_gain - line_1) if line_2c > 0 else 0
    dividends, gain = reduce_by_capital_gain_excess(
        excess, qualified_dividends, net_gain
    )
    ordinary_income, line_4, line_4_capped = (
        qualified_dividends_and_capital_gain_tax_worksheet(
            line_3, dividends, gain, status
        )
    )
    # "If Form 1040 or 1040-SR, line 15, is zero, don't complete this
    # worksheet."
    if line_1 <= 0:
        return 0.0, 0.0, ordinary_income
    line_5 = tax_rate_schedule(line_2c, status)
    return max(0, line_4 - line_5), max(0, line_4_capped - line_5), ordinary_income


def amt_rates(amount, status):
    """Form 6251 line 7, "All others", and Part III lines 18 and 39."""
    separate = status == "SEPARATE"
    if amount <= (119_550 if separate else 239_100):
        return 0.26 * amount
    return 0.28 * amount - (2_391 if separate else 4_782)


def form_6251_part_iii(line_12, line_13, line_20, status):
    """2025 Form 6251, lines 12 to 40, with no Schedule D Tax Worksheet.

    Without that worksheet line 14 is zero, line 15 equals line 13 and line
    27 equals line 20.
    """
    line_15 = line_13
    line_16 = min(line_12, line_15)
    line_17 = line_12 - line_16
    line_18 = amt_rates(line_17, status)
    line_19 = ZERO_RATE_AMOUNT_2025[status]
    line_21 = max(0, line_19 - line_20)
    line_22 = min(line_12, line_13)
    line_23 = min(line_21, line_22)
    line_24 = line_22 - line_23
    line_25 = FIFTEEN_PERCENT_RATE_AMOUNT_2025[status]
    line_26 = line_21
    line_27 = line_20
    line_28 = line_26 + line_27
    line_29 = max(0, line_25 - line_28)
    line_30 = min(line_24, line_29)
    line_31 = 0.15 * line_30
    line_32 = line_23 + line_30
    line_33 = line_22 - line_32
    line_34 = 0.20 * line_33
    line_38 = line_18 + line_31 + line_34
    line_39 = amt_rates(line_12, status)
    return min(line_38, line_39)


def form_6251_line_7(
    taxable_excess, excluded, qualified_dividends, net_gain, line_20, status
):
    """Form 6251 line 7 through its Foreign Earned Income Tax Worksheet.

    2025 Form 6251 instructions, page 10. `line_20` is line 5 of the capital
    gains worksheet "as figured for the regular tax". A filer with no
    exclusion gets the ordinary line 7 tax.
    """
    # "If Form 6251, line 6, is zero, don't complete this worksheet."
    if taxable_excess <= 0:
        return 0.0
    line_1 = taxable_excess
    line_2c = max(0, excluded)
    line_3 = line_1 + line_2c
    if qualified_dividends + net_gain > 0:
        # "To see if you have an AMT capital gain excess, subtract Form 6251,
        # line 6, from line 4 of your AMT Qualified Dividends and Capital
        # Gain Tax Worksheet".
        excess = max(0, qualified_dividends + net_gain - line_1) if line_2c > 0 else 0
        dividends, gain = reduce_by_capital_gain_excess(
            excess, qualified_dividends, net_gain
        )
        line_4 = form_6251_part_iii(line_3, dividends + gain, line_20, status)
    else:
        line_4 = amt_rates(line_3, status)
    line_5 = amt_rates(line_2c, status)
    return max(0, line_4 - line_5)


# ---------------------------------------------------------------------------
# The model.
# ---------------------------------------------------------------------------

OUTPUTS = [
    "filing_status",
    "tax_unit_itemizes",
    "taxable_income",
    "foreign_earned_income_exclusion",
    "taxable_income_plus_section_911_exclusion",
    "section_911_capital_gain_excess",
    "income_tax_main_rates",
    "capital_gains_tax",
    "regular_tax_before_credits",
    "amt_income_less_exemptions",
    "amt_income_less_exemptions_plus_section_911_exclusion",
    "amt_section_911_capital_gain_excess",
    "alternative_minimum_tax",
    "income_tax_before_credits",
]


def build_situation(households, year):
    people, tax_units, marital_units = {}, {}, {}
    groups = {"households": {}, "spm_units": {}, "families": {}}
    for i, h in enumerate(households):
        head = f"head_{i}"
        people[head] = {
            "age": {year: 45},
            "employment_income": {year: h["wages"]},
            "qualified_dividend_income": {year: h["qualified_dividends"]},
            "long_term_capital_gains": {year: h["long_term_gains"]},
            "short_term_capital_gains": {year: h["short_term_gains"]},
            "long_term_capital_gains_on_collectibles": {
                year: h.get("collectibles_gains", 0)
            },
            "real_estate_taxes": {year: h.get("real_estate_taxes", 0)},
            "deductible_mortgage_interest": {year: h.get("mortgage_interest", 0)},
            "charitable_cash_donations": {year: h.get("charitable_gifts", 0)},
        }
        members = [head]
        marital_units[f"marital_unit_{i}"] = {"members": [head]}
        if h["status"] == "JOINT":
            spouse = f"spouse_{i}"
            people[spouse] = {"age": {year: 45}}
            members.append(spouse)
            marital_units[f"marital_unit_{i}"]["members"].append(spouse)
        if h["status"] == "HEAD_OF_HOUSEHOLD":
            # Old enough to be a dependent without a child tax credit.
            child = f"child_{i}"
            people[child] = {"age": {year: 17}}
            members.append(child)
            marital_units[f"marital_unit_{i}_child"] = {"members": [child]}
        tax_units[f"tax_unit_{i}"] = {
            "members": members,
            # Set for every tax unit: an input given to only some of them
            # leaves the rest at the default (single), not at the status
            # the model would compute.
            "filing_status": {year: h["status"]},
            "foreign_earned_income_exclusion": {year: h["exclusion"]},
            "unrecaptured_section_1250_gain": {
                year: h.get("unrecaptured_section_1250_gain", 0)
            },
        }
        groups["households"][f"household_{i}"] = {
            "members": members,
            "state_code": {year: "TX"},
        }
        groups["spm_units"][f"spm_unit_{i}"] = {"members": members}
        groups["families"][f"family_{i}"] = {"members": members}
    return {
        "people": people,
        "tax_units": tax_units,
        "marital_units": marital_units,
        **groups,
    }


def calculate(households, year):
    simulation = Simulation(situation=build_situation(households, year))
    results = {}
    for v in OUTPUTS:
        values = simulation.calculate(v, year)
        results[v] = (
            values.decode_to_str() if v == "filing_status" else np.asarray(values)
        )
    results["regular_tax"] = (
        results["income_tax_main_rates"] + (results["capital_gains_tax"])
    )
    return results


def with_exclusion(households, exclusion):
    """The same households with the exclusion replaced or transformed."""
    change = exclusion if callable(exclusion) else lambda _: exclusion
    return [{**h, "exclusion": change(h["exclusion"])} for h in households]


def net_gain(household):
    """Schedule D: the smaller of lines 15 and 16, or zero if either is a loss."""
    long_term = household["long_term_gains"]
    return max(0, min(long_term, long_term + household["short_term_gains"]))


MODEL_TAXES = ["regular_tax", "income_tax_before_credits"]


def tolerance(*amounts):
    """Five cents, plus the rounding of single-precision arithmetic.

    The model stores amounts as 32-bit floats, which carry about seven
    significant digits, and the stacked tax is a difference of two taxes on
    larger amounts.
    """
    return 0.05 + 5e-7 * np.max(np.abs(amounts), axis=0)


def assert_matches_worksheets(households, law):
    """The 2025 model against the transcribed 2025 worksheets."""
    cap_gaps = []
    for i, h in enumerate(households):
        status = law["filing_status"][i]
        assert status == h["status"], (i, status)
        taxable_income = float(law["taxable_income"][i])
        gain = net_gain(h)
        dividends = h["qualified_dividends"]
        line_6, line_6_capped, ordinary_income = foreign_earned_income_tax_worksheet(
            taxable_income, h["exclusion"], dividends, gain, status
        )
        regular_tax = float(law["regular_tax"][i])
        stacked_income = taxable_income + h["exclusion"]
        assert float(law["regular_tax_before_credits"][i]) == pytest.approx(
            regular_tax, abs=tolerance(stacked_income)
        ), (i, h)
        assert regular_tax == pytest.approx(
            line_6_capped, abs=tolerance(stacked_income)
        ), (i, h)
        # The form's line 25 cap takes at most $7.50 off line 23.
        cap_gaps.append(line_6 - line_6_capped)
        line_7 = form_6251_line_7(
            float(law["amt_income_less_exemptions"][i]),
            h["exclusion"],
            dividends,
            gain,
            ordinary_income,
            status,
        )
        assert -tolerance(stacked_income) <= cap_gaps[-1], (i, h)
        assert cap_gaps[-1] <= 7.5 + tolerance(stacked_income), (i, h)
        # Form 6251 lines 9 to 11 with no foreign tax credit.
        amt = max(0, line_7 - line_6_capped)
        taxable_excess = float(
            law["amt_income_less_exemptions_plus_section_911_exclusion"][i]
        )
        assert float(law["alternative_minimum_tax"][i]) == pytest.approx(
            amt, abs=tolerance(stacked_income, taxable_excess)
        ), (i, h)


def assert_invariants(households, year):
    law = calculate(households, year)
    unstacked = calculate(with_exclusion(households, 0), year)
    more_excluded = calculate(with_exclusion(households, lambda e: 1.5 * e + 500), year)
    excluded = law["foreign_earned_income_exclusion"]
    assert np.array_equal(excluded, [h["exclusion"] for h in households])
    excludes = excluded > 0
    taxable_income = law["taxable_income"]
    # The exclusion changes the rates, not taxable income.
    for other in [unstacked, more_excluded]:
        assert np.array_equal(other["taxable_income"], taxable_income)

    # 1. A household without an exclusion gets the same results whatever the
    # other households in the batch exclude. (test_nothing_excluded_changes_
    # nothing checks the amounts section 911(f) replaces.)
    for v in OUTPUTS[1:]:
        assert np.array_equal(law[v][~excludes], unstacked[v][~excludes]), v
    assert np.array_equal(
        unstacked["taxable_income_plus_section_911_exclusion"], taxable_income
    )
    assert np.array_equal(
        unstacked["amt_income_less_exemptions_plus_section_911_exclusion"],
        unstacked["amt_income_less_exemptions"],
    )
    for v in ["section_911_capital_gain_excess", "amt_section_911_capital_gain_excess"]:
        assert not unstacked[v].any(), v

    # 2. Worksheet line 3 is line 1 plus line 2c.
    slack = tolerance(
        taxable_income + more_excluded["foreign_earned_income_exclusion"],
        more_excluded["amt_income_less_exemptions_plus_section_911_exclusion"],
    )
    assert (
        np.abs(
            law["taxable_income_plus_section_911_exclusion"]
            - (taxable_income + excluded)
        )
        <= slack
    ).all()

    for v in MODEL_TAXES:
        # 3. Stacking never lowers the tax ...
        assert (law[v] >= unstacked[v] - slack).all(), v
        # 4. ... and the tax never falls as the excluded amount rises.
        assert (more_excluded[v] >= law[v] - slack).all(), v
        assert (law[v] >= 0).all(), v

    # 5. Section 911(f)(1)(A) applies "if such taxpayer has taxable income":
    # with none, there is no regular tax, whatever is excluded.
    no_taxable_income = taxable_income == 0
    for results in [law, unstacked, more_excluded]:
        assert (results["regular_tax"][no_taxable_income] == 0).all()

    # 6. Each dollar of taxable income bears at most the top rate, so the
    # regular tax is at most that rate times taxable income (37% in every
    # year tested).
    assert (law["regular_tax"] <= 0.37 * taxable_income + slack).all()

    # 7. The capital gain excess is the part of the gains above taxable
    # income, and only a filer with an exclusion has one.
    assert (law["section_911_capital_gain_excess"] >= 0).all()
    assert not law["section_911_capital_gain_excess"][~excludes].any()
    assert not law["amt_section_911_capital_gain_excess"][~excludes].any()
    return law, unstacked


STATUSES = ["SINGLE", "JOINT", "HEAD_OF_HOUSEHOLD", "SEPARATE"]

GRID = [
    {
        "status": status,
        "wages": wages,
        "qualified_dividends": dividends,
        "long_term_gains": long_term,
        "short_term_gains": short_term,
        "exclusion": exclusion,
    }
    for status in STATUSES
    for wages in (0, 20_000, 59_975, 140_000, 700_000)
    for dividends, long_term, short_term in (
        (0, 0, 0),
        (3_000, 0, 0),
        (0, 50_000, 0),
        (10_000, 40_000, -15_000),
        (0, 30_000, 20_000),
        (25_000, 900_000, 0),
        (0, -8_000, 5_000),
    )
    for exclusion in (0, 1, 40_025, 130_000, 260_000)
]


def test_grid_matches_the_2025_worksheets():
    law = calculate(GRID, 2025)
    assert_matches_worksheets(GRID, law)
    # The grid reaches every part of the computation.
    excludes = law["foreign_earned_income_exclusion"] > 0
    assert (law["section_911_capital_gain_excess"] > 0).any()
    assert (law["amt_section_911_capital_gain_excess"] > 0).any()
    assert (excludes & (law["capital_gains_tax"] > 0)).any()
    assert (excludes & (law["alternative_minimum_tax"] > 0)).any()
    assert (excludes & (law["taxable_income"] == 0)).any()


@pytest.mark.parametrize("year", [2018, 2022, 2025, 2026])
def test_grid_invariants(year):
    law, unstacked = assert_invariants(GRID, year)
    # The grid reaches filers whose tax the stacking raises.
    assert (law["regular_tax"] > unstacked["regular_tax"] + 1).any()


def test_review_example_from_the_tax_table():
    # 2025, head of household, $60,000 of included wages and $40,000
    # excluded. Worksheet: line 1 is $36,375 ($60,000 less the $23,625
    # standard deduction), line 2c $40,000, line 3 $76,375. The Tax Table
    # gives $9,978 on line 3 and $4,463 on line 2c, so line 6 is $5,515.
    # The Tax Table taxes the middle of each $50 row; the model taxes the
    # exact amounts ($9,977.50 less $4,460.00).
    household = {
        "status": "HEAD_OF_HOUSEHOLD",
        "wages": 60_000,
        "qualified_dividends": 0,
        "long_term_gains": 0,
        "short_term_gains": 0,
        "exclusion": 40_000,
    }
    law = calculate([household], 2025)
    assert law["taxable_income"][0] == 36_375
    assert law["regular_tax"][0] == pytest.approx(5_517.50, abs=0.01)
    assert law["regular_tax"][0] == pytest.approx(9_978 - 4_463, abs=3)
    unstacked = calculate(with_exclusion([household], 0), 2025)
    # $4,025 is the Tax Table amount for $36,375.
    assert unstacked["regular_tax"][0] == pytest.approx(4_025, abs=0.01)


# The Tax Table's column order.
STATUSES_TABLE_ORDER = ["SINGLE", "JOINT", "SEPARATE", "HEAD_OF_HOUSEHOLD"]

# Rows of the 2025 Tax Table (2025 Instructions for Form 1040): at least,
# but less than, then the tax for single, married filing jointly, married
# filing separately and head of household filers. The table taxes the middle
# of each row and rounds to the dollar.
TAX_TABLE_2025_ROWS = [
    (11_900, 11_950, 1_193, 1_193, 1_193, 1_193),
    (17_000, 17_050, 1_805, 1_703, 1_805, 1_703),
    (23_850, 23_900, 2_627, 2_388, 2_627, 2_525),
    (30_000, 30_050, 3_365, 3_126, 3_365, 3_263),
    (36_350, 36_400, 4_127, 3_888, 4_127, 4_025),
    (40_000, 40_050, 4_565, 4_326, 4_565, 4_463),
    (48_450, 48_500, 5_579, 5_340, 5_579, 5_477),
    (60_050, 60_100, 8_131, 6_732, 8_131, 6_869),
    (64_800, 64_850, 9_176, 7_302, 9_176, 7_439),
    (76_350, 76_400, 11_717, 8_688, 11_717, 9_978),
    (96_900, 96_950, 16_238, 11_154, 16_238, 14_499),
    (99_950, 100_000, 16_909, 11_823, 16_909, 15_170),
]
# 2025 Tax Computation Worksheet: taxable income, multiplication amount and
# subtraction amount, one row from each section.
TAX_COMPUTATION_WORKSHEET_2025_ROWS = {
    "SINGLE": [(150_000, 0.24, 7_153), (700_000, 0.37, 42_979.75)],
    "JOINT": [(300_000, 0.24, 14_306), (800_000, 0.37, 75_937.50)],
    "SEPARATE": [(220_000, 0.32, 22_937), (400_000, 0.37, 37_968.75)],
    "HEAD_OF_HOUSEHOLD": [(120_000, 0.24, 8_892), (300_000, 0.35, 32_191)],
}


def test_transcribed_schedule_matches_the_2025_tax_table():
    for low, high, *taxes in TAX_TABLE_2025_ROWS:
        for status, tax in zip(STATUSES_TABLE_ORDER, taxes):
            # Round half up to the dollar, as the table does.
            assert int(tax_rate_schedule((low + high) / 2, status) + 0.5) == tax, (
                low,
                status,
            )
    for status, rows in TAX_COMPUTATION_WORKSHEET_2025_ROWS.items():
        for amount, rate, subtraction in rows:
            assert tax_rate_schedule(amount, status) == pytest.approx(
                amount * rate - subtraction, abs=1e-6
            ), (amount, status)


# Households with every kind of gain the computation touches, itemizers
# among them.
REPLACED_AMOUNTS_GRID = [
    {
        "status": status,
        "wages": wages,
        "qualified_dividends": dividends,
        "long_term_gains": long_term,
        "short_term_gains": short_term,
        "collectibles_gains": collectibles,
        "unrecaptured_section_1250_gain": section_1250,
        "real_estate_taxes": real_estate_taxes,
        "mortgage_interest": 0,
        "charitable_gifts": charitable_gifts,
        "exclusion": exclusion,
    }
    for status in STATUSES
    for wages in (0, 60_000, 400_000)
    for dividends, long_term, short_term, collectibles, section_1250 in (
        (0, 0, 0, 0, 0),
        (5_000, 80_000, -10_000, 20_000, 15_000),
        (0, 30_000, 0, 30_000, 0),
        (20_000, 600_000, 40_000, 0, 100_000),
    )
    for real_estate_taxes, charitable_gifts in ((0, 0), (12_000, 40_000))
    for exclusion in (0, 50_000)
] + [
    # Amounts with cents, which single precision cannot store exactly, so a
    # rounding step that whole-dollar amounts would hide shows up here.
    {
        "status": status,
        "wages": 61_234.56,
        "qualified_dividends": 12_345.67,
        "long_term_gains": 100_000.01,
        "short_term_gains": -1_234.89,
        "collectibles_gains": 0,
        "unrecaptured_section_1250_gain": 15_000.37,
        "real_estate_taxes": 0,
        "mortgage_interest": 0,
        "charitable_gifts": 0,
        "exclusion": exclusion,
    }
    for status in STATUSES
    for exclusion in (0, 50_000.25)
]


def test_nothing_excluded_changes_nothing():
    """With no capital gain excess, each amount that section 911(f) replaces
    equals the amount it replaces, bit for bit, and with nothing excluded so
    do the stacked bases."""
    from policyengine_core.periods import period as make_period

    from policyengine_us.model_api import add, max_
    from policyengine_us.variables.gov.irs.tax.federal_income.foreign_earned_income_exclusion.schedule_d_tax_worksheet_after_capital_gain_excess import (
        schedule_d_tax_worksheet_after_capital_gain_excess,
    )
    from policyengine_us.variables.gov.irs.tax.federal_income.foreign_earned_income_exclusion.section_911_net_capital_gain_other_than_dividends import (
        section_911_net_capital_gain_other_than_dividends,
    )

    for year in [2018, 2025, 2026]:
        simulation = Simulation(situation=build_situation(REPLACED_AMOUNTS_GRID, year))

        def get(variable):
            return np.asarray(simulation.calculate(variable, year))

        excluded = get("foreign_earned_income_exclusion")
        nothing_excluded = excluded == 0
        no_excess = get("section_911_capital_gain_excess") == 0
        assert not get("section_911_capital_gain_excess")[nothing_excluded].any()
        assert not get("amt_section_911_capital_gain_excess")[nothing_excluded].any()
        # The grid has filers with an excess and filers without.
        assert (~no_excess).any() and (no_excess & ~nothing_excluded).any()
        assert get("tax_unit_itemizes").any() and not get("tax_unit_itemizes").all()

        dividends = np.asarray(
            simulation.calculate("qualified_dividend_income", year, map_to="tax_unit")
        )
        pairs = {
            "section_911_net_capital_gain": get("net_capital_gain"),
            "section_911_qualified_dividend_income": dividends,
            "section_911_28_percent_rate_gain": get(
                "capital_gains_28_percent_rate_gain"
            ),
            "section_911_unrecaptured_section_1250_gain": get(
                "unrecaptured_section_1250_gain"
            ),
            "section_911_adjusted_net_capital_gain": get("adjusted_net_capital_gain"),
        }
        for variable, original in pairs.items():
            assert np.array_equal(get(variable)[no_excess], original[no_excess]), (
                variable,
                year,
            )
        tax_unit = simulation.populations["tax_unit"]
        period = make_period(year)
        # The reduced non-dividend gain against the expression main used in
        # capital_gains_tax, computed the same way (not stored in between).
        main_gain = max_(
            0,
            tax_unit("net_capital_gain", period)
            - add(tax_unit, period, ["qualified_dividend_income"]),
        )
        assert np.array_equal(
            np.asarray(
                section_911_net_capital_gain_other_than_dividends(tax_unit, period)
            )[no_excess],
            np.asarray(main_gain)[no_excess],
        ), year
        worksheet = schedule_d_tax_worksheet_after_capital_gain_excess(
            tax_unit, period, get("taxable_income")
        )
        no_excess = no_excess & (np.asarray(worksheet.capital_gain_excess) == 0)
        for line, original in [
            ("line_9", "dwks09"),
            ("line_10", "dwks10"),
            ("line_13", "dwks13"),
            ("unrecaptured_section_1250_gain", "unrecaptured_section_1250_gain"),
        ]:
            assert np.array_equal(
                np.asarray(getattr(worksheet, line))[no_excess],
                get(original)[no_excess],
            ), (line, year)
        for stacked, original in [
            ("taxable_income_plus_section_911_exclusion", "taxable_income"),
            (
                "amt_income_less_exemptions_plus_section_911_exclusion",
                "amt_income_less_exemptions",
            ),
        ]:
            assert np.array_equal(
                get(stacked)[nothing_excluded], get(original)[nothing_excluded]
            ), (stacked, year)


household_strategy = st.fixed_dictionaries(
    {
        "status": st.sampled_from(STATUSES),
        "wages": st.integers(0, 900_000),
        "qualified_dividends": st.one_of(st.just(0), st.integers(1, 300_000)),
        "long_term_gains": st.one_of(st.just(0), st.integers(-50_000, 1_500_000)),
        "short_term_gains": st.one_of(st.just(0), st.integers(-100_000, 100_000)),
        "exclusion": st.one_of(st.just(0), st.integers(1, 300_000)),
        "real_estate_taxes": st.one_of(st.just(0), st.integers(1, 60_000)),
        "mortgage_interest": st.one_of(st.just(0), st.integers(1, 80_000)),
        "charitable_gifts": st.one_of(st.just(0), st.integers(1, 150_000)),
    }
)

# Fixed examples, so CI on an unrelated pull request draws the same households.
SETTINGS = dict(
    max_examples=10,
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
    st.sampled_from([2018, 2022, 2025, 2026]),
)
def test_random_households_keep_the_invariants(households, year):
    assert_invariants(households, year)


@hypothesis.settings(**SETTINGS)
@hypothesis.given(st.lists(household_strategy, min_size=1, max_size=25))
def test_random_households_match_the_2025_worksheets(households):
    assert_matches_worksheets(households, calculate(households, 2025))

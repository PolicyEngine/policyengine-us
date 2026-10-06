"""Property and differential tests for the regular tax on Form 6251 line 10.

26 U.S.C. 1(h)(1): "If a taxpayer has a net capital gain for any taxable
year, the tax imposed by this section for such taxable year shall not exceed
the sum of" the amounts in subparagraphs (A) to (F). The 2025 Schedule D Tax
Worksheet adds those amounts on line 45, figures the tax on all of line 1 at
the regular rates on line 46, and enters "the smaller of line 45 or line 46"
on line 47, the tax on Form 1040 line 16.

The model figures the regular tax once, by the section 1(h) formulas:
`income_tax_main_rates` taxes subparagraph (A)'s amount at the regular
rates, and `capital_gains_tax` adds subparagraphs (B) to (F), but no more
than the rest of `tax_on_taxable_income_at_main_rates` (line 46).
`regular_tax_before_credits` is the sum, and Form 6251 line 10 uses it.

Two kinds of test:

- Differential. Lines 1 to 47 of the 2025 Schedule D Tax Worksheet (2025
  Instructions for Schedule D, pages 15 and 16) are transcribed below line by
  line, with every "skip" instruction, the Form 4952 line 4g election (lines
  3 to 9, with line 4 from Form 4952 lines 4d and 4e), capital gain
  distributions (Schedule D line 13), short-term losses, and Schedule D lines
  18 and 19. The tax at the regular rates is the 2025 Tax Computation
  Worksheet, extended below $100,000 at the same rates as the model does
  (the Tax Table rounds within $50 rows). For 2026 the same worksheet runs on
  Rev. Proc. 2025-32's amounts: the rate tables of section 4.01 and the
  maximum zero and 15 percent rate amounts of section 4.03. Every household
  is compared line by line with the model. Schedule D lines 18 and 19 are
  the 28 percent rate gain and unrecaptured section 1250 gain as entered, as
  the model takes them.
- Properties that hold for every household and year, from the model alone:
  1. 0 <= regular tax <= line 46, the tax on all taxable income at the
     regular rates ("shall not exceed").
  2. The preferential computation never exceeds the ordinary one:
     0 <= capital_gains_tax <= line 46 - income_tax_main_rates, so the
     main-rates tax is never more than the regular tax.
  3. Identities: regular_tax_before_credits is income_tax_main_rates plus
     capital_gains_tax; income_tax_before_credits is the regular tax plus
     the AMT; and the AMT is Form 6251 line 9 less line 10 (the regular tax),
     if more than zero.
  4. Without qualified dividends or net capital gain, the regular tax is
     line 46.
  5. Worksheet lines: line 10 is the net capital gain, line 13 the adjusted
     net capital gain, line 18 <= line 21 <= line 14, and the main-rates tax
     is the tax on line 21.
  6. More wages, long-term gain or qualified dividends never lower the
     regular tax.
  7. A household's results do not depend on the other households in its
     batch or their order.
  And, for every year from 2018 and every filing status, the line 46 limit
  binds exactly where the 0 percent rate amount ends below the top of the
  12 percent bracket.
"""

from collections import namedtuple

import numpy as np
import pytest

from policyengine_us import Simulation
from policyengine_us.system import system as SYSTEM

# Hypothesis is a dev extra; skip rather than fail collection without it.
hypothesis = pytest.importorskip("hypothesis")
st = pytest.importorskip("hypothesis.strategies")

STATUSES = ["SINGLE", "JOINT", "SEPARATE", "HEAD_OF_HOUSEHOLD", "SURVIVING_SPOUSE"]
INF = float("inf")

# ---------------------------------------------------------------------------
# Dollar amounts.
# ---------------------------------------------------------------------------

Amounts = namedtuple(
    "Amounts",
    [
        "zero_rate",  # worksheet line 15
        "below_25_percent",  # worksheet line 19, the top of the 24% bracket
        "fifteen_rate",  # worksheet line 26
        "brackets",  # (top, rate) rows of the regular rate schedule
    ],
)


def _rows(*tops):
    """The 10 to 37 percent schedule with the given bracket tops."""
    rates = [0.10, 0.12, 0.22, 0.24, 0.32, 0.35, 0.37]
    return list(zip(list(tops) + [INF], rates))


# 2025: Schedule D Tax Worksheet lines 15, 19 and 26 as printed; the bracket
# tops are the rows of the 2025 Tax Computation Worksheet (2025 Instructions
# for Form 1040, line 16), whose subtraction amounts imply the 10 and 12
# percent tops (single: 22% x 48,475 - 5,086 = 5,578.50 = 10% x 11,925 +
# 12% x 36,550).
_UNMARRIED_2025 = (11_925, 48_475, 103_350, 197_300, 250_525)
AMOUNTS = {
    2025: Amounts(
        zero_rate={
            "SINGLE": 48_350,
            "SEPARATE": 48_350,
            "JOINT": 96_700,
            "SURVIVING_SPOUSE": 96_700,
            "HEAD_OF_HOUSEHOLD": 64_750,
        },
        below_25_percent={
            "SINGLE": 197_300,
            "SEPARATE": 197_300,
            "JOINT": 394_600,
            "SURVIVING_SPOUSE": 394_600,
            "HEAD_OF_HOUSEHOLD": 197_300,
        },
        fifteen_rate={
            "SINGLE": 533_400,
            "SEPARATE": 300_000,
            "JOINT": 600_050,
            "SURVIVING_SPOUSE": 600_050,
            "HEAD_OF_HOUSEHOLD": 566_700,
        },
        brackets={
            "SINGLE": _rows(*_UNMARRIED_2025, 626_350),
            "SEPARATE": _rows(*_UNMARRIED_2025, 375_800),
            "JOINT": _rows(23_850, 96_950, 206_700, 394_600, 501_050, 751_600),
            "SURVIVING_SPOUSE": _rows(
                23_850, 96_950, 206_700, 394_600, 501_050, 751_600
            ),
            "HEAD_OF_HOUSEHOLD": _rows(
                17_000, 64_850, 103_350, 197_300, 250_500, 626_350
            ),
        },
    ),
    # 2026: Rev. Proc. 2025-32, section 4.01 (Tables 1 to 4) and section 4.03.
    2026: Amounts(
        zero_rate={
            "SINGLE": 49_450,
            "SEPARATE": 49_450,
            "JOINT": 98_900,
            "SURVIVING_SPOUSE": 98_900,
            "HEAD_OF_HOUSEHOLD": 66_200,
        },
        below_25_percent={
            "SINGLE": 201_775,
            "SEPARATE": 201_775,
            "JOINT": 403_550,
            "SURVIVING_SPOUSE": 403_550,
            "HEAD_OF_HOUSEHOLD": 201_750,
        },
        fifteen_rate={
            "SINGLE": 545_500,
            "SEPARATE": 306_850,
            "JOINT": 613_700,
            "SURVIVING_SPOUSE": 613_700,
            "HEAD_OF_HOUSEHOLD": 579_600,
        },
        brackets={
            "SINGLE": _rows(12_400, 50_400, 105_700, 201_775, 256_225, 640_600),
            "SEPARATE": _rows(12_400, 50_400, 105_700, 201_775, 256_225, 384_350),
            "JOINT": _rows(24_800, 100_800, 211_400, 403_550, 512_450, 768_700),
            "SURVIVING_SPOUSE": _rows(
                24_800, 100_800, 211_400, 403_550, 512_450, 768_700
            ),
            "HEAD_OF_HOUSEHOLD": _rows(
                17_700, 67_450, 105_700, 201_750, 256_200, 640_600
            ),
        },
    ),
}


def regular_rate_tax(amount, status, year):
    """The tax on an amount at the regular rates."""
    tax, bottom = 0.0, 0.0
    for top, rate in AMOUNTS[year].brackets[status]:
        if amount <= bottom:
            break
        tax += rate * (min(amount, top) - bottom)
        bottom = top
    return tax


def test_rate_schedules_match_the_printed_amounts():
    """The rows reproduce the printed tax amounts: the 2025 Tax Computation
    Worksheet's subtraction amounts and Rev. Proc. 2025-32's bases."""
    # 2025, rate x amount - subtraction at the top of each row.
    for status, row_top, rate, subtraction in [
        ("SINGLE", 197_300, 0.24, 7_153),
        ("SINGLE", 626_350, 0.35, 30_452.75),
        ("SEPARATE", 375_800, 0.35, 30_452.75),
        ("JOINT", 751_600, 0.35, 60_905.50),
        ("HEAD_OF_HOUSEHOLD", 250_500, 0.32, 24_676),
    ]:
        assert regular_rate_tax(row_top, status, 2025) == pytest.approx(
            rate * row_top - subtraction
        )
    # 2026, the base at the bottom of a row.
    for status, row_bottom, base in [
        ("SINGLE", 640_600, 192_979.25),
        ("SEPARATE", 384_350, 103_291.75),
        ("JOINT", 768_700, 206_583.50),
        ("HEAD_OF_HOUSEHOLD", 640_600, 191_171),
    ]:
        assert regular_rate_tax(row_bottom, status, 2026) == pytest.approx(base)


# ---------------------------------------------------------------------------
# The 2025 Schedule D Tax Worksheet, transcribed.
# ---------------------------------------------------------------------------


def schedule_d_tax_worksheet(h, line_1, status, year):
    """Lines 1 to 47. Returns a dict of line amounts, with line 47 the tax."""
    a = AMOUNTS[year]
    schedule_d_15 = h["long_term"] + h["distributions"]
    schedule_d_16 = schedule_d_15 + h["short_term"]
    schedule_d_18 = h["collectibles"]
    schedule_d_19 = h["section_1250"]
    line = {1: line_1}
    line[46] = regular_rate_tax(line_1, status, year)
    # "Exception: Don't use the Qualified Dividends and Capital Gain Tax
    # Worksheet or this worksheet to figure your tax if: Line 15 or line 16
    # of Schedule D is zero or less and you have no qualified dividends ...;
    # or Form 1040 ... line 15, is zero or less."
    if (min(schedule_d_15, schedule_d_16) <= 0 and h["dividends"] == 0) or (
        line_1 <= 0
    ):
        line[47] = line[46]
        return line
    line[2] = h["dividends"]
    line[3] = h["election"]
    # Form 4952 line 4d, "the excess, if any, of your total gains over your
    # total losses", and line 4e, the smaller of line 4d or "the excess, if
    # any, of your net long-term capital gain over your net short-term
    # capital loss", with every capital asset held for investment.
    line_4d = max(0, schedule_d_16)
    line[4] = min(line_4d, max(0, schedule_d_15 - max(0, -h["short_term"])))
    line[5] = max(0, line[3] - line[4])
    line[6] = max(0, line[2] - line[5])
    line[7] = min(schedule_d_15, schedule_d_16)
    line[8] = min(line[3], line[4])
    line[9] = max(0, line[7] - line[8])
    line[10] = line[6] + line[9]
    line[11] = schedule_d_18 + schedule_d_19
    line[12] = min(line[9], line[11])
    line[13] = line[10] - line[12]
    line[14] = max(0, line[1] - line[13])
    line[15] = a.zero_rate[status]
    line[16] = min(line[1], line[15])
    line[17] = min(line[14], line[16])
    line[18] = max(0, line[1] - line[10])
    line[19] = min(line[1], a.below_25_percent[status])
    line[20] = min(line[14], line[19])
    line[21] = max(line[18], line[20])
    line[22] = line[16] - line[17]
    for i in range(23, 44):
        line[i] = 0
    # "If lines 1 and 16 are the same, skip lines 23 through 43."
    if line[1] != line[16]:
        line[23] = min(line[1], line[13])
        line[24] = line[22]
        line[25] = max(0, line[23] - line[24])
        line[26] = a.fifteen_rate[status]
        line[27] = min(line[1], line[26])
        line[28] = line[21] + line[22]
        line[29] = max(0, line[27] - line[28])
        line[30] = min(line[25], line[29])
        line[31] = 0.15 * line[30]
        line[32] = line[24] + line[30]
        # "If lines 1 and 32 are the same, skip lines 33 through 43."
        if line[1] != line[32]:
            line[33] = line[23] - line[32]
            line[34] = 0.20 * line[33]
            # "If Schedule D, line 19, is zero or blank, skip lines 35
            # through 40."
            if schedule_d_19 > 0:
                line[35] = min(line[9], schedule_d_19)
                line[36] = line[10] + line[21]
                line[37] = line[1]
                line[38] = max(0, line[36] - line[37])
                line[39] = max(0, line[35] - line[38])
                line[40] = 0.25 * line[39]
            # "If Schedule D, line 18, is zero or blank, skip lines 41
            # through 43."
            if schedule_d_18 > 0:
                line[41] = line[21] + line[22] + line[30] + line[33] + line[39]
                line[42] = line[1] - line[41]
                line[43] = 0.28 * line[42]
    line[44] = regular_rate_tax(line[21], status, year)
    line[45] = line[31] + line[34] + line[40] + line[43] + line[44]
    line[47] = min(line[45], line[46])
    return line


def assert_worksheet_identities(line):
    """Identities of the transcription itself."""
    if 2 not in line:
        return
    # Lines 21, 22, 30, 33, 39 and 42 split line 1 among the regular rates
    # and the 0, 15, 20, 25 and 28 percent rates. Where the worksheet skips
    # lines, the lines it skips would be zero.
    split = line[21] + line[22] + line[30] + line[33] + line[39] + line[42]
    assert split == pytest.approx(line[1], abs=0.01), line
    assert line[45] >= line[44] >= 0
    assert line[47] == min(line[45], line[46])
    assert line[18] <= line[21] <= max(line[14], line[18])


# ---------------------------------------------------------------------------
# The model.
# ---------------------------------------------------------------------------

OUTPUTS = [
    "filing_status",
    "taxable_income",
    "has_qdiv_or_ltcg",
    "net_capital_gain",
    "adjusted_net_capital_gain",
    "capital_gains_excluded_from_taxable_income",
    "dwks10",
    "dwks13",
    "dwks14",
    "dwks19",
    "income_tax_main_rates",
    "capital_gains_tax",
    "tax_on_taxable_income_at_main_rates",
    "regular_tax_before_credits",
    "amt_part_iii_required",
    "amt_base_tax",
    "amt_tax_including_cg",
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
            "qualified_dividend_income": {year: h["dividends"]},
            "long_term_capital_gains": {year: h["long_term"]},
            "short_term_capital_gains": {year: h["short_term"]},
            "non_sch_d_capital_gains": {year: h["distributions"]},
            "investment_income_elected_form_4952": {year: h["election"]},
            # Schedule D line 18 is part of the long-term gain.
            "long_term_capital_gains_on_collectibles": {year: h["collectibles"]},
        }
        members = [head]
        marital_units[f"marital_unit_{i}"] = {"members": [head]}
        if h["status"] == "JOINT":
            spouse = f"spouse_{i}"
            people[spouse] = {"age": {year: 45}}
            members.append(spouse)
            marital_units[f"marital_unit_{i}"]["members"].append(spouse)
        if h["status"] in ("HEAD_OF_HOUSEHOLD", "SURVIVING_SPOUSE"):
            # Old enough to be a dependent without a child tax credit.
            child = f"child_{i}"
            people[child] = {"age": {year: 17}}
            members.append(child)
            marital_units[f"marital_unit_{i}_child"] = {"members": [child]}
        tax_units[f"tax_unit_{i}"] = {
            "members": members,
            # Set for every tax unit: an input given to only some of them
            # leaves the rest at the default (single).
            "filing_status": {year: h["status"]},
            "unrecaptured_section_1250_gain": {year: h["section_1250"]},
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
    return results


def tolerance(*amounts):
    """Five cents, plus the rounding of single-precision arithmetic.

    The model stores amounts as 32-bit floats, which carry about seven
    significant digits.
    """
    return 0.05 + 5e-7 * np.max(np.abs(amounts), axis=0)


# ---------------------------------------------------------------------------
# Checks.
# ---------------------------------------------------------------------------


def assert_matches_worksheet(households, law, year):
    """The model against the transcribed worksheet, household by household."""
    for i, h in enumerate(households):
        status = law["filing_status"][i]
        assert status == h["status"], (i, status)
        line_1 = float(law["taxable_income"][i])
        line = schedule_d_tax_worksheet(h, line_1, status, year)
        assert_worksheet_identities(line)
        slack = tolerance(line_1)
        context = (i, h, line)
        assert float(law["tax_on_taxable_income_at_main_rates"][i]) == pytest.approx(
            line[46], abs=slack
        ), context
        assert float(law["regular_tax_before_credits"][i]) == pytest.approx(
            line[47], abs=slack
        ), context
        if 2 in line:
            assert float(law["income_tax_main_rates"][i]) == pytest.approx(
                line[44], abs=slack
            ), context
            assert float(law["capital_gains_tax"][i]) == pytest.approx(
                line[47] - line[44], abs=slack
            ), context
            for model_line, worksheet_line in (
                ("dwks10", 10),
                ("dwks13", 13),
                ("dwks14", 14),
                ("dwks19", 21),
            ):
                assert float(law[model_line][i]) == pytest.approx(
                    line[worksheet_line], abs=slack
                ), (model_line, context)


def assert_properties(households, law):
    """Properties 1 to 5, for every household."""
    line_1 = law["taxable_income"].astype(float)
    tol = tolerance(line_1)
    main = law["income_tax_main_rates"].astype(float)
    gains_tax = law["capital_gains_tax"].astype(float)
    regular = law["regular_tax_before_credits"].astype(float)
    line_46 = law["tax_on_taxable_income_at_main_rates"].astype(float)
    amt = law["alternative_minimum_tax"].astype(float)
    # 1. "Shall not exceed": 0 <= regular tax <= line 46.
    assert (regular >= 0).all()
    assert (regular <= line_46 + tol).all()
    # 2. The preferential computation never exceeds the ordinary one.
    assert (gains_tax >= 0).all()
    assert (gains_tax <= line_46 - main + tol).all()
    assert (main <= regular + tol).all()
    # 3. Identities, to single-precision rounding (the model adds 32-bit
    # floats: near $384,000 they are 3 cents apart).
    assert (np.abs(regular - (main + gains_tax)) <= tol).all()
    before_credits = law["income_tax_before_credits"].astype(float)
    assert (np.abs(before_credits - (regular + amt)) <= tol).all()
    # Form 6251 lines 9 to 11, with no foreign tax credit or Form 4972.
    line_9 = np.where(
        law["amt_part_iii_required"],
        np.minimum(law["amt_base_tax"], law["amt_tax_including_cg"]),
        law["amt_base_tax"],
    ).astype(float)
    assert (np.abs(amt - np.maximum(0, line_9 - regular)) <= tol).all()
    # 4. No dividends or gain: the regular tax is line 46, bit for bit.
    no_gain = law["net_capital_gain"] == 0
    assert np.array_equal(regular[no_gain], line_46[no_gain])
    # 5. Worksheet lines.
    has_gains = law["has_qdiv_or_ltcg"].astype(bool)
    assert np.allclose(
        law["dwks10"], law["net_capital_gain"], rtol=0, atol=0.01 + 1e-6 * line_1
    )
    assert np.allclose(
        law["dwks13"][has_gains],
        law["adjusted_net_capital_gain"][has_gains],
        rtol=0,
        atol=(0.01 + 1e-6 * line_1)[has_gains],
    )
    line_14 = law["dwks14"].astype(float)
    line_21 = law["dwks19"].astype(float)
    line_18 = np.where(has_gains, np.maximum(0, line_1 - law["dwks10"]), 0)
    assert (line_18 <= line_21 + tol).all()
    assert (line_21 <= line_14 + tol).all()
    # income_tax_main_rates taxes line 21, the amount section 1(h)(1)(A)
    # taxes at the regular rates.
    regular_rate_amount = np.maximum(
        0, line_1 - law["capital_gains_excluded_from_taxable_income"]
    )
    assert np.allclose(
        line_21[has_gains], regular_rate_amount[has_gains], rtol=0, atol=tol[has_gains]
    )


# ---------------------------------------------------------------------------
# Households.
# ---------------------------------------------------------------------------

DOLLARS = 2_000_000


@st.composite
def households(draw):
    long_term = draw(st.one_of(st.just(0), st.integers(-50_000, DOLLARS)))
    short_term = draw(st.one_of(st.just(0), st.integers(-100_000, 300_000)))
    distributions = draw(st.one_of(st.just(0), st.integers(1, 100_000)))
    dividends = draw(st.one_of(st.just(0), st.integers(1, 400_000)))
    gain = max(0, min(long_term, long_term + short_term) + distributions)
    # Schedule D lines 18 and 19 as shares of the long-term gain.
    collectibles = max(0, long_term) * draw(st.sampled_from([0, 0, 10, 50, 100])) // 100
    section_1250 = max(0, long_term) * draw(st.sampled_from([0, 0, 20, 60, 100])) // 100
    return {
        "status": draw(st.sampled_from(STATUSES)),
        "wages": draw(st.one_of(st.just(0), st.integers(1, 1_500_000))),
        "dividends": dividends,
        "long_term": long_term,
        "short_term": short_term,
        "distributions": distributions,
        "election": draw(
            st.one_of(
                st.just(0),
                st.just(0),
                st.integers(1, DOLLARS),
                st.sampled_from([gain, gain + dividends]),
            )
        ),
        "collectibles": collectibles,
        "section_1250": section_1250,
    }


def household(status, wages=0, dividends=0, long_term=0, **rest):
    return {
        "status": status,
        "wages": wages,
        "dividends": dividends,
        "long_term": long_term,
        "short_term": rest.get("short_term", 0),
        "distributions": rest.get("distributions", 0),
        "election": rest.get("election", 0),
        "collectibles": rest.get("collectibles", 0),
        "section_1250": rest.get("section_1250", 0),
    }


# Wages that put taxable income, with the standard deduction, near the lines
# where the limit binds: the 0 percent rate amount, the top of the 12 percent
# bracket and the top of the 24 percent bracket.
GRID = [
    household(status, wages=wages, dividends=dividends, long_term=long_term, **rest)
    for status in STATUSES
    for wages in (0, 40_000, 64_000, 110_000, 250_000, 450_000, 900_000)
    for dividends, long_term, rest in (
        (0, 0, {}),
        (125, 0, {}),
        (250, 0, {}),
        (2_000, 0, {}),
        (0, 30_000, {"short_term": -10_000}),
        (5_000, 80_000, {"election": 20_000}),
        (0, 200_000, {"collectibles": 50_000, "section_1250": 60_000}),
        (10_000, 600_000, {"distributions": 4_000, "section_1250": 100_000}),
    )
]


# Standard deductions (2025: Rev. Proc. 2025-32, section 3.01; 2026: section
# 4.14(1)). The surviving spouse here has a dependent child.
STANDARD_DEDUCTION = {
    2025: {"SINGLE": 15_750, "SEPARATE": 15_750, "JOINT": 31_500},
    2026: {"SINGLE": 16_100, "SEPARATE": 16_100, "JOINT": 32_200},
}
for _year, _head in ((2025, 23_625), (2026, 24_150)):
    STANDARD_DEDUCTION[_year]["HEAD_OF_HOUSEHOLD"] = _head
    STANDARD_DEDUCTION[_year]["SURVIVING_SPOUSE"] = STANDARD_DEDUCTION[_year]["JOINT"]


def boundary_households(year):
    """Ordinary taxable income equal to the 0 percent rate amount, and
    qualified dividends up to the top of the 12 percent bracket, then a dollar
    less and a dollar more: line 45 exceeds line 46 by 3 percent of the
    dividends inside the band."""
    out = []
    for status in STATUSES:
        zero_rate = AMOUNTS[year].zero_rate[status]
        top_of_12 = AMOUNTS[year].brackets[status][1][0]
        wages = zero_rate + STANDARD_DEDUCTION[year][status]
        for dividends in (top_of_12 - zero_rate + d for d in (-1, 0, 1)):
            out.append(household(status, wages=wages, dividends=dividends))
    return out


def test_grid_matches_worksheet_2025_and_2026():
    for year in (2025, 2026):
        households = GRID + boundary_households(year)
        law = calculate(households, year)
        assert_matches_worksheet(households, law, year)
        assert_properties(households, law)
        lines = [
            schedule_d_tax_worksheet(
                h, float(law["taxable_income"][i]), h["status"], year
            )
            for i, h in enumerate(households)
        ]
        excess = np.array(
            [line[45] - line[46] if 45 in line else 0.0 for line in lines]
        )
        # Every boundary household's line 45 exceeds its line 46, by 3
        # percent of the dividends that fit in the band.
        boundary = excess[len(GRID) :].reshape(len(STATUSES), 3)
        bands = np.array(
            [
                AMOUNTS[year].brackets[status][1][0] - AMOUNTS[year].zero_rate[status]
                for status in STATUSES
            ]
        )
        expected = 0.03 * np.stack([bands - 1, bands, bands], axis=1)
        # A dollar above the band is taxed at 22 percent on line 46 and 15 on
        # line 45, which takes 7 cents off the excess.
        expected[:, 2] -= 0.07
        assert boundary == pytest.approx(expected, abs=0.01), year


def test_line_45_above_line_46_by_hand():
    # 2026, single: 49,450 of ordinary taxable income and 950 of qualified
    # dividends. Line 44, the tax on 49,450, is 1,240 + 12% x 37,050 =
    # 5,686; line 30 is 950 (15%: 142.50), so line 45 is 5,828.50. Line 46,
    # the tax on 50,400, is 5,800 (Rev. Proc. 2025-32, Table 3).
    h = household("SINGLE", wages=50_400 + 16_100 - 950, dividends=950)
    law = calculate([h], 2026)
    assert law["taxable_income"][0] == 50_400
    line = schedule_d_tax_worksheet(h, 50_400, "SINGLE", 2026)
    assert (line[44], line[45], line[46], line[47]) == pytest.approx(
        (5_686, 5_828.50, 5_800, 5_800)
    )
    assert law["income_tax_main_rates"][0] == pytest.approx(5_686)
    assert law["capital_gains_tax"][0] == pytest.approx(114)
    assert law["regular_tax_before_credits"][0] == pytest.approx(5_800)
    assert_matches_worksheet([h], law, 2026)


def test_limit_binds_at_the_top_of_the_12_percent_bracket_every_year():
    """From 2018, for every filing status: taxable income at the top of the
    12 percent bracket, with qualified dividends from the 0 percent rate amount
    up. The dividends are taxed at 15 percent on line 45 and 12 percent on
    line 46, so the regular tax is line 46, and the capital gains tax is 12
    percent of the dividends."""
    for year in range(2018, 2036):
        p = SYSTEM.parameters(f"{year}-01-01").gov.irs
        situation = {"people": {}, "tax_units": {}, "households": {}}
        bands = []
        for i, status in enumerate(STATUSES):
            top_of_12 = float(p.income.bracket.thresholds["2"][status])
            zero_rate = float(p.capital_gains.thresholds["1"][status])
            band = max(0.0, top_of_12 - zero_rate)
            bands.append(band)
            situation["people"][f"person_{i}"] = {
                "age": {year: 45},
                "qualified_dividend_income": {year: band},
            }
            situation["tax_units"][f"tax_unit_{i}"] = {
                "members": [f"person_{i}"],
                "filing_status": {year: status},
                "taxable_income": {year: top_of_12},
            }
            situation["households"][f"household_{i}"] = {
                "members": [f"person_{i}"],
                "state_code": {year: "TX"},
            }
        sim = Simulation(situation=situation)
        bands = np.array(bands)
        ordinary_rate = p.income.bracket.rates["2"]
        preferential_rate = p.capital_gains.rates["2"]
        assert preferential_rate > ordinary_rate, year
        regular = sim.calculate("regular_tax_before_credits", year)
        line_46 = sim.calculate("tax_on_taxable_income_at_main_rates", year)
        gains_tax = sim.calculate("capital_gains_tax", year)
        assert np.allclose(regular, line_46, rtol=0, atol=0.01), year
        assert np.allclose(gains_tax, ordinary_rate * bands, rtol=0, atol=0.01), year
        # The band is $100 to $250 wide from 2018 to 2025 and $950 to $1,900
        # in 2026 (Rev. Proc. 2025-32), the published years.
        if year <= 2025:
            assert ((bands >= 100) & (bands <= 250)).all(), (year, bands)
        elif year == 2026:
            assert ((bands >= 950) & (bands <= 1_900)).all(), (year, bands)


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
    st.lists(households(), min_size=1, max_size=25), st.sampled_from([2025, 2026])
)
def test_random_households_match_worksheet(batch, year):
    law = calculate(batch, year)
    assert_matches_worksheet(batch, law, year)
    assert_properties(batch, law)


@hypothesis.settings(**SETTINGS)
@hypothesis.given(
    st.lists(households(), min_size=1, max_size=15),
    st.sampled_from([2018, 2021, 2024, 2025, 2026, 2027, 2030, 2035]),
    st.integers(1, 50_000),
)
# Capital gain distributions with a Schedule D net loss. Before #9788, gross
# income added the distributions outside the Schedule D loss limit, while
# net_capital_gain nets them on Schedule D line 13, so $1 more long-term gain
# raised net capital gain but not taxable income and cut this 2018 single
# filer's regular tax by $0.12.
@hypothesis.example(
    [
        household("SINGLE"),
        household("SINGLE", short_term=-40_273, distributions=50_000),
    ],
    2018,
    1,
)
def test_random_households_keep_the_properties(batch, year, more):
    """Properties 1 to 7 in years without a transcription."""
    count = len(batch)
    variants = (
        batch
        + [{**h, "wages": h["wages"] + more} for h in batch]
        + [{**h, "long_term": max(0, h["long_term"]) + more} for h in batch]
        + [{**h, "dividends": h["dividends"] + more} for h in batch]
    )
    law = calculate(variants, year)
    assert_properties(variants, law)
    regular = law["regular_tax_before_credits"].astype(float).reshape(4, count)
    tol = tolerance(law["taxable_income"].astype(float)).reshape(4, count)
    # 6. More wages, long-term gain or dividends never lower the regular tax.
    # (Raising a long-term loss to a gain is also more income.)
    for k in (1, 2, 3):
        assert (regular[k] >= regular[0] - tol[k]).all(), k
    # 7. The same households in reverse order give the same results.
    reverse = calculate(batch[::-1], year)
    for v in OUTPUTS:
        assert np.array_equal(reverse[v][::-1], law[v][:count]), v

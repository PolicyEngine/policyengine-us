"""Property and differential tests for Form 6251 Part III (26 U.S.C. 55(b)(3)).

Section 55(b)(3) caps the tentative minimum tax of a taxpayer with net
capital gain at the tax on the taxable excess less the gains, figured "at the
rates and in the same manner as if this paragraph had not been enacted", plus
the 0, 15, 20 and 25 percent amounts on the gains. "In the same manner"
carries section 55(b)(1)(C): "In the case of a married individual filing a
separate return, subparagraph (A) shall be applied by substituting 50
percent of the dollar amount otherwise applicable under clause (i) and
clause (ii) thereof." The 2025 Form 6251 applies the same schedule on line 18
(to line 17, line 12 less the gains) and on line 39 (to line 12): "If line 17
is $239,100 or less ($119,550 or less if married filing separately),
multiply line 17 by 26% (0.26). Otherwise, multiply line 17 by 28% (0.28)
and subtract $4,782 ($2,391 if married filing separately) from the result."

Two kinds of test:

- Differential. Lines 12 to 40 of the 2025 Form 6251 are transcribed below
  and compared, household by household and for every filing status, with
  `amt_tax_including_cg` (line 38), `amt_base_tax` (line 39) and
  `alternative_minimum_tax` (line 11). Line 13 comes from the household's own
  dividends and gains (Qualified Dividends and Capital Gain Tax Worksheet,
  line 4), not from the model's worksheet variables.
- Properties that hold for every household and year:
  - Part III never exceeds line 39 on the same line 12 by more than
    rounding. The gains taxed in Part III are at most 25 percent, below the
    26 percent floor of the line 39 schedule, and line 18 taxes the rest on
    the same schedule as line 39.
  - With no qualified dividends or capital gain, line 17 equals line 12, so
    line 18 equals line 39.
  - For filers other than married filing separately, line 18 is the AMT
    scale applied with no factor, bit for bit: their multiplier is 1.

Households with 28-percent rate or unrecaptured section 1250 gain go through
the Schedule D Tax Worksheet. Its 2025 lines 1 to 47 are transcribed below
too, and for those households the model is compared with:

- line 47, the regular tax (`income_tax_main_rates` plus
  `capital_gains_tax`), which taxes at the regular rates the greater of line
  18 or line 20 (line 21), where line 19 is the taxable income taxed at a
  rate below 25 percent (26 U.S.C. 1(h)(1)(A)(ii)(I));
- Form 6251 lines 38 to 40 and 11, with line 14 from Schedule D line 19,
  line 15 capped by worksheet line 10, line 27 from worksheet line 21 and
  lines 35 to 37 taxing the rest of the unrecaptured gain at 25 percent.

Further properties for those households: worksheet line 21 lies between
lines 18 and 14, and equals line 14 without either kind of gain (so line 27
is then line 20, line 5 of the capital gains worksheet); the regular tax
never exceeds the tax on all taxable income at the regular rates (line 46).
"""

import numpy as np
import pytest

from policyengine_us import Simulation
from policyengine_us.system import system as SYSTEM

# Hypothesis is a dev extra; skip rather than fail collection without it.
hypothesis = pytest.importorskip("hypothesis")
st = pytest.importorskip("hypothesis.strategies")

STATUSES = ["SINGLE", "JOINT", "SEPARATE", "HEAD_OF_HOUSEHOLD", "SURVIVING_SPOUSE"]

# ---------------------------------------------------------------------------
# The 2025 Form 6251, transcribed.
# ---------------------------------------------------------------------------

# Line 19.
ZERO_RATE_AMOUNT_2025 = {
    "SINGLE": 48_350,
    "SEPARATE": 48_350,
    "JOINT": 96_700,
    "SURVIVING_SPOUSE": 96_700,
    "HEAD_OF_HOUSEHOLD": 64_750,
}
# Line 25.
FIFTEEN_PERCENT_RATE_AMOUNT_2025 = {
    "SINGLE": 533_400,
    "SEPARATE": 300_000,
    "JOINT": 600_050,
    "SURVIVING_SPOUSE": 600_050,
    "HEAD_OF_HOUSEHOLD": 566_700,
}


def amt_rates_2025(amount, status):
    """Form 6251 (2025) lines 18 and 39, and line 7 "All others"."""
    if status == "SEPARATE":
        return 0.26 * amount if amount <= 119_550 else 0.28 * amount - 2_391
    return 0.26 * amount if amount <= 239_100 else 0.28 * amount - 4_782


def form_6251_part_iii_2025(
    line_12,
    line_13,
    line_20,
    status,
    line_14=0,
    worksheet_line_10=None,
    line_27=None,
):
    """2025 Form 6251, lines 12 to 40.

    With no Schedule D Tax Worksheet, line 14 is zero, line 15 is line 13
    and line 27 is line 20 (line 5 of the capital gains worksheet). With
    one, pass line 14 (Schedule D line 19), the worksheet's line 10 and its
    line 21 for line 27.
    Returns lines 17, 38, 39 and 40.
    """
    if worksheet_line_10 is None:
        line_15 = line_13
    else:
        line_15 = min(line_13 + line_14, worksheet_line_10)
    if line_27 is None:
        line_27 = line_20
    line_16 = min(line_12, line_15)
    line_17 = line_12 - line_16
    line_18 = amt_rates_2025(line_17, status)
    line_21 = max(0, ZERO_RATE_AMOUNT_2025[status] - line_20)
    line_22 = min(line_12, line_13)
    line_23 = min(line_21, line_22)
    line_24 = line_22 - line_23
    line_26 = line_21
    line_28 = line_26 + line_27
    line_29 = max(0, FIFTEEN_PERCENT_RATE_AMOUNT_2025[status] - line_28)
    line_30 = min(line_24, line_29)
    line_31 = 0.15 * line_30
    line_32 = line_23 + line_30
    line_33 = line_34 = line_37 = 0
    # "If lines 32 and 12 are the same, skip lines 33 through 37."
    if line_32 != line_12:
        line_33 = line_22 - line_32
        line_34 = 0.20 * line_33
        # "If line 14 is zero or blank, skip lines 35 through 37."
        if line_14 > 0:
            line_35 = line_17 + line_32 + line_33
            line_36 = line_12 - line_35
            line_37 = 0.25 * line_36
    line_38 = line_18 + line_31 + line_34 + line_37
    line_39 = amt_rates_2025(line_12, status)
    return line_17, line_38, line_39, min(line_38, line_39)


# The 2025 Schedule D Tax Worksheet (Instructions for Schedule D (Form 1040)).
# Line 19: the smaller of line 1 or these amounts, the top of the 24 percent
# bracket.
BELOW_25_PERCENT_AMOUNT_2025 = {
    "SINGLE": 197_300,
    "SEPARATE": 197_300,
    "JOINT": 394_600,
    "SURVIVING_SPOUSE": 394_600,
    "HEAD_OF_HOUSEHOLD": 197_300,
}

# Lines 44 and 46 tax amounts at the regular rates. These are the rows of the
# 2025 Tax Computation Worksheet (2025 Instructions for Form 1040, page 80):
# (top of the row, multiplication amount, subtraction amount). The model taxes
# amounts under $100,000 at the same rates rather than at the Tax Table's
# midpoints, and so does this transcription. The 10 and 12 percent rows'
# tops are the lower brackets; each matches the Tax Table row containing it
# (for example, single $48,450-$48,500: $5,579, the tax on $48,475 rounded)
# and the 22 percent row's subtraction amount (for single, 10% of $48,475
# plus 2% of $11,925 is $5,086).
_UNMARRIED_ROWS = [
    (11_925, 0.10, 0),
    (48_475, 0.12, 238.50),
    (103_350, 0.22, 5_086),
    (197_300, 0.24, 7_153),
    (250_525, 0.32, 22_937),
]
TAX_COMPUTATION_ROWS_2025 = {
    "SINGLE": _UNMARRIED_ROWS
    + [(626_350, 0.35, 30_452.75), (float("inf"), 0.37, 42_979.75)],
    "SEPARATE": _UNMARRIED_ROWS
    + [(375_800, 0.35, 30_452.75), (float("inf"), 0.37, 37_968.75)],
    "JOINT": [
        (23_850, 0.10, 0),
        (96_950, 0.12, 477),
        (206_700, 0.22, 10_172),
        (394_600, 0.24, 14_306),
        (501_050, 0.32, 45_874),
        (751_600, 0.35, 60_905.50),
        (float("inf"), 0.37, 75_937.50),
    ],
    "HEAD_OF_HOUSEHOLD": [
        (17_000, 0.10, 0),
        (64_850, 0.12, 340),
        (103_350, 0.22, 6_825),
        (197_300, 0.24, 8_892),
        (250_500, 0.32, 24_676),
        (626_350, 0.35, 32_191),
        (float("inf"), 0.37, 44_718),
    ],
}
TAX_COMPUTATION_ROWS_2025["SURVIVING_SPOUSE"] = TAX_COMPUTATION_ROWS_2025["JOINT"]


def regular_tax_2025(amount, status):
    """The 2025 tax on an amount at the regular rates."""
    if amount <= 0:
        return 0
    for top, rate, subtraction in TAX_COMPUTATION_ROWS_2025[status]:
        if amount <= top:
            return rate * amount - subtraction


def schedule_d_tax_worksheet_2025(household, line_1, status):
    """2025 Schedule D Tax Worksheet, lines 1 to 47, with no Form 4952.

    Schedule D lines 18 and 19 are the household's 28 percent rate gain
    (collectibles) and unrecaptured section 1250 gain. Returns the lines.
    """
    long_term = household["long_term_gains"]
    schedule_d_18 = max(0, long_term) * household.get("collectibles_share", 0) / 100
    schedule_d_19 = max(0, long_term) * household.get("section_1250_share", 0) / 100
    line = {1: line_1}
    line[2] = household["qualified_dividends"]
    line[3] = line[4] = line[5] = 0
    line[6] = max(0, line[2] - line[5])
    # Schedule D line 15 is the long-term gain, line 16 the net gain.
    line[7] = min(long_term, long_term + household["short_term_gains"])
    line[8] = min(line[3], line[4])
    line[9] = max(0, line[7] - line[8])
    line[10] = line[6] + line[9]
    line[11] = schedule_d_18 + schedule_d_19
    line[12] = min(line[9], line[11])
    line[13] = line[10] - line[12]
    line[14] = max(0, line[1] - line[13])
    line[15] = ZERO_RATE_AMOUNT_2025[status]
    line[16] = min(line[1], line[15])
    line[17] = min(line[14], line[16])
    line[18] = max(0, line[1] - line[10])
    line[19] = min(line[1], BELOW_25_PERCENT_AMOUNT_2025[status])
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
        line[26] = FIFTEEN_PERCENT_RATE_AMOUNT_2025[status]
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
    if line[1] > 0:
        # Lines 21, 22, 30, 33, 39 and 42 split line 1: the amounts taxed at
        # the regular rates and at 0, 15, 20, 25 and 28 percent.
        split = line[21] + line[22] + line[30] + line[33] + line[39] + line[42]
        assert split == pytest.approx(line[1], abs=0.01), (household, line)
    line[44] = regular_tax_2025(line[21], status)
    line[45] = line[31] + line[34] + line[40] + line[43] + line[44]
    line[46] = regular_tax_2025(line[1], status)
    line[47] = min(line[45], line[46])
    line["schedule_d_19"] = schedule_d_19
    return line


def capital_gains_worksheet_line_4(household):
    """Qualified Dividends and Capital Gain Tax Worksheet, lines 2 to 4.

    Line 3 is the smaller of Schedule D lines 15 and 16, or zero if either
    is a loss.
    """
    long_term = household["long_term_gains"]
    net_gain = max(0, min(long_term, long_term + household["short_term_gains"]))
    return household["qualified_dividends"] + net_gain


# ---------------------------------------------------------------------------
# The model.
# ---------------------------------------------------------------------------

OUTPUTS = [
    "filing_status",
    "taxable_income",
    "has_qdiv_or_ltcg",
    "dwks10",
    "dwks14",
    "dwks19",
    "income_tax_main_rates",
    "regular_tax_before_credits",
    "capital_gains_tax",
    "amt_income_less_exemptions",
    "amt_tax_including_cg",
    "amt_base_tax",
    "alternative_minimum_tax",
]


def build_situation(households, year):
    people, tax_units, marital_units = {}, {}, {}
    groups = {"households": {}, "spm_units": {}, "families": {}}
    for i, h in enumerate(households):
        head = f"head_{i}"
        long_term = h["long_term_gains"]
        people[head] = {
            "age": {year: 45},
            "employment_income": {year: h["wages"]},
            "qualified_dividend_income": {year: h["qualified_dividends"]},
            "long_term_capital_gains": {year: long_term},
            "short_term_capital_gains": {year: h["short_term_gains"]},
            # Schedule D line 18 is part of the long-term gain.
            "long_term_capital_gains_on_collectibles": {
                year: max(0, long_term) * h.get("collectibles_share", 0) / 100
            },
            "real_estate_taxes": {year: h.get("real_estate_taxes", 0)},
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
            "unrecaptured_section_1250_gain": {
                year: max(0, long_term) * h.get("section_1250_share", 0) / 100
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
    return results


def tolerance(*amounts):
    """Five cents, plus the rounding of single-precision arithmetic.

    The model stores amounts as 32-bit floats, which carry about seven
    significant digits.
    """
    return 0.05 + 5e-7 * np.max(np.abs(amounts), axis=0)


def assert_matches_form_6251(households, law):
    """The 2025 model against the transcribed 2025 Form 6251."""
    for i, h in enumerate(households):
        status = law["filing_status"][i]
        assert status == h["status"], (i, status)
        line_12 = float(law["amt_income_less_exemptions"][i])
        line_13 = capital_gains_worksheet_line_4(h)
        line_20 = max(0, float(law["taxable_income"][i]) - line_13)
        _, line_38, line_39, line_40 = form_6251_part_iii_2025(
            line_12, line_13, line_20, status
        )
        part_iii = float(law["amt_tax_including_cg"][i])
        base = float(law["amt_base_tax"][i])
        assert part_iii == pytest.approx(line_38, abs=tolerance(line_12)), (i, h)
        assert base == pytest.approx(line_39, abs=tolerance(line_12)), (i, h)
        # Lines 9 to 11, with no foreign tax credit and no Form 4972.
        line_10 = float(law["regular_tax_before_credits"][i]) + float(
            law["capital_gains_tax"][i]
        )
        amt = max(0, line_40 - line_10)
        assert float(law["alternative_minimum_tax"][i]) == pytest.approx(
            amt, abs=tolerance(line_12, line_10)
        ), (i, h)


def assert_properties(households, law):
    part_iii = law["amt_tax_including_cg"].astype(float)
    base = law["amt_base_tax"].astype(float)
    line_12 = law["amt_income_less_exemptions"].astype(float)
    # Line 38 never exceeds line 39 on the same line 12.
    assert (part_iii <= base + tolerance(line_12)).all()
    # No dividends or gains: line 17 is line 12, so line 18 is line 39.
    no_gains = np.array(
        [
            h["qualified_dividends"] == 0
            and h["long_term_gains"] <= 0
            and h["short_term_gains"] <= 0
            for h in households
        ]
    )
    assert np.all(np.abs(part_iii - base)[no_gains] <= tolerance(line_12)[no_gains])


def assert_matches_schedule_d_tax_worksheet(households, law):
    """The 2025 model against the transcribed 2025 Schedule D Tax Worksheet.

    For households with no short-term loss, so that Schedule D lines 18 and
    19 are the 28 percent rate gain and unrecaptured section 1250 gain as
    entered (a short-term loss would reduce them on the 28% Rate Gain and
    Unrecaptured Section 1250 Gain Worksheets, which the model does not do).
    """
    for i, h in enumerate(households):
        assert h["short_term_gains"] >= 0, h
        status = law["filing_status"][i]
        assert status == h["status"], (i, status)
        line_1 = float(law["taxable_income"][i])
        regular_tax = float(law["income_tax_main_rates"][i]) + float(
            law["capital_gains_tax"][i]
        )
        if line_1 <= 0:
            assert regular_tax == 0, (i, h)
            continue
        worksheet = schedule_d_tax_worksheet_2025(h, line_1, status)
        if law["has_qdiv_or_ltcg"][i]:
            for model_line, worksheet_line in (
                ("dwks10", 10),
                ("dwks14", 14),
                ("dwks19", 21),
            ):
                assert float(law[model_line][i]) == pytest.approx(
                    worksheet[worksheet_line], abs=tolerance(line_1)
                ), (i, h, model_line)
        # Line 45. The model does not take the smaller of lines 45 and 46,
        # which differ only when a little gain taxed at 15 percent sits where
        # the regular rate is 12 percent.
        assert regular_tax == pytest.approx(worksheet[45], abs=tolerance(line_1)), (
            i,
            h,
            worksheet,
        )
        # Form 6251 Part III, with lines 14, 15 and 27 from the worksheet.
        line_12 = float(law["amt_income_less_exemptions"][i])
        _, line_38, line_39, line_40 = form_6251_part_iii_2025(
            line_12,
            worksheet[13],
            worksheet[14],
            status,
            line_14=worksheet["schedule_d_19"],
            worksheet_line_10=worksheet[10],
            line_27=worksheet[21],
        )
        assert float(law["amt_tax_including_cg"][i]) == pytest.approx(
            line_38, abs=tolerance(line_12)
        ), (i, h)
        assert float(law["amt_base_tax"][i]) == pytest.approx(
            line_39, abs=tolerance(line_12)
        ), (i, h)
        # Line 11, with line 10 the worksheet's regular tax (line 45, as
        # above) and no foreign tax credit.
        amt = max(0, line_40 - worksheet[45])
        assert float(law["alternative_minimum_tax"][i]) == pytest.approx(
            amt, abs=tolerance(line_12, line_1)
        ), (i, h)


def assert_schedule_d_properties(households, law):
    """Schedule D Tax Worksheet line 21 (`dwks19`), for every year."""
    line_1 = law["taxable_income"].astype(float)
    line_10 = law["dwks10"].astype(float)
    line_14 = law["dwks14"].astype(float)
    line_21 = law["dwks19"].astype(float)
    has_gains = law["has_qdiv_or_ltcg"].astype(bool)
    tol = tolerance(line_1)
    # Line 18 <= line 21 <= line 14: line 21 is the larger of line 18 and
    # the smaller of line 14 and line 19, and line 18 is at most line 14.
    line_18 = np.where(has_gains, np.maximum(0, line_1 - line_10), 0)
    assert (line_18 <= line_21 + tol).all()
    assert (line_21 <= line_14 + tol).all()
    # Without 28 percent rate or unrecaptured section 1250 gain, line 13 is
    # line 10, so line 21 is line 14 (QDCG Worksheet line 5), bit for bit,
    # and Form 6251 line 27 is line 20.
    plain = np.array(
        [
            h.get("collectibles_share", 0) == 0 and h.get("section_1250_share", 0) == 0
            for h in households
        ]
    )
    assert np.array_equal(line_21[plain], line_14[plain])


# ---------------------------------------------------------------------------
# Line 18 as a schedule.
# ---------------------------------------------------------------------------

FILING_STATUS = SYSTEM.variables["filing_status"].possible_values


@hypothesis.settings(max_examples=200, deadline=None, derandomize=True)
@hypothesis.given(
    st.lists(
        st.one_of(
            st.integers(0, 10_000_000),
            st.floats(0, 1e7, allow_nan=False, allow_infinity=False),
        ),
        min_size=1,
        max_size=40,
    ),
    st.integers(2013, 2035),
)
def test_line_18_schedule(amounts, year):
    # The AMT subtree only: the whole tree at an instant is slow to build.
    p = SYSTEM.parameters.gov.irs.income.amt(f"{year}-01-01")
    line_17 = np.repeat(np.array(amounts, dtype=float), len(STATUSES))
    statuses = np.tile(np.array(STATUSES), len(amounts))
    filing_status = FILING_STATUS.encode(statuses)
    line_18 = p.brackets.calc(line_17, factor=p.multiplier[filing_status])
    separate = statuses == "SEPARATE"
    # Everyone else: bit for bit the scale with no factor, on the same array.
    full = p.brackets.calc(line_17)
    assert np.array_equal(line_18[~separate], full[~separate])
    # Married filing separately: the breakpoint is halved (55(b)(1)(C)).
    breakpoint = p.brackets.thresholds[-1] / 2
    low, high = p.brackets.rates
    expected = np.where(
        line_17 <= breakpoint,
        low * line_17,
        high * line_17 - (high - low) * breakpoint,
    )
    assert line_18[separate] == pytest.approx(expected[separate], rel=1e-12, abs=1e-6)
    # Halving the breakpoint never lowers the tax, and raises it by the
    # rate difference on the part of line 17 between the two breakpoints.
    assert line_18[separate] - full[separate] == pytest.approx(
        (high - low) * np.clip(line_17[separate] - breakpoint, 0, breakpoint),
        rel=1e-9,
        abs=1e-6,
    )


# ---------------------------------------------------------------------------
# Households.
# ---------------------------------------------------------------------------

GRID = [
    {
        "status": status,
        "wages": wages,
        "qualified_dividends": dividends,
        "long_term_gains": long_term,
        "short_term_gains": short_term,
    }
    for status in STATUSES
    for wages in (0, 60_000, 150_000, 260_000, 700_000)
    for dividends, long_term, short_term in (
        (0, 0, 0),
        (3_000, 0, 0),
        (0, 50_000, 0),
        (10_000, 40_000, -15_000),
        (0, 30_000, 20_000),
        (25_000, 900_000, 0),
        (0, 1_500_000, 0),
        (0, -8_000, 5_000),
    )
]


def test_grid_matches_form_6251_2025():
    law = calculate(GRID, 2025)
    assert_matches_form_6251(GRID, law)
    assert_properties(GRID, law)
    # The grid reaches separate filers whose line 17 is above the separate
    # breakpoint and below the full one, where Part III sets the AMT.
    reached = False
    for i, h in enumerate(GRID):
        line_12 = float(law["amt_income_less_exemptions"][i])
        line_13 = capital_gains_worksheet_line_4(h)
        line_17 = line_12 - min(line_12, line_13)
        reached |= (
            h["status"] == "SEPARATE"
            and 119_550 < line_17 < 239_100
            and law["amt_tax_including_cg"][i] < law["amt_base_tax"][i]
            and law["alternative_minimum_tax"][i] > 0
        )
    assert reached


def test_separate_filer_with_line_17_of_136_162_50():
    # 2025, married filing separately: $104,000 of wages, $25,000 of
    # qualified dividends and $900,000 of long-term gain. Form 6251 line 4
    # is $1,029,000 plus 25% of the excess over $900,350 ($32,162.50), so
    # line 12 is $1,061,162.50 (no exemption is left) and line 17 is
    # $136,162.50. That is above $119,550, so line 18 is 28% of it less
    # $2,391, $35,734.50; 26% of it would be $35,402.25, $332.25 less.
    household = {
        "status": "SEPARATE",
        "wages": 104_000,
        "qualified_dividends": 25_000,
        "long_term_gains": 900_000,
        "short_term_gains": 0,
    }
    law = calculate([household], 2025)
    line_12 = float(law["amt_income_less_exemptions"][0])
    assert line_12 == 1_061_162.5
    line_17, line_38, line_39, _ = form_6251_part_iii_2025(
        line_12, 925_000, float(law["taxable_income"][0]) - 925_000, "SEPARATE"
    )
    assert line_17 == 136_162.5
    assert amt_rates_2025(line_17, "SEPARATE") == pytest.approx(35_734.5)
    assert line_38 < line_39
    assert_matches_form_6251([household], law)
    assert law["alternative_minimum_tax"][0] > 0


# ---------------------------------------------------------------------------
# Households with 28 percent rate or unrecaptured section 1250 gain.
# ---------------------------------------------------------------------------


def test_unrecaptured_gain_household_by_hand():
    # 2025, single: $200,000 of wages and $400,000 of long-term gain, of
    # which $100,000 is unrecaptured section 1250 gain. Taxable income is
    # $584,250 (the standard deduction is $15,750).
    # Schedule D Tax Worksheet: line 10 $400,000; line 13 $300,000; line 14
    # $284,250; line 18 $184,250; line 19 $197,300; line 20 $197,300; line
    # 21 $197,300; line 22 $0; line 30 $300,000 (15%: $45,000); line 33 $0;
    # line 38 $400,000 + $197,300 - $584,250 = $13,050, so line 39 is
    # $86,950 (25%: $21,737.50); line 44, the tax on $197,300, is $40,199.
    # Line 45: $106,936.50. Taxing line 18 ($184,250) at the regular rates
    # and all $100,000 at 25 percent instead gives $107,067.
    # Form 6251: line 12 $511,900 ($600,000 less the $88,100 exemption);
    # lines 13 to 17: $300,000, $100,000, $400,000, $400,000, $111,900;
    # line 18 $29,094; line 20 $284,250; line 21 $0; line 22 $300,000; line
    # 27 $197,300 (worksheet line 21); line 29 $336,100; line 30 $300,000
    # (15%: $45,000); line 33 $0; line 36 $100,000 (25%: $25,000). Line 38:
    # $99,094. Worksheet line 14 on line 27 would leave $249,150 at 15
    # percent and $50,850 at 20 percent: $101,636.50.
    household = {
        "status": "SINGLE",
        "wages": 200_000,
        "qualified_dividends": 0,
        "long_term_gains": 400_000,
        "short_term_gains": 0,
        "section_1250_share": 25,
    }
    law = calculate([household], 2025)
    assert law["taxable_income"][0] == 584_250
    assert law["dwks14"][0] == 284_250
    assert law["dwks19"][0] == 197_300
    regular_tax = law["income_tax_main_rates"][0] + law["capital_gains_tax"][0]
    assert regular_tax == pytest.approx(106_936.50, abs=0.01)
    assert law["amt_income_less_exemptions"][0] == 511_900
    assert law["amt_tax_including_cg"][0] == pytest.approx(99_094, abs=0.01)
    assert law["alternative_minimum_tax"][0] == 0
    assert_matches_schedule_d_tax_worksheet([household], law)


def test_rate_gain_household_by_hand():
    # 2025, single: $200,000 of wages and $400,000 of long-term gain, of
    # which $100,000 is collectibles gain (28 percent rate gain). Worksheet
    # lines 10 to 22 are as in the previous test. Schedule D line 19 is zero,
    # so lines 35 to 40 are skipped. Line 41: $197,300 + $0 + $300,000 + $0
    # + $0 = $497,300. Line 42: $86,950 (28%: $24,346). Line 45: $45,000 +
    # $24,346 + $40,199 = $109,545. Taxing the whole $100,000 at 28 percent
    # on top would tax $13,050 of it twice.
    household = {
        "status": "SINGLE",
        "wages": 200_000,
        "qualified_dividends": 0,
        "long_term_gains": 400_000,
        "short_term_gains": 0,
        "collectibles_share": 25,
    }
    law = calculate([household], 2025)
    assert law["dwks19"][0] == 197_300
    regular_tax = law["income_tax_main_rates"][0] + law["capital_gains_tax"][0]
    assert regular_tax == pytest.approx(109_545, abs=0.01)
    assert_matches_schedule_d_tax_worksheet([household], law)


SCHEDULE_D_GRID = [
    {
        "status": status,
        "wages": wages,
        "qualified_dividends": dividends,
        "long_term_gains": long_term,
        "short_term_gains": short_term,
        "section_1250_share": section_1250,
        "collectibles_share": collectibles,
        "real_estate_taxes": real_estate_taxes,
    }
    for status in STATUSES
    for wages in (0, 60_000, 150_000, 260_000, 700_000)
    for real_estate_taxes in (0, 40_000)
    for (
        dividends,
        long_term,
        short_term,
        section_1250,
        collectibles,
    ) in (
        (0, 400_000, 0, 25, 0),
        (0, 400_000, 0, 0, 25),
        (10_000, 300_000, 20_000, 30, 20),
        (0, 100_000, 0, 50, 60),
        (25_000, 900_000, 0, 10, 10),
        (0, 50_000, 5_000, 100, 0),
        (3_000, 0, 0, 0, 0),
        (0, 0, 0, 0, 0),
    )
]


def test_schedule_d_grid_matches_2025():
    law = calculate(SCHEDULE_D_GRID, 2025)
    assert_matches_schedule_d_tax_worksheet(SCHEDULE_D_GRID, law)
    assert_properties(SCHEDULE_D_GRID, law)
    assert_schedule_d_properties(SCHEDULE_D_GRID, law)
    # The grid reaches worksheet line 21 below line 14 (line 19 binding),
    # and the alternative minimum tax for such a household.
    below = law["dwks19"] < law["dwks14"]
    assert below.any()
    assert (below & (law["alternative_minimum_tax"] > 0)).any()


household_strategy = st.fixed_dictionaries(
    {
        "status": st.sampled_from(STATUSES),
        "wages": st.integers(0, 1_500_000),
        "qualified_dividends": st.one_of(st.just(0), st.integers(1, 400_000)),
        "long_term_gains": st.one_of(st.just(0), st.integers(-50_000, 2_000_000)),
        "short_term_gains": st.one_of(st.just(0), st.integers(-100_000, 300_000)),
        "real_estate_taxes": st.one_of(st.just(0), st.integers(1, 60_000)),
    }
)

# Adds 28-percent rate gain (collectibles) and unrecaptured section 1250
# gain, as shares of the long-term gain.
household_with_schedule_d_strategy = st.builds(
    lambda h, collectibles, section_1250: {
        **h,
        "collectibles_share": collectibles,
        "section_1250_share": section_1250,
    },
    household_strategy,
    st.one_of(st.just(0), st.integers(1, 100)),
    st.one_of(st.just(0), st.integers(1, 100)),
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
@hypothesis.given(st.lists(household_strategy, min_size=1, max_size=25))
def test_random_households_match_form_6251_2025(households):
    assert_matches_form_6251(households, calculate(households, 2025))


@hypothesis.settings(**SETTINGS)
@hypothesis.given(
    st.lists(household_with_schedule_d_strategy, min_size=1, max_size=25),
    st.sampled_from([2018, 2022, 2025, 2026, 2030]),
)
# The case Hypothesis shrank to against the full-breakpoint line 18: a 2018
# separate filer with no gains whose line 12 ($95,555) is $5 above the
# separate breakpoint ($95,550), so line 18 fell $0.10 short of line 39.
@hypothesis.example(
    households=[
        {
            "status": "SEPARATE",
            "wages": 150_255,
            "qualified_dividends": 0,
            "long_term_gains": 0,
            "short_term_gains": 0,
            "real_estate_taxes": 0,
            "collectibles_share": 0,
            "section_1250_share": 0,
        }
    ],
    year=2018,
)
def test_random_households_keep_the_properties(households, year):
    # Each household with its dividends and gains removed as well, so that
    # line 17 is line 12 for some filers of every status.
    no_gains = [
        {
            **h,
            "qualified_dividends": 0,
            "long_term_gains": 0,
            "short_term_gains": 0,
        }
        for h in households
    ]
    households = households + no_gains
    law = calculate(households, year)
    assert_properties(households, law)
    assert_schedule_d_properties(households, law)


# Households with 28 percent rate or unrecaptured section 1250 gain and no
# short-term loss (see assert_matches_schedule_d_tax_worksheet).
schedule_d_worksheet_household_strategy = st.builds(
    lambda h, short_term, collectibles, section_1250: {
        **h,
        "short_term_gains": short_term,
        "collectibles_share": collectibles,
        "section_1250_share": section_1250,
    },
    household_strategy,
    st.one_of(st.just(0), st.integers(1, 300_000)),
    st.one_of(st.just(0), st.integers(1, 100)),
    st.one_of(st.just(0), st.integers(1, 100)),
)


@hypothesis.settings(**SETTINGS)
@hypothesis.given(
    st.lists(schedule_d_worksheet_household_strategy, min_size=1, max_size=25)
)
def test_random_households_match_schedule_d_tax_worksheet_2025(households):
    law = calculate(households, 2025)
    assert_matches_schedule_d_tax_worksheet(households, law)
    assert_schedule_d_properties(households, law)

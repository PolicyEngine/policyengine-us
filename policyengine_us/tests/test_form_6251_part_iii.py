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
the Schedule D Tax Worksheet, which is not transcribed here; they are
checked only against the properties. YAML unit tests cover those lines.
"""

import numpy as np
import pytest

from policyengine_us import CountryTaxBenefitSystem, Simulation

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


def form_6251_part_iii_2025(line_12, line_13, line_20, status):
    """2025 Form 6251, lines 12 to 40, with no Schedule D Tax Worksheet.

    With no Schedule D Tax Worksheet, line 14 is zero, line 15 is line 13
    and line 27 is line 20 (line 5 of the capital gains worksheet).
    Returns lines 17, 38, 39 and 40.
    """
    line_15 = line_13
    line_16 = min(line_12, line_15)
    line_17 = line_12 - line_16
    line_18 = amt_rates_2025(line_17, status)
    line_21 = max(0, ZERO_RATE_AMOUNT_2025[status] - line_20)
    line_22 = min(line_12, line_13)
    line_23 = min(line_21, line_22)
    line_24 = line_22 - line_23
    line_28 = line_21 + line_20
    line_29 = max(0, FIFTEEN_PERCENT_RATE_AMOUNT_2025[status] - line_28)
    line_30 = min(line_24, line_29)
    line_31 = 0.15 * line_30
    line_32 = line_23 + line_30
    line_33 = line_22 - line_32
    line_34 = 0.20 * line_33
    line_38 = line_18 + line_31 + line_34
    line_39 = amt_rates_2025(line_12, status)
    return line_17, line_38, line_39, min(line_38, line_39)


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


# ---------------------------------------------------------------------------
# Line 18 as a schedule.
# ---------------------------------------------------------------------------

SYSTEM = CountryTaxBenefitSystem()
FILING_STATUS = SYSTEM.variables["filing_status"].possible_values


@hypothesis.settings(max_examples=200, deadline=None)
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
    p = SYSTEM.parameters(f"{year}-01-01").gov.irs.income.amt
    line_17 = np.repeat(np.array(amounts, dtype=float), len(STATUSES))
    statuses = np.tile(np.array(STATUSES), len(amounts))
    filing_status = FILING_STATUS.encode(statuses)
    line_18 = p.brackets.calc(line_17, factor=p.multiplier[filing_status])
    separate = statuses == "SEPARATE"
    # Everyone else: bit for bit the scale with no factor.
    assert np.array_equal(line_18[~separate], p.brackets.calc(line_17[~separate]))
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
    full = p.brackets.calc(line_17[separate])
    assert line_18[separate] - full == pytest.approx(
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

SETTINGS = dict(
    max_examples=10,
    deadline=None,
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
    assert_properties(households, calculate(households, year))

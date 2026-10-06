"""The Form 4952 line 4g election and the regular tax under 26 U.S.C. 1(h).

A Form 4952 line 4g election reduces net capital gain (section 1(h)(2)), so
the elected gain loses the capital gains rates. Section 1(h)(1) then taxes
the rest: subparagraph (A) at the regular rates the greater of taxable income
less net capital gain or the lesser of the taxable income taxed below 25
percent and taxable income less adjusted net capital gain; (B) to (D)
adjusted net capital gain at 0, 15 and 20 percent; (E) unrecaptured section
1250 gain at 25 percent; and (F) "the amount of taxable income in excess of
the sum of the amounts on which tax is determined under the preceding
subparagraphs" at 28 percent. The 2025 Schedule D Tax Worksheet follows the
same steps: line 12 limits Schedule D lines 18 and 19 to line 9 (the gain,
other than qualified dividends, after the election), lines 41 to 43 tax the
rest of line 1 at 28 percent, and line 47 is "the smaller of line 45 or line
46". test_regular_tax_before_credits.py checks the regular tax against the
worksheet for 2025 and 2026 and its bounds across years; this file checks
what the election does, and the bounds with elections and both gains for
2018 to 2030.

Properties, for every generated household and year (2018, 2022, 2025, 2026
and 2030), with elections and both gains:

1. The regular tax is never more than the tax on all taxable income at the
   regular rates (line 46), figured here from the rate schedule parameters
   rather than taken from the model.
2. With no taxable income the regular tax and the capital gains tax are
   exactly zero.
3. Neither is negative.
4. Electing more never lowers the regular tax, or
   income_tax_before_credits, by more than two amounts that the law itself
   produces:

   - `rate_overlap` (test_form_4952_section_911_interaction.py): where the 0
     percent amount ends below the top of the 12 percent bracket, gain is
     taxed at 15 percent and ordinary income at 12 percent ($3.75 single in
     2025);
   - 3 percent (28 less 25) of the smaller of the extra amount elected and
     the unrecaptured section 1250 gain. Subparagraph (E) taxes at 25 percent
     the unrecaptured gain less "the excess (if any) of (I) the sum of the
     amount on which tax is determined under subparagraph (A) plus the net
     capital gain, over (II) taxable income" (worksheet lines 35 to 39). When
     the top of the 24 percent bracket sets the (A) amount, that excess
     shrinks with net capital gain, so an election moves gain from the 28 to
     the 25 percent rate (test_election_can_move_gain_from_28_to_25_percent).

   Without unrecaptured section 1250 gain the first bound alone holds.

Differential, for 2025: with the election on Schedule D Tax Worksheet lines 3
and 4 (transcribed in test_form_6251_part_iii.py) and nonzero Schedule D lines
18 and 19, Form 6251 Part III (lines 13 to 15 and 27 from the worksheet after
the election) and line 11 match the model, and so does line 47. The
transcription takes Schedule D lines 18 and 19 as entered, without the
short-term loss netting of the 28% Rate Gain and Unrecaptured Section 1250
Gain Worksheets (1(h)(4)(B), 1(h)(6)), so the households it compares have no
short-term loss.

Households are 45, live in Texas and take the standard deduction, so the
election never changes taxable income.
"""

import numpy as np
import pytest

from policyengine_us import Simulation
from policyengine_us.tests.test_form_4952_section_911_interaction import (
    rate_overlap,
)
from policyengine_us.tests.test_form_6251_part_iii import (
    STATUSES,
    form_6251_part_iii_2025,
    schedule_d_tax_worksheet_lines_2025,
    tolerance,
)

# Hypothesis is a dev extra; skip rather than fail collection without it.
hypothesis = pytest.importorskip("hypothesis")
st = pytest.importorskip("hypothesis.strategies")

YEARS = [2018, 2022, 2025, 2026, 2030]

OUTPUTS = [
    "filing_status",
    "taxable_income",
    "has_qdiv_or_ltcg",
    "net_capital_gain",
    "dwks10",
    "dwks13",
    "dwks19",
    "income_tax_main_rates",
    "tax_on_taxable_income_at_main_rates",
    "capital_gains_tax",
    "amt_income_less_exemptions",
    "amt_tax_including_cg",
    "amt_base_tax",
    "alternative_minimum_tax",
    "income_tax_before_credits",
]


def household(**amounts):
    h = {
        "status": "SINGLE",
        "wages": 0,
        "dividends": 0,
        "long_term": 0,
        "short_term": 0,
        "collectibles": 0,
        "section_1250": 0,
        "election": 0,
        "more_elected": 1_000,
    }
    h.update(amounts)
    return h


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
            "long_term_capital_gains_on_collectibles": {year: h["collectibles"]},
            "investment_income_elected_form_4952": {year: h["election"]},
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
    results["regular_tax"] = results["income_tax_main_rates"].astype(float) + results[
        "capital_gains_tax"
    ].astype(float)
    parameters = simulation.tax_benefit_system.parameters(f"{year}-01-01")
    results["parameters"] = parameters
    return results


def tax_at_regular_rates(amount, parameters, status):
    """The tax on an amount at the rate schedule in the parameters."""
    bracket = parameters.gov.irs.income.bracket
    tax, bottom = 0.0, 0.0
    for i in range(1, len(list(bracket.rates.__iter__())) + 1):
        top = max(bottom, float(bracket.thresholds[str(i)][status]))
        if amount > bottom:
            tax += float(bracket.rates[str(i)]) * (min(amount, top) - bottom)
        bottom = top
    return tax


def column(households, key):
    return np.array([h[key] for h in households], dtype=float)


# ---------------------------------------------------------------------------
# The properties.
# ---------------------------------------------------------------------------


def assert_properties(households, law):
    """Properties 1 to 3."""
    parameters = law["parameters"]
    taxable_income = law["taxable_income"].astype(float)
    regular_tax = law["regular_tax"]
    slack = tolerance(taxable_income)
    for i, h in enumerate(households):
        status = str(law["filing_status"][i])
        assert status == h["status"], (i, status)
        # 1. Never more than the tax on all taxable income (line 46), from
        # the parameters, and the model's own line 46 is that tax.
        line_46 = tax_at_regular_rates(taxable_income[i], parameters, status)
        assert regular_tax[i] <= line_46 + slack[i], (i, h, regular_tax[i], line_46)
        assert float(law["tax_on_taxable_income_at_main_rates"][i]) == pytest.approx(
            line_46, abs=slack[i]
        ), (i, h)
    # 2. No taxable income, no regular tax.
    none = taxable_income <= 0
    assert not regular_tax[none].any()
    assert not law["capital_gains_tax"][none].any()
    # 3. Not negative.
    assert (law["capital_gains_tax"] >= 0).all()
    assert (regular_tax >= 0).all()


def election_dip_bound(households, law):
    """The largest fall in the regular tax that electing `more_elected` more
    can cause (property 4)."""
    parameters = law["parameters"]
    gains = parameters.gov.irs.capital_gains
    rate_difference = float(gains.other_cg_rate) - float(gains.unrecaptured_s_1250_rate)
    overlaps = {
        str(status): rate_overlap(parameters, str(status))
        for status in set(law["filing_status"])
    }
    return np.array(
        [
            overlaps[str(status)]
            + rate_difference * min(h["more_elected"], h["section_1250"])
            for status, h in zip(law["filing_status"], households)
        ]
    )


def assert_election_bound(households, year):
    """Property 4, with each household and the same one electing more in one
    batch."""
    count = len(households)
    more = [{**h, "election": h["election"] + h["more_elected"]} for h in households]
    results = calculate(households + more, year)
    law = {
        v: values[:count] if isinstance(values, np.ndarray) else values
        for v, values in results.items()
    }
    higher = {
        v: values[count:] if isinstance(values, np.ndarray) else values
        for v, values in results.items()
    }
    assert_properties(households + more, results)
    # The election never changes taxable income here (standard deduction).
    assert np.array_equal(law["taxable_income"], higher["taxable_income"])
    slack = tolerance(law["taxable_income"].astype(float))
    bound = election_dip_bound(households, law)
    for v in ["regular_tax", "income_tax_before_credits"]:
        dip = law[v].astype(float) - higher[v].astype(float)
        bad = np.flatnonzero(dip > bound + slack)
        assert not bad.size, (v, [households[i] for i in bad[:3]], dip[bad[:3]])
    return law, higher


# ---------------------------------------------------------------------------
# The 2025 forms.
# ---------------------------------------------------------------------------


def worksheet_for(h, line_1, status):
    """The 2025 Schedule D Tax Worksheet for a household. Form 4952 line 4e
    is the smaller of line 4d (the net gain) and the net capital gain from
    property held for investment, as the model reads it."""
    long_term, short_term = h["long_term"], h["short_term"]
    net_gain = max(0, long_term + short_term)
    investment_gain = max(0, long_term - max(0, -short_term))
    return schedule_d_tax_worksheet_lines_2025(
        line_1,
        qualified_dividends=h["dividends"],
        form_4952_line_4g=h["election"],
        form_4952_line_4e=min(net_gain, investment_gain),
        schedule_d_line_15=long_term,
        schedule_d_line_16=long_term + short_term,
        schedule_d_line_18=h["collectibles"],
        schedule_d_line_19=h["section_1250"],
        status=status,
    )


def assert_matches_2025_forms(households, law):
    for i, h in enumerate(households):
        assert h["short_term"] >= 0, h
        status = str(law["filing_status"][i])
        line_1 = float(law["taxable_income"][i])
        regular_tax = float(law["regular_tax"][i])
        if line_1 <= 0:
            assert regular_tax == 0, (i, h)
            continue
        worksheet = worksheet_for(h, line_1, status)
        slack = tolerance(line_1)
        # The model fills its worksheet lines only for a filer with
        # dividends or gains (dwks19 is zero otherwise); the tax is compared
        # for everyone.
        if law["has_qdiv_or_ltcg"][i]:
            for model_line, worksheet_line in (
                ("dwks10", 10),
                ("dwks13", 13),
                ("dwks19", 21),
            ):
                assert float(law[model_line][i]) == pytest.approx(
                    worksheet[worksheet_line], abs=slack
                ), (i, h, model_line, worksheet)
        assert regular_tax == pytest.approx(worksheet[47], abs=slack), (
            i,
            h,
            worksheet,
        )
        # Form 6251 Part III with lines 13 to 15 and 27 from the worksheet
        # (after the election), then lines 9 to 11 with no foreign tax
        # credit.
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
        amt_slack = tolerance(line_12, line_1)
        assert float(law["amt_tax_including_cg"][i]) == pytest.approx(
            line_38, abs=amt_slack
        ), (i, h)
        assert float(law["amt_base_tax"][i]) == pytest.approx(line_39, abs=amt_slack), (
            i,
            h,
        )
        assert float(law["alternative_minimum_tax"][i]) == pytest.approx(
            max(0, line_40 - worksheet[47]), abs=amt_slack
        ), (i, h)


# ---------------------------------------------------------------------------
# Tests.
# ---------------------------------------------------------------------------

# Wages, dividends, long-term gain, short-term gain, collectibles gain and
# unrecaptured section 1250 gain.
GRID_INCOMES = [
    (0, 0, 10_000, 0, 10_000, 0),
    (100_000, 0, 100_000, 0, 100_000, 0),
    (300_000, 0, 100_000, 0, 100_000, 0),
    (115_750, 0, 200_000, 0, 100_000, 100_000),
    (60_000, 5_000, 80_000, 10_000, 20_000, 30_000),
    (20_000, 25_000, 900_000, 0, 90_000, 90_000),
    (700_000, 10_000, 400_000, 0, 0, 150_000),
    # Ordinary income at the 0 percent amount and gain in the 12 percent
    # bracket, single, 2025.
    (64_100, 0, 125, 0, 0, 0),
    (64_100, 0, 10_000, 0, 0, 0),
]


def grid():
    rows = []
    for status in STATUSES:
        for (
            wages,
            dividends,
            long_term,
            short_term,
            collectibles,
            s1250,
        ) in GRID_INCOMES:
            gain = long_term + short_term
            for election in sorted(
                {0, gain // 2, gain, gain + dividends // 2, gain + dividends + 9_000}
            ):
                rows.append(
                    household(
                        status=status,
                        wages=wages,
                        dividends=dividends,
                        long_term=long_term,
                        short_term=short_term,
                        collectibles=collectibles,
                        section_1250=s1250,
                        election=election,
                        more_elected=50_000,
                    )
                )
    return rows


GRID = grid()


def test_grid_matches_the_2025_forms():
    law = calculate(GRID, 2025)
    assert_properties(GRID, law)
    assert_matches_2025_forms(GRID, law)
    # The grid reaches the 28 percent rate on what is left of line 9 after
    # an election, the line 47 limit, and the AMT with an election.
    elects = column(GRID, "election") > 0
    rate_gain = column(GRID, "collectibles") > 0
    line_46 = law["tax_on_taxable_income_at_main_rates"]
    assert (elects & rate_gain & (law["capital_gains_tax"] > 0)).any()
    assert (np.abs(law["regular_tax"] - line_46) < 0.01)[
        law["capital_gains_tax"] > 0
    ].any()
    assert (elects & (law["alternative_minimum_tax"] > 0)).any()


@pytest.mark.parametrize("year", YEARS)
def test_grid_keeps_the_properties(year):
    law, higher = assert_election_bound(GRID, year)
    # Electing more raises the tax of some households.
    assert (higher["regular_tax"] > law["regular_tax"] + 1).any()


def test_election_can_move_gain_from_28_to_25_percent():
    """An intended exception to "electing more never lowers the tax".

    2025, single: $115,750 of wages and $200,000 of long-term gain, $100,000
    of it collectibles gain and $100,000 unrecaptured section 1250 gain.
    Taxable income is $300,000. Schedule D Tax Worksheet with no election:
    lines 9 to 12 are $200,000, line 13 is $0, line 18 $100,000, line 20
    $197,300 and line 21 $197,300. Line 35 is $100,000; line 38 is $200,000
    + $197,300 - $300,000 = $97,300, the part of the 1250 gain the regular
    rates tax; line 39 is $2,700 (25%: $675) and line 42 $100,000 (28%:
    $28,000). Electing $50,000 lowers line 10 to $150,000 and line 38 to
    $47,300, so line 39 is $52,700 ($13,175) and line 42 $50,000 ($14,000):
    the tax falls by $1,500, 3% of $50,000. Section 1(h)(1)(E)(ii) measures
    the same excess with net capital gain, which the election reduces
    (section 1(h)(2)).
    """
    households = [
        household(
            wages=115_750,
            long_term=200_000,
            collectibles=100_000,
            section_1250=100_000,
            election=election,
        )
        for election in (0, 50_000)
    ]
    law = calculate(households, 2025)
    assert list(law["taxable_income"]) == [300_000, 300_000]
    assert list(law["regular_tax"]) == pytest.approx([68_874, 67_374], abs=0.01)
    worksheets = [worksheet_for(h, 300_000, "SINGLE") for h in households]
    assert [w[39] for w in worksheets] == [2_700, 52_700]
    assert [w[42] for w in worksheets] == [100_000, 50_000]
    assert [w[47] for w in worksheets] == pytest.approx([68_874, 67_374])
    assert law["alternative_minimum_tax"].tolist() == [0, 0]
    assert_matches_2025_forms(households, law)
    # Within the bound of property 4: 3% of the $50,000 elected.
    bound = election_dip_bound([{**households[0], "more_elected": 50_000}], law)
    assert bound[0] == pytest.approx(3.75 + 1_500)
    dip = law["regular_tax"][0] - law["regular_tax"][1]
    assert dip <= bound[0] + tolerance(300_000)


@st.composite
def households(draw, short_term_loss=True):
    h = household(
        status=draw(st.sampled_from(STATUSES)),
        wages=draw(st.one_of(st.just(0), st.integers(1, 1_000_000))),
        dividends=draw(st.one_of(st.just(0), st.integers(1, 300_000))),
        long_term=draw(st.one_of(st.just(0), st.integers(1, 1_500_000))),
        short_term=draw(
            st.one_of(
                st.just(0),
                st.integers(-100_000 if short_term_loss else 1, 200_000),
            )
        ),
        more_elected=draw(st.one_of(st.integers(1, 500), st.integers(1, 400_000))),
    )
    # 28-percent rate gain and unrecaptured section 1250 gain, as parts of
    # the long-term gain; together they may exceed it, as Schedule D lines 18
    # and 19 can exceed line 9.
    h["collectibles"] = draw(st.one_of(st.just(0), st.integers(0, h["long_term"])))
    h["section_1250"] = draw(st.one_of(st.just(0), st.integers(0, h["long_term"])))
    gain = max(0, h["long_term"] + min(0, h["short_term"]))
    # Elections at the gain and at the gain plus dividends are where the
    # election starts and stops reducing qualified dividends.
    h["election"] = draw(
        st.one_of(
            st.just(0),
            st.integers(1, 2_000_000),
            st.sampled_from([gain, gain + h["dividends"]]),
            st.integers(max(0, gain - 5), gain + h["dividends"] + 5),
        )
    )
    return h


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
    st.lists(households(), min_size=1, max_size=25), st.sampled_from(YEARS)
)
def test_random_households_keep_the_properties(batch, year):
    assert_election_bound(batch, year)


@hypothesis.settings(**SETTINGS)
@hypothesis.given(st.lists(households(short_term_loss=False), min_size=1, max_size=25))
# Found by this test: an election with no gains or dividends. The model's
# worksheet lines are zero without dividends or gains; the tax still matches.
@hypothesis.example([household(wages=122_146, election=50_223)])
def test_random_households_match_the_2025_forms(batch):
    law = calculate(batch, 2025)
    assert_properties(batch, law)
    assert_matches_2025_forms(batch, law)

"""Property and differential tests for the netting of 28 percent rate gain and
unrecaptured section 1250 gain.

26 U.S.C. 1(h)(4): the 28-percent rate gain is the excess, if any, of
collectibles gain and section 1202 gain over collectibles loss, the net
short-term capital loss and the long-term capital loss carried to the year.
1(h)(6)(A): unrecaptured section 1250 gain is the gain before losses less the
excess, if any, of those losses over those gains. The 2025 Instructions for
Schedule D carry these out on the 28% Rate Gain Worksheet (page 11, line 7 is
Schedule D line 18) and the Unrecaptured Section 1250 Gain Worksheet (page 13,
line 18 is Schedule D line 19). A Form 2555 filer with a capital gain excess
then reduces Schedule D line 18 by the excess and enters the excess as a loss
on line 16 of the second worksheet (2025 Form 1040 instructions, Foreign
Earned Income Tax Worksheet, footnote, modifications 3 and 4).

The model takes either family of inputs:

- before netting: `collectibles_gain_or_loss`, `section_1202_gain`,
  `unrecaptured_section_1250_gain_before_losses` and
  `long_term_capital_loss_carryover`, which it nets as the worksheets do;
- as reported on Schedule D lines 18 and 19, already netted:
  `long_term_capital_gains_on_collectibles`,
  `long_term_capital_gains_on_small_business_stock` and
  `unrecaptured_section_1250_gain`. The microdata carry these from the PUF
  (E24518 and E24515) together with the short-term losses already netted
  against them, so they pass through.

Python rather than YAML because these check every household of random
batches against an independent transcription and against each other; the
worked examples are YAML (capital_gains_28_percent_rate_gain.yaml,
schedule_d_unrecaptured_section_1250_gain.yaml, capital_gains_tax.yaml).

- Differential. Both worksheets are transcribed below line by line. For
  every household entering amounts before netting, single or joint, the
  model's `capital_gains_28_percent_rate_gain` and
  `schedule_d_unrecaptured_section_1250_gain` must equal lines 7 and 18.
  With a capital gain excess, `section_911_28_percent_rate_gain`,
  `section_911_unrecaptured_section_1250_gain` and the lines 13 and 19 of
  `schedule_d_tax_worksheet_after_capital_gain_excess` must equal the
  worksheets completed a second time with modifications 1 to 4, with the
  excess figured here from the taxable base passed in.
- Properties that hold for every household, from the model alone:
  1. Bounds: 0 <= line 18 <= the gains (worksheet lines 1 to 4, if more than
     zero) and 0 <= line 19 <= the gain before losses.
  2. Conservation: line 18 + line 19 = the gains plus the gain before losses
     less the losses, if more than zero. Losses absorb the 28 percent rate
     gain first, then unrecaptured section 1250 gain, and nothing else.
  3. Order: losses reach line 19 only when line 18 is zero.
  4. Amounts reported as Schedule D lines 18 and 19 pass through unchanged
     whatever the losses; amounts before netting without losses do too.
  5. More short-term loss or carryover never raises line 18 or 19; more
     collectibles gain never lowers either; more section 1250 gain never
     lowers line 19 or changes line 18.
  6. Netting is on the return: moving amounts between spouses changes
     nothing.
  7. Identities with the Schedule D Tax Worksheet: adjusted net capital gain
     is net capital gain less lines 18 and 19, if more than zero, and line
     13 is line 10 less the smaller of line 9 and lines 18 plus 19.
  8. A household's results do not depend on the other households in its
     batch or their order.
"""

import numpy as np
import pytest

from policyengine_us import Simulation
from policyengine_us.variables.gov.irs.tax.federal_income.foreign_earned_income_exclusion.schedule_d_tax_worksheet_after_capital_gain_excess import (
    schedule_d_tax_worksheet_after_capital_gain_excess,
)

# Hypothesis is a dev extra; skip rather than fail collection without it.
hypothesis = pytest.importorskip("hypothesis")
st = pytest.importorskip("hypothesis.strategies")

YEAR = 2025
OUTPUTS = [
    "capital_gains_28_percent_rate_gain",
    "schedule_d_unrecaptured_section_1250_gain",
    "section_911_28_percent_rate_gain",
    "section_911_unrecaptured_section_1250_gain",
    "net_capital_gain",
    "adjusted_net_capital_gain",
    "dwks09",
    "dwks10",
    "dwks13",
    "has_qdiv_or_ltcg",
]
# Person amounts and the model inputs they set.
PERSON_INPUTS = {
    "long_term": "long_term_capital_gains",
    "short_term": "short_term_capital_gains",
    "collectibles": "collectibles_gain_or_loss",
    "section_1202": "section_1202_gain",
    "carryover": "long_term_capital_loss_carryover",
    "reported_collectibles": "long_term_capital_gains_on_collectibles",
    "reported_section_1202": "long_term_capital_gains_on_small_business_stock",
}

# ---------------------------------------------------------------------------
# The two 2025 worksheets, transcribed.
# ---------------------------------------------------------------------------


def unit_total(h, amount):
    return sum(p[amount] for p in h["people"])


def rate_gain_worksheet(h, capital_gain_excess=0):
    """28% Rate Gain Worksheet lines 1 to 7, for the amounts before netting.
    Line 7 is Schedule D line 18.

    The model has one input for collectibles gain or (loss), which covers
    lines 1, 3 and 4. A Form 2555 filer then reduces Schedule D line 18, but
    not below zero, by any capital gain excess (modification 3).
    """
    line = {}
    line[1] = unit_total(h, "collectibles")
    # "Enter as a positive number" the section 1202 amounts.
    line[2] = max(0, unit_total(h, "section_1202"))
    line[3] = 0
    line[4] = 0
    # "Enter your long-term capital loss carryovers from Schedule D, line
    # 14": a loss, entered in parentheses.
    line[5] = -max(0, unit_total(h, "carryover"))
    # "If Schedule D, line 7, is a (loss), enter that (loss) here."
    line[6] = min(0, unit_total(h, "short_term"))
    combined = sum(line[i] for i in range(1, 7))
    # "If zero or less, enter -0-."
    line[7] = combined if combined > 0 else 0
    line["schedule_d_18"] = max(0, line[7] - capital_gain_excess)
    return line


def unrecaptured_gain_worksheet(h, rate, capital_gain_excess=0):
    """Unrecaptured Section 1250 Gain Worksheet lines 13 to 18, for the gain
    before losses. Line 18 is Schedule D line 19. A Form 2555 filer includes
    any capital gain excess as a loss on line 16 (modification 4)."""
    line = {}
    line[13] = h["section_1250"]
    # "If you had any section 1202 gain or collectibles gain or (loss),
    # enter the total of lines 1 through 4 of the 28% Rate Gain Worksheet."
    line[14] = rate[1] + rate[2] + rate[3] + rate[4]
    line[15] = rate[6]
    line[16] = rate[5] - capital_gain_excess
    combined = line[14] + line[15] + line[16]
    # "If the result is a (loss), enter it as a positive amount."
    line[17] = -combined if combined < 0 else 0
    # "If zero or less, enter -0-."
    line[18] = max(0, line[13] - line[17])
    return line


def schedule_d_lines_18_and_19(h, capital_gain_excess=0):
    """Schedule D lines 18 and 19, after modifications 3 and 4 for any excess.

    For amounts reported as lines 18 and 19 the worksheets were completed
    before: line 17 was zero when line 18 was positive, and line 19 was line
    13 less line 17. Adding the excess to line 16 then takes line 19 down by
    the part of the excess line 18 does not absorb.
    """
    if h["reported"]:
        line_18 = unit_total(h, "reported_collectibles") + unit_total(
            h, "reported_section_1202"
        )
        line_19 = h["reported_section_1250"]
        return (
            max(0, line_18 - capital_gain_excess),
            max(0, line_19 - max(0, capital_gain_excess - line_18)),
        )
    rate = rate_gain_worksheet(h, capital_gain_excess)
    gain = unrecaptured_gain_worksheet(h, rate, capital_gain_excess)
    return rate["schedule_d_18"], gain[18]


def schedule_d_tax_worksheet(h, capital_gain_excess=0):
    """2025 Schedule D Tax Worksheet lines 9, 10 and 13 for these households
    (no qualified dividends, capital gain distributions or Form 4952
    election), completed a second time with modifications 1 to 4 for any
    capital gain excess."""
    long_term = unit_total(h, "long_term")
    schedule_d_16 = long_term + unit_total(h, "short_term")
    # Lines 7 to 9; line 6 is zero.
    line_9 = max(0, min(long_term, schedule_d_16))
    # Modification 1 (and 2, with line 6 zero).
    line_9 = max(0, line_9 - capital_gain_excess)
    line_10 = line_9
    line_18, line_19 = schedule_d_lines_18_and_19(h, capital_gain_excess)
    line_13 = line_10 - min(line_9, line_18 + line_19)
    # The model enters zero when the worksheet is not used: no qualified
    # dividends and no long-term or net capital gain.
    uses_worksheet = long_term > 0 or schedule_d_16 > 0
    return {9: line_9, 10: line_10, 13: line_13 if uses_worksheet else 0}


# ---------------------------------------------------------------------------
# The model.
# ---------------------------------------------------------------------------


def build_situation(households):
    people, tax_units, marital_units = {}, {}, {}
    groups = {"households": {}, "spm_units": {}, "families": {}}
    for i, h in enumerate(households):
        members = []
        for j, p in enumerate(h["people"]):
            name = f"person_{i}_{j}"
            people[name] = {"age": {YEAR: 45}}
            for amount, variable in PERSON_INPUTS.items():
                people[name][variable] = {YEAR: p[amount]}
            members.append(name)
        marital_units[f"marital_unit_{i}"] = {"members": list(members)}
        tax_units[f"tax_unit_{i}"] = {
            "members": list(members),
            # Set for every tax unit: an input given to only some of them
            # leaves the rest at the default.
            "filing_status": {YEAR: "JOINT" if len(members) == 2 else "SINGLE"},
            "unrecaptured_section_1250_gain_before_losses": {YEAR: h["section_1250"]},
            "unrecaptured_section_1250_gain": {YEAR: h["reported_section_1250"]},
            "section_911_capital_gain_excess": {YEAR: h["excess"]},
            "foreign_earned_income_exclusion": {YEAR: h["excluded"]},
        }
        groups["households"][f"household_{i}"] = {
            "members": list(members),
            "state_code": {YEAR: "TX"},
        }
        groups["spm_units"][f"spm_unit_{i}"] = {"members": list(members)}
        groups["families"][f"family_{i}"] = {"members": list(members)}
    return {
        "people": people,
        "tax_units": tax_units,
        "marital_units": marital_units,
        **groups,
    }


def taxable_base(h):
    """The Form 6251 taxable base passed to the worksheet helper: worksheet
    line 10 less the household's AMT capital gain excess."""
    return schedule_d_tax_worksheet(h)[10] - h["amt_excess"]


def calculate(households):
    simulation = Simulation(situation=build_situation(households))
    results = {v: np.asarray(simulation.calculate(v, YEAR)) for v in OUTPUTS}
    worksheet = schedule_d_tax_worksheet_after_capital_gain_excess(
        simulation.populations["tax_unit"],
        YEAR,
        np.array([taxable_base(h) for h in households], dtype=float),
    )
    results["helper_excess"] = np.asarray(worksheet.capital_gain_excess)
    results["helper_line_13"] = np.asarray(worksheet.line_13)
    results["helper_line_19"] = np.asarray(worksheet.unrecaptured_section_1250_gain)
    return results


def close(a, b):
    return abs(float(a) - float(b)) <= 0.01 + 5e-7 * max(abs(float(a)), abs(float(b)))


# ---------------------------------------------------------------------------
# Checks.
# ---------------------------------------------------------------------------


def assert_matches_worksheets(households, law):
    for i, h in enumerate(households):
        line_18, line_19 = schedule_d_lines_18_and_19(h)
        context = (i, h)
        assert close(law["capital_gains_28_percent_rate_gain"][i], line_18), context
        assert close(law["schedule_d_unrecaptured_section_1250_gain"][i], line_19), (
            context
        )
        # Modifications 3 and 4, with the regular tax excess.
        line_18_911, line_19_911 = schedule_d_lines_18_and_19(h, h["excess"])
        assert close(law["section_911_28_percent_rate_gain"][i], line_18_911), context
        assert close(
            law["section_911_unrecaptured_section_1250_gain"][i], line_19_911
        ), context
        # The worksheet helper as Form 6251 calls it: a filer excluding
        # income has an excess when line 10 is more than the taxable base.
        line_10 = schedule_d_tax_worksheet(h)[10]
        amt_excess = (
            max(0, line_10 - max(0, taxable_base(h))) if h["excluded"] > 0 else 0
        )
        assert close(law["helper_excess"][i], amt_excess), context
        assert close(
            law["helper_line_13"][i], schedule_d_tax_worksheet(h, amt_excess)[13]
        ), context
        assert close(
            law["helper_line_19"][i], schedule_d_lines_18_and_19(h, amt_excess)[1]
        ), context


def assert_properties(households, law):
    line_18 = law["capital_gains_28_percent_rate_gain"].astype(float)
    line_19 = law["schedule_d_unrecaptured_section_1250_gain"].astype(float)
    reported = np.array([h["reported"] for h in households], dtype=bool)
    entered_1250 = np.array(
        [h["reported_section_1250"] + h["section_1250"] for h in households],
        dtype=float,
    )
    gains = np.array(
        [
            unit_total(h, "collectibles") + max(0, unit_total(h, "section_1202"))
            for h in households
        ],
        dtype=float,
    )
    reported_18 = np.array(
        [
            unit_total(h, "reported_collectibles")
            + unit_total(h, "reported_section_1202")
            for h in households
        ],
        dtype=float,
    )
    losses = np.array(
        [
            max(0, -unit_total(h, "short_term")) + max(0, unit_total(h, "carryover"))
            for h in households
        ],
        dtype=float,
    )
    tol = 0.01 + 5e-7 * (np.abs(gains) + reported_18 + entered_1250 + losses)
    netted = ~reported
    # 1. Bounds.
    assert (line_18 >= 0).all()
    assert (line_18[netted] <= np.maximum(0, gains[netted]) + tol[netted]).all()
    assert (line_19 >= 0).all()
    assert (line_19 <= entered_1250 + tol).all()
    # 2. Conservation.
    assert np.allclose(
        (line_18 + line_19)[netted],
        np.maximum(0, gains + entered_1250 - losses)[netted],
        rtol=0,
        atol=tol.max(),
    )
    # 3. Order.
    reduced = netted & (line_19 < entered_1250 - tol)
    assert (line_18[reduced] == 0).all()
    # 4. Pass-through: reported amounts whatever the losses, and amounts
    # before netting without losses.
    unchanged = reported | ((losses == 0) & (gains >= 0))
    assert np.allclose(
        line_18[unchanged],
        np.where(reported, reported_18, gains)[unchanged],
        rtol=0,
        atol=0.01,
    )
    assert np.allclose(line_19[unchanged], entered_1250[unchanged], rtol=0, atol=0.01)
    # 7. Identities with the Schedule D Tax Worksheet.
    net_gain = law["net_capital_gain"].astype(float)
    assert np.allclose(
        law["adjusted_net_capital_gain"].astype(float),
        np.maximum(0, net_gain - (line_18 + line_19)),
        rtol=0,
        atol=0.02 + 5e-7 * net_gain.max(),
    )
    uses_worksheet = law["has_qdiv_or_ltcg"].astype(bool)
    line_9 = law["dwks09"].astype(float)
    line_10 = law["dwks10"].astype(float)
    expected_13 = line_10 - np.minimum(line_9, line_18 + line_19)
    assert np.allclose(
        law["dwks13"].astype(float)[uses_worksheet],
        expected_13[uses_worksheet],
        rtol=0,
        atol=0.02 + 5e-7 * max(1, line_10.max()),
    )


# ---------------------------------------------------------------------------
# Households.
# ---------------------------------------------------------------------------


@st.composite
def person(draw, reported):
    p = {
        "long_term": draw(st.one_of(st.just(0), st.integers(-200_000, 2_000_000))),
        # Schedule D line 7 for this person: a gain or a loss.
        "short_term": draw(st.one_of(st.just(0), st.integers(-1_000_000, 500_000))),
        "carryover": draw(st.one_of(st.just(0), st.just(0), st.integers(1, 800_000))),
        "collectibles": 0,
        "section_1202": 0,
        "reported_collectibles": 0,
        "reported_section_1202": 0,
    }
    if reported:
        # Schedule D line 18 as the microdata carry it: never negative.
        p["reported_collectibles"] = draw(
            st.one_of(st.just(0), st.integers(1, 1_000_000))
        )
        p["reported_section_1202"] = draw(
            st.one_of(st.just(0), st.just(0), st.integers(1, 300_000))
        )
    else:
        # Collectibles gain or (loss): a net collectibles loss is negative.
        p["collectibles"] = draw(
            st.one_of(st.just(0), st.just(0), st.integers(-200_000, 1_000_000))
        )
        p["section_1202"] = draw(
            st.one_of(st.just(0), st.just(0), st.integers(1, 500_000))
        )
    return p


@st.composite
def households(draw):
    reported = draw(st.booleans())
    people = draw(st.lists(person(reported), min_size=1, max_size=2))
    section_1250 = draw(st.one_of(st.just(0), st.integers(1, 1_500_000)))
    return {
        "reported": reported,
        "people": people,
        "section_1250": 0 if reported else section_1250,
        "reported_section_1250": section_1250 if reported else 0,
        # A regular tax capital gain excess, entered as the section 911
        # amount, and an AMT one, for the worksheet helper.
        "excess": draw(st.one_of(st.just(0), st.just(0), st.integers(1, 1_000_000))),
        "amt_excess": draw(st.one_of(st.just(0), st.integers(1, 1_000_000))),
        # The helper refigures only for a filer who excludes income.
        "excluded": draw(st.sampled_from([0, 100_000])),
    }


SETTINGS = dict(
    max_examples=12,
    deadline=None,
    derandomize=True,
    suppress_health_check=[
        hypothesis.HealthCheck.too_slow,
        hypothesis.HealthCheck.data_too_large,
    ],
)

AMOUNTS = tuple(a for a in PERSON_INPUTS if a != "long_term") + ("long_term",)


def with_head(h, amount, more):
    """`more` added to the head's `amount`, in whichever family the
    household enters."""
    if h["reported"] and amount in ("collectibles", "section_1202"):
        amount = "reported_" + amount
    head = {**h["people"][0], amount: h["people"][0][amount] + more}
    return {**h, "people": [head] + h["people"][1:]}


def on_one_person(h):
    """The return's amounts all on the head."""
    head = {**h["people"][0], **{a: unit_total(h, a) for a in AMOUNTS}}
    others = [{**p, **{a: 0 for a in AMOUNTS}} for p in h["people"][1:]]
    return {**h, "people": [head] + others}


def more_section_1250(h, more):
    key = "reported_section_1250" if h["reported"] else "section_1250"
    return {**h, key: h[key] + more}


@hypothesis.settings(**SETTINGS)
@hypothesis.given(st.lists(households(), min_size=1, max_size=20))
def test_random_households_match_worksheets(batch):
    law = calculate(batch)
    assert_matches_worksheets(batch, law)
    assert_properties(batch, law)


@hypothesis.settings(**SETTINGS)
@hypothesis.given(
    st.lists(households(), min_size=1, max_size=12), st.integers(1, 300_000)
)
def test_random_households_keep_the_properties(batch, more):
    count = len(batch)
    variants = (
        batch
        + [with_head(h, "short_term", -more) for h in batch]
        + [with_head(h, "carryover", more) for h in batch]
        + [with_head(h, "collectibles", more) for h in batch]
        + [more_section_1250(h, more) for h in batch]
        + [on_one_person(h) for h in batch]
    )
    law = calculate(variants)
    assert_matches_worksheets(variants, law)
    assert_properties(variants, law)
    line_18 = law["capital_gains_28_percent_rate_gain"].astype(float).reshape(6, count)
    line_19 = (
        law["schedule_d_unrecaptured_section_1250_gain"].astype(float).reshape(6, count)
    )
    tol = 0.01 + 5e-7 * (np.abs(line_18).max() + np.abs(line_19).max())
    # 5. Monotonicity: rows 1 and 2 add losses, row 3 collectibles gain, row
    # 4 section 1250 gain.
    for k in (1, 2):
        assert (line_18[k] <= line_18[0] + tol).all(), k
        assert (line_19[k] <= line_19[0] + tol).all(), k
    assert (line_18[3] >= line_18[0] - tol).all()
    assert (line_19[3] >= line_19[0] - tol).all()
    assert (line_19[4] >= line_19[0] - tol).all()
    assert np.array_equal(line_18[4], line_18[0])
    # 4. Reported amounts ignore the added losses.
    reported = np.array([h["reported"] for h in batch], dtype=bool)
    for k in (1, 2):
        assert np.array_equal(line_18[k][reported], line_18[0][reported]), k
        assert np.array_equal(line_19[k][reported], line_19[0][reported]), k
    # 6. Netting is on the return.
    assert np.array_equal(line_18[5], line_18[0])
    assert np.array_equal(line_19[5], line_19[0])
    # 8. The same households in reverse order give the same results.
    reverse = calculate(batch[::-1])
    for v in OUTPUTS:
        assert np.array_equal(reverse[v][::-1], law[v][:count]), v


def test_worked_examples_match_worksheets():
    """The YAML examples, through both the model and the transcription."""

    def h(section_1250=0, excess=0, reported=False, **head):
        p = {"long_term": 50_000, "short_term": 0, "carryover": 0}
        p.update(
            {
                "collectibles": 0,
                "section_1202": 0,
                "reported_collectibles": 0,
                "reported_section_1202": 0,
            },
            **head,
        )
        return {
            "reported": reported,
            "people": [p],
            "section_1250": 0 if reported else section_1250,
            "reported_section_1250": section_1250 if reported else 0,
            "excess": excess,
            "amt_excess": 0,
            "excluded": 0,
        }

    batch = [
        h(collectibles=10_000, short_term=-8_000),
        h(collectibles=10_000, short_term=-15_000, section_1250=20_000),
        h(section_1202=4_000, collectibles=10_000, short_term=-5_000, carryover=3_000),
        h(collectibles=-4_000, section_1250=20_000),
        h(short_term=-6_000, carryover=1_000, section_1250=20_000),
        # An excess of 9,000 takes line 18 from 2,000 to 0 and the 7,000
        # left reduces line 19 from 20,000 to 13,000.
        h(collectibles=10_000, short_term=-8_000, section_1250=20_000, excess=9_000),
        # The microdata's PUF lines 18 and 19 with the loss already netted.
        h(
            reported=True,
            reported_collectibles=2_000,
            short_term=-8_000,
            section_1250=20_000,
        ),
    ]
    law = calculate(batch)
    assert_matches_worksheets(batch, law)
    assert_properties(batch, law)
    assert law["capital_gains_28_percent_rate_gain"].tolist() == [
        2_000,
        0,
        6_000,
        0,
        0,
        2_000,
        2_000,
    ]
    assert law["schedule_d_unrecaptured_section_1250_gain"].tolist() == [
        0,
        15_000,
        0,
        16_000,
        13_000,
        20_000,
        20_000,
    ]
    assert law["section_911_28_percent_rate_gain"][5] == 0
    assert law["section_911_unrecaptured_section_1250_gain"][5] == 13_000

"""Properties of the New York City income tax elimination credit.

NY Tax Law § 1310(h) allows a city resident a credit equal to the city tax
"otherwise due ... reduced by all the credits permitted by this article" when
the resident is entitled to a dependent deduction under IRC § 151(c), has
federal adjusted gross income (AGI) at or below a threshold that depends on
filing status and the number of dependents, claims no New York State or City
pass-through entity tax (PTET) credit, and has disqualified income under
IRC § 32(i) of at most $10,000. Above the threshold the credit falls in
proportion to the excess and ends $5,000 above it. Form IT-270 computes it on
lines 1 to 11 and Form IT-201 claims it on line 70a; line 6 of IT-270 is
IT-201 line 54 (`nyc_income_tax_before_refundable_credits`), and lines 7 and
8 are the NYC child and dependent care credit and NYC EITC.

The hypothesis tests build one vectorized simulation per example, holding a
batch of generated tax units (every filing status, 0 to 9 dependents, wages
with cents, optional interest, childcare expenses and PTET claim, in or
outside New York City, tax year 2025 or 2026), and check for every tax unit:

1. Bounds: 0 <= credit <= max(line 54 - NYC CDCC - NYC EITC, 0), so the
   credit never exceeds the tax left after the other Article 30 credits.
2. Zeros: the credit is 0 whenever AGI exceeds the threshold by more than
   $5,000, the tax unit has no dependents, investment income exceeds
   $10,000, a PTET credit is claimed, or the tax unit is outside the city.
3. Elimination: when eligible with AGI at or below the threshold and a
   positive line 54 - CDCC - EITC, that amount less the credit is 0, so
   `nyc_income_tax` equals minus the NYC school tax credit. That credit is a
   State credit under Tax Law § 606(ggg), not an Article 30 credit, so it
   still refunds.
4. Differential: the credit equals an independent closed-form
   implementation of IT-270 Part 1 and Part 2 lines 1 to 11 built on the
   model's own AGI, threshold, line 54, CDCC and EITC, and the threshold
   equals the statutory table (§ 1310(h)(1)(B)(i)-(ii)) scaled by one
   factor per year. Line 5 is rounded to the fourth decimal place. IT-201
   and its credit forms take whole-dollar amounts, which makes line 5 an
   exact multiple of 0.0001 before rounding; with the model's unrounded
   AGI, an excess ending in 25 or 75 cents lands exactly halfway between two
   fourth-decimal values, where neither the statute (which does not round)
   nor the form (which never sees cents) picks a side. At those ties the
   credit must equal line 10 times one of the two neighbouring fractions;
   everywhere else it must match the round-half-up reference to the cent.
5. Monotonicity: with line 54, CDCC and EITC held fixed as inputs, the
   credit is non-increasing in AGI (and full at or below the threshold,
   zero beyond the phase-out).

A deterministic test covers the threshold tables for every dependent count
from 1 to 10 in every tax year from 2025 to 2035:

6. The joint and surviving spouse threshold is at least the single,
   separate and head of household threshold; thresholds are non-decreasing
   in the number of dependents; single, separate and head of household
   thresholds are equal, as are joint and surviving spouse thresholds.
7. The 2025 thresholds equal the statutory table, and each later year's
   thresholds equal it times one common factor of at least 1
   (§ 1310(h)(1)(B)(iii): "one plus the cost-of-living adjustment").
"""

from collections import Counter

import numpy as np
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation
from policyengine_us.system import system

# Tax Law § 1310(h)(1)(B)(i): married filing jointly or qualified surviving
# spouse; the last row is "7 or more".
JOINT_TABLE = {
    1: 36_789,
    2: 46_350,
    3: 54_545,
    4: 61_071,
    5: 68_403,
    6: 75_204,
    7: 91_902,
}
# § 1310(h)(1)(B)(ii): single, married filing separately or head of
# household; the last row is "8 or more".
OTHER_TABLE = {
    1: 31_503,
    2: 36_824,
    3: 46_512,
    4: 53_711,
    5: 59_928,
    6: 65_712,
    7: 74_565,
    8: 88_361,
}
JOINT_STATUSES = ("JOINT", "SURVIVING_SPOUSE")
FILING_STATUSES = (
    "SINGLE",
    "JOINT",
    "SEPARATE",
    "HEAD_OF_HOUSEHOLD",
    "SURVIVING_SPOUSE",
)
# § 1310(h)(2) and (h)(1)(D).
PHASE_OUT_WIDTH = 5_000
INVESTMENT_INCOME_LIMIT = 10_000
YEARS = (2025, 2026)
TABLE_YEARS = range(2025, 2036)
BATCH_SIZE = 30
# Comparison tolerance. The model stores amounts as float32, which resolves
# about $0.008 near $130,000.
CENT = 0.01


def statutory_threshold(filing_status, dependents):
    """Form IT-270-I line 2 table; 0 for a tax unit without dependents."""
    if dependents < 1:
        return 0
    table = JOINT_TABLE if filing_status in JOINT_STATUSES else OTHER_TABLE
    return table[min(dependents, max(table))]


def model_thresholds(year):
    return system.parameters(
        f"{year}-01-01"
    ).gov.local.ny.nyc.tax.income.credits.income_tax_elimination.income_threshold


def model_threshold(year, filing_status, dependents):
    """The model's threshold, used only to aim generated AGI at the phase-out."""
    scales = model_thresholds(year)
    name = {
        "SINGLE": "single",
        "JOINT": "joint",
        "SEPARATE": "separate",
        "HEAD_OF_HOUSEHOLD": "head_of_household",
        "SURVIVING_SPOUSE": "surviving_spouse",
    }[filing_status]
    return float(getattr(scales, name).calc(max(dependents, 1)))


def to_cents(dollars):
    return int(round(dollars * 100))


# Cents biased towards 0, 25, 50 and 75, which put the phase-out fraction on
# an exact multiple of 0.0001 or exactly halfway between two of them.
cents = st.one_of(st.sampled_from([0, 25, 50, 75, 99]), st.integers(0, 99))


@st.composite
def dollars_and_cents(draw, low, high):
    return draw(st.integers(low, high)) * 100 + draw(cents)


@st.composite
def target_agi_cents(draw, year, filing_status, dependents):
    """AGI anywhere from $0 to $130,000, or near the threshold and the end of
    the phase-out."""
    threshold = model_threshold(year, filing_status, dependents)
    anywhere = dollars_and_cents(0, 129_999)
    edges = st.sampled_from(
        [0, 1, -1, PHASE_OUT_WIDTH * 100, PHASE_OUT_WIDTH * 100 + 1]
    )
    near = st.one_of(dollars_and_cents(-2_000, 7_000), edges).map(
        lambda offset: to_cents(threshold) + offset
    )
    return min(max(draw(st.one_of(anywhere, near)), 0), 13_000_000)


@st.composite
def nyc_tax_unit(draw, year):
    filing_status = draw(st.sampled_from(FILING_STATUSES))
    # Head of household and surviving spouse filers need a qualifying person.
    fewest = 1 if filing_status in ("HEAD_OF_HOUSEHOLD", "SURVIVING_SPOUSE") else 0
    dependents = draw(st.integers(fewest, 9))
    child_ages = draw(
        st.lists(st.integers(0, 17), min_size=dependents, max_size=dependents)
    )
    interest = draw(
        st.one_of(
            st.just(0),
            dollars_and_cents(0, 14_999),
            # Just under, at and just over the $10,000 limit.
            st.sampled_from([999_999, 1_000_000, 1_000_001]),
        )
    )
    agi = draw(target_agi_cents(year, filing_status, dependents))
    wages = min(max(agi - interest, 0), 13_000_000)
    head_share = draw(st.integers(0, 100)) if filing_status == "JOINT" else 100
    head_wages = wages * head_share // 100
    childcare = draw(st.one_of(st.just(0), dollars_and_cents(0, 12_000)))
    return {
        "filing_status": filing_status,
        "dependents": dependents,
        "child_ages": child_ages,
        "head_wages": head_wages / 100,
        "spouse_wages": (wages - head_wages) / 100,
        "interest": interest / 100,
        "childcare": childcare / 100 if dependents else 0.0,
        "ptet": draw(st.sampled_from([False, False, False, True])),
        "in_nyc": draw(st.sampled_from([True, True, True, True, False])),
    }


@st.composite
def batches(draw):
    year = draw(st.sampled_from(YEARS))
    units = draw(st.lists(nyc_tax_unit(year), min_size=BATCH_SIZE, max_size=BATCH_SIZE))
    return year, units


def build_simulation(year, units, tax_unit_inputs=None):
    """One household, tax unit, SPM unit, family and set of marital units per
    generated tax unit, all in New York State."""
    situation = {
        "people": {},
        "tax_units": {},
        "spm_units": {},
        "families": {},
        "marital_units": {},
        "households": {},
    }
    for i, unit in enumerate(units):
        head = f"head{i}"
        situation["people"][head] = {
            "age": {year: 40},
            "employment_income": {year: unit.get("head_wages", 0.0)},
            "taxable_interest_income": {year: unit.get("interest", 0.0)},
        }
        adults = [head]
        if unit["filing_status"] == "JOINT":
            spouse = f"spouse{i}"
            situation["people"][spouse] = {
                "age": {year: 38},
                "employment_income": {year: unit.get("spouse_wages", 0.0)},
            }
            adults.append(spouse)
        members = list(adults)
        for j, age in enumerate(unit["child_ages"]):
            child = f"child{i}_{j}"
            situation["people"][child] = {"age": {year: age}}
            situation["marital_units"][f"child_marital_unit{i}_{j}"] = {
                "members": [child]
            }
            members.append(child)
        situation["marital_units"][f"marital_unit{i}"] = {"members": adults}
        situation["tax_units"][f"tax_unit{i}"] = {
            "members": members,
            "filing_status": {year: unit["filing_status"]},
            "ny_pass_through_entity_tax_credit_claimed": {
                year: unit.get("ptet", False)
            },
            **{
                name: {year: values[i]}
                for name, values in (tax_unit_inputs or {}).items()
            },
        }
        situation["spm_units"][f"spm_unit{i}"] = {
            "members": members,
            "childcare_expenses": {year: unit.get("childcare", 0.0)},
        }
        situation["families"][f"family{i}"] = {"members": members}
        situation["households"][f"household{i}"] = {
            "members": members,
            "state_code": {year: "NY"},
            "in_nyc": {year: unit.get("in_nyc", True)},
        }
    return Simulation(situation=situation)


def calculate(sim, year, names):
    return {name: sim.calculate(name, year).astype(float) for name in names}


def reference_line_5(agi, threshold):
    """IT-270 lines 3 to 5, and whether line 5 is an exact rounding tie.

    AGI and the threshold are float32 values held exactly in float64, so
    line 4 and twice line 4 (line 5 in units of 0.0001) are exact here and the
    half-up rounding below involves no floating-point error.
    """
    line_3 = np.maximum(agi - threshold, 0)
    line_4 = PHASE_OUT_WIDTH - line_3
    units = 2 * line_4
    tie = (units - np.floor(units)) == 0.5
    return (
        np.floor(units + 0.5) / 10_000,
        np.floor(units) / 10_000,
        np.ceil(units) / 10_000,
        tie,
    )


def check_credit_batch(year, units, seen):
    sim = build_simulation(year, units)
    v = calculate(
        sim,
        year,
        [
            "nyc_income_tax_elimination_credit",
            "nyc_income_tax_elimination_credit_income_threshold",
            "adjusted_gross_income",
            "eitc_relevant_investment_income",
            "nyc_income_tax_before_refundable_credits",
            "nyc_cdcc",
            "nyc_eitc",
            "nyc_school_tax_credit",
            "nyc_income_tax",
            "tax_unit_dependents",
        ],
    )
    eligible_flag = sim.calculate("nyc_income_tax_elimination_credit_eligible", year)
    credit = v["nyc_income_tax_elimination_credit"]
    threshold = v["nyc_income_tax_elimination_credit_income_threshold"]
    agi = v["adjusted_gross_income"]
    investment_income = v["eitc_relevant_investment_income"]
    line_54 = v["nyc_income_tax_before_refundable_credits"]
    cdcc, eitc = v["nyc_cdcc"], v["nyc_eitc"]
    line_10 = line_54 - cdcc - eitc

    filing_status = np.array([u["filing_status"] for u in units])
    dependents = np.array([u["dependents"] for u in units])
    interest = np.array([u["interest"] for u in units])
    wages = np.array([u["head_wages"] + u["spouse_wages"] for u in units])
    ptet = np.array([u["ptet"] for u in units])
    in_nyc = np.array([u["in_nyc"] for u in units])

    # Preconditions: the generated structure reached the model as intended.
    np.testing.assert_array_equal(v["tax_unit_dependents"], dependents)
    np.testing.assert_array_equal(
        sim.calculate("filing_status", year).decode_to_str(), filing_status
    )
    np.testing.assert_array_equal(sim.calculate("in_nyc", year), in_nyc)
    np.testing.assert_allclose(investment_income, interest, atol=CENT)
    np.testing.assert_allclose(agi, wages + interest, atol=2 * CENT)

    has_dependents = dependents >= 1
    within_phase_out = agi - threshold <= PHASE_OUT_WIDTH
    passes_investment = investment_income <= INVESTMENT_INCOME_LIMIT
    eligible = in_nyc & has_dependents & within_phase_out & passes_investment & ~ptet

    # 1. Bounds.
    assert np.all(credit >= 0), credit[credit < 0]
    over = credit > np.maximum(line_10, 0) + CENT
    assert not over.any(), (credit[over], line_10[over])

    # 2. Zeros.
    must_be_zero = (
        ~in_nyc
        | ~has_dependents
        | (agi > threshold + PHASE_OUT_WIDTH)
        | ~passes_investment
        | ptet
    )
    np.testing.assert_array_equal(credit[must_be_zero], 0)

    # 3. Elimination at or below the threshold.
    full = eligible & (agi <= threshold) & (line_10 > 0)
    np.testing.assert_allclose(line_10[full] - credit[full], 0, atol=CENT)
    np.testing.assert_allclose(
        v["nyc_income_tax"][full], -v["nyc_school_tax_credit"][full], atol=CENT
    )

    # 4. Differential against IT-270 lines 1 to 11. The model's eligibility
    # flag agrees with Part 1 except within a cent of the end of the
    # phase-out, where float32 addition can move the boundary and line 5
    # is 0 either way.
    at_boundary = np.abs(agi - (threshold + PHASE_OUT_WIDTH)) < CENT
    np.testing.assert_array_equal(eligible_flag[~at_boundary], eligible[~at_boundary])
    factor = model_threshold(year, "JOINT", 1) / JOINT_TABLE[1]
    if year == 2025:
        assert factor == 1
    statutory = np.array(
        [statutory_threshold(f, d) for f, d in zip(filing_status, dependents)]
    )
    in_city = in_nyc & has_dependents
    np.testing.assert_allclose(
        threshold[in_city], statutory[in_city] * factor, rtol=1e-7
    )
    line_5, line_5_down, line_5_up, tie = reference_line_5(agi, threshold)
    claims = eligible & (line_10 > 0)
    expected = np.where(claims, line_10 * line_5, 0)
    exact = ~(claims & tie)
    np.testing.assert_allclose(credit[exact], expected[exact], atol=CENT)
    tied = claims & tie
    low = line_10[tied] * line_5_down[tied] - CENT
    high = line_10[tied] * line_5_up[tied] + CENT
    assert np.all((credit[tied] >= low) & (credit[tied] <= high)), (
        agi[tied],
        credit[tied],
        low,
        high,
    )

    partial = claims & (agi > threshold)
    seen[f"year {year}"] += 1
    seen["full credit"] += np.sum(full & (credit > 0))
    seen["partial credit"] += np.sum(partial & (credit > 0) & (credit < line_10))
    seen["tie in line 5"] += np.sum(tied & partial)
    seen["over the phase-out"] += np.sum(
        in_nyc & has_dependents & (agi > threshold + PHASE_OUT_WIDTH)
    )
    seen["no dependents but tax"] += np.sum(in_nyc & ~has_dependents & (line_10 > 0))
    seen["investment income over limit"] += np.sum(
        in_nyc & has_dependents & within_phase_out & ~passes_investment & ~ptet
    )
    seen["investment income at limit"] += np.sum(
        eligible & (investment_income == INVESTMENT_INCOME_LIMIT)
    )
    seen["PTET with tax"] += np.sum(
        in_nyc & has_dependents & within_phase_out & ptet & (line_10 > 0)
    )
    seen["outside the city"] += np.sum(~in_nyc)
    seen["eligible with NYC CDCC"] += np.sum(eligible & (cdcc > 0))
    seen["eligible with NYC EITC"] += np.sum(eligible & (eitc > 0))
    seen["other credits exceed line 54"] += np.sum(
        eligible & (line_54 > 0) & (line_10 <= 0)
    )
    seen["school tax credit refunded"] += np.sum(
        full & (v["nyc_school_tax_credit"] > 0)
    )
    for status in FILING_STATUSES:
        seen[f"{status} credit"] += np.sum((filing_status == status) & (credit > 0))


def test_credit_bounds_zeros_elimination_and_it270_reference():
    seen = Counter()

    @settings(
        max_examples=60,
        deadline=None,
        derandomize=True,
        database=None,
        suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large],
    )
    @given(batches())
    def check(batch):
        check_credit_batch(*batch, seen)

    check()
    # Guard against a vacuous pass: every regime the properties speak to
    # occurs in the generated batches.
    missing = [
        name
        for name in [
            "year 2025",
            "year 2026",
            "full credit",
            "partial credit",
            "tie in line 5",
            "over the phase-out",
            "no dependents but tax",
            "investment income over limit",
            "investment income at limit",
            "PTET with tax",
            "outside the city",
            "eligible with NYC CDCC",
            "eligible with NYC EITC",
            "other credits exceed line 54",
            "school tax credit refunded",
            *[f"{status} credit" for status in FILING_STATUSES],
        ]
        if seen[name] == 0
    ]
    assert not missing, (missing, seen)


GROUPS = 4
AGIS_PER_GROUP = 10


@st.composite
def monotonicity_batches(draw):
    """Groups of tax units that differ only in AGI, with line 54, the NYC
    CDCC and the NYC EITC given as inputs."""
    year = draw(st.sampled_from(YEARS))
    units, inputs = (
        [],
        {
            "adjusted_gross_income": [],
            "nyc_income_tax_before_refundable_credits": [],
            "nyc_cdcc": [],
            "nyc_eitc": [],
        },
    )
    for _ in range(GROUPS):
        filing_status = draw(st.sampled_from(FILING_STATUSES))
        dependents = draw(st.integers(1, 9))
        child_ages = [5] * dependents
        line_54 = draw(dollars_and_cents(0, 7_999)) / 100
        cdcc = draw(st.one_of(st.just(0), dollars_and_cents(0, 999))) / 100
        eitc = draw(st.one_of(st.just(0), dollars_and_cents(0, 1_999))) / 100
        agis = sorted(
            draw(
                st.lists(
                    target_agi_cents(year, filing_status, dependents),
                    min_size=AGIS_PER_GROUP,
                    max_size=AGIS_PER_GROUP,
                )
            )
        )
        for agi in agis:
            units.append({"filing_status": filing_status, "child_ages": child_ages})
            inputs["adjusted_gross_income"].append(agi / 100)
            inputs["nyc_income_tax_before_refundable_credits"].append(line_54)
            inputs["nyc_cdcc"].append(cdcc)
            inputs["nyc_eitc"].append(eitc)
    return year, units, inputs


def test_credit_is_non_increasing_in_agi():
    seen = Counter()

    @settings(
        max_examples=40,
        deadline=None,
        derandomize=True,
        database=None,
        suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large],
    )
    @given(monotonicity_batches())
    def check(batch):
        year, units, inputs = batch
        sim = build_simulation(year, units, tax_unit_inputs=inputs)
        v = calculate(
            sim,
            year,
            [
                "nyc_income_tax_elimination_credit",
                "nyc_income_tax_elimination_credit_income_threshold",
                "adjusted_gross_income",
                "nyc_income_tax_before_refundable_credits",
                "nyc_cdcc",
                "nyc_eitc",
            ],
        )
        for name in inputs:
            np.testing.assert_allclose(v[name], inputs[name], atol=CENT)
        credit = v["nyc_income_tax_elimination_credit"].reshape(GROUPS, AGIS_PER_GROUP)
        agi = v["adjusted_gross_income"].reshape(GROUPS, AGIS_PER_GROUP)
        threshold = v["nyc_income_tax_elimination_credit_income_threshold"].reshape(
            GROUPS, AGIS_PER_GROUP
        )
        line_10 = (
            v["nyc_income_tax_before_refundable_credits"]
            - v["nyc_cdcc"]
            - v["nyc_eitc"]
        ).reshape(GROUPS, AGIS_PER_GROUP)
        assert np.all(np.diff(agi, axis=1) >= 0)
        # 5. Non-increasing in AGI, with no tolerance: every step of the
        # formula is monotone and float rounding preserves order.
        steps = np.diff(credit, axis=1)
        assert np.all(steps <= 0), (agi, credit)
        full = agi <= threshold
        np.testing.assert_allclose(
            credit[full], np.maximum(line_10, 0)[full], atol=CENT
        )
        np.testing.assert_array_equal(credit[agi > threshold + PHASE_OUT_WIDTH], 0)
        seen["falls within a group"] += np.sum(steps < 0)
        seen["full credit"] += np.sum(full & (credit > 0))
        seen["beyond the phase-out"] += np.sum(agi > threshold + PHASE_OUT_WIDTH)
        seen[f"year {year}"] += 1

    check()
    missing = [
        name
        for name in [
            "falls within a group",
            "full credit",
            "beyond the phase-out",
            "year 2025",
            "year 2026",
        ]
        if seen[name] == 0
    ]
    assert not missing, (missing, seen)


def threshold_table(year):
    scales = model_thresholds(year)
    dependents = np.arange(1, 11)
    return {
        name: getattr(scales, name).calc(dependents).astype(float)
        for name in (
            "single",
            "joint",
            "separate",
            "head_of_household",
            "surviving_spouse",
        )
    }


def test_threshold_tables():
    dependents = np.arange(1, 11)
    statutory = {
        "joint": np.array([statutory_threshold("JOINT", d) for d in dependents]),
        "single": np.array([statutory_threshold("SINGLE", d) for d in dependents]),
    }
    for year in TABLE_YEARS:
        table = threshold_table(year)
        # 6. Ordering and equalities.
        np.testing.assert_array_equal(table["separate"], table["single"])
        np.testing.assert_array_equal(table["head_of_household"], table["single"])
        np.testing.assert_array_equal(table["surviving_spouse"], table["joint"])
        assert np.all(table["joint"] >= table["single"]), year
        for values in table.values():
            assert np.all(np.diff(values) >= 0), (year, values)
        # 7. The statutory table, scaled by one common factor from 2026.
        factor = table["joint"] / statutory["joint"]
        np.testing.assert_allclose(
            table["single"] / statutory["single"], factor, rtol=1e-12
        )
        np.testing.assert_allclose(factor, factor[0], rtol=1e-12)
        if year == 2025:
            np.testing.assert_array_equal(factor, 1)
        else:
            assert factor[0] >= 1, (year, factor[0])

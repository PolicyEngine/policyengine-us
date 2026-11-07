"""Invariants of the child care income limits that states post.

Each chart below copies one state document, so it acts as a second implementation
of that state's limit. Each rule below states the same limit as a rate, a guideline
year and a rounding rule, written apart from the formulas.

1. Posted charts: a family at the printed top of a chart passes the income test and
   a family one dollar over fails, for every family size on the chart. Nevada prints
   the nearest dollar and tests the unrounded share, so its test allows one dollar.
2. Rules: for every date in RULES and for any income, a family passes exactly when
   its income is at or below the rate times that date's guideline, rounded as the
   state's chart rounds. This also makes each income test monotonic in income.
3. Enrolled families: a family that passes as a new applicant passes as an enrolled
   family at the same income, in every state with separate limits.
4. Ohio: the voucher pays only families over the Publicly Funded Child Care limit,
   never pays more than the charge, and leaves the two programs exclusive, including
   for homeless families, whom Publicly Funded Child Care serves without its income
   test. Together the two income tests stay monotonic. The voucher's own test breaks
   monotonicity on purpose, since a family under the intake limit belongs to
   Publicly Funded Child Care.
5. Nevada: while the April to September 2024 percent-of-income schedule applied, no
   family owed more than 7% of income, and sizes above 14 use the 14-person column.
6. Georgia: the program test equals its conjuncts, a priority group never removes
   eligibility, and enrollment replaces the priority group.
7. A family of three earning $40,000 gets the result each state's chart gives.

YAML pins single households. These tests walk whole charts and many incomes in one
simulation, which keeps them fast enough to run in CI.
"""

import math
from dataclasses import dataclass
from typing import Callable, Optional

import numpy as np
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation


def simulate(
    state, month, families, income_variable, spm=None, person=None, household=None
):
    """Build one simulation with a separate household per (size, monthly income)."""
    year = int(month[:4])
    people, tax_units, spm_units, family_units, households = {}, {}, {}, {}, {}
    marital_units = {}
    for index, (size, income) in enumerate(families):
        members = [f"person_{index}_{slot}" for slot in range(size)]
        for slot, member in enumerate(members):
            people[member] = {
                "age": {year: 30 if slot == 0 else 5},
                "immigration_status": {year: "CITIZEN"},
                "weekly_hours_worked_before_lsr": {year: 40 if slot == 0 else 0},
            }
            people[member].update(person(index, slot) if person else {})
            # Without explicit marital units, every person would share one.
            marital_units[f"marital_{index}_{slot}"] = {"members": [member]}
        income_input = (
            {year: income * 12}
            if income_variable == "nv_ccdp_countable_income"
            else {month: income}
        )
        spm_units[f"spm_{index}"] = {
            "members": members,
            income_variable: income_input,
            **(spm(index) if spm else {}),
        }
        tax_units[f"tax_{index}"] = {"members": members}
        family_units[f"family_{index}"] = {"members": members}
        households[f"household_{index}"] = {
            "members": members,
            "state_code": {year: state},
            **(household(index) if household else {}),
        }
    return Simulation(
        situation={
            "people": people,
            "tax_units": tax_units,
            "spm_units": spm_units,
            "families": family_units,
            "marital_units": marital_units,
            "households": households,
        }
    )


def passes(test, month, families):
    """Run an income test for (size, monthly income) families."""

    def enrolled(_):
        return {test.enrolled_variable: {month: True}}

    spm = enrolled if test.enrolled_variable and test.enrolled else None
    simulation = simulate(test.state, month, families, test.income, spm=spm)
    return simulation.calculate(test.eligible, month).astype(bool)


@dataclass(frozen=True)
class Program:
    state: str
    eligible: str
    income: str
    enrolled_variable: Optional[str] = None
    enrolled: bool = False


AL = Program(
    "AL", "al_ccsp_income_eligible", "al_ccsp_countable_income", "al_ccsp_enrolled"
)
AL_ENROLLED = Program(
    "AL",
    "al_ccsp_income_eligible",
    "al_ccsp_countable_income",
    "al_ccsp_enrolled",
    True,
)
ID = Program(
    "ID", "id_iccp_income_eligible", "id_iccp_countable_income", "id_iccp_enrolled"
)
IN = Program(
    "IN", "in_ccdf_income_eligible", "in_ccdf_countable_income", "is_in_ccdf_enrolled"
)
MO = Program(
    "MO", "mo_ccs_income_eligible", "mo_ccs_adjusted_income", "mo_ccs_enrolled"
)
MO_ENROLLED = Program(
    "MO", "mo_ccs_income_eligible", "mo_ccs_adjusted_income", "mo_ccs_enrolled", True
)
WV = Program("WV", "wv_ccap_income_eligible", "wv_ccap_countable_income")
MT = Program(
    "MT", "mt_ccap_income_eligible", "mt_ccap_countable_income", "mt_ccap_enrolled"
)
MT_ENROLLED = Program(
    "MT",
    "mt_ccap_income_eligible",
    "mt_ccap_countable_income",
    "mt_ccap_enrolled",
    True,
)
NV = Program(
    "NV", "nv_ccdp_income_eligible", "nv_ccdp_countable_income", "nv_ccdp_enrolled"
)
NV_ENROLLED = Program(
    "NV",
    "nv_ccdp_income_eligible",
    "nv_ccdp_countable_income",
    "nv_ccdp_enrolled",
    True,
)
OH = Program(
    "OH", "oh_ccap_income_eligible", "oh_ccap_countable_income", "oh_ccap_enrolled"
)
OH_VOUCHER = Program("OH", "oh_ccvp_eligible", "oh_ccap_countable_income")
GA = Program(
    "GA", "ga_caps_income_eligible", "ga_caps_countable_income", "ga_caps_enrolled"
)
GA_ENROLLED = Program(
    "GA",
    "ga_caps_income_eligible",
    "ga_caps_countable_income",
    "ga_caps_enrolled",
    True,
)
GA_VERY_LOW = Program(
    "GA", "ga_caps_priority_group_eligible", "ga_caps_countable_income"
)


@dataclass(frozen=True)
class Chart:
    source: str
    program: Program
    month: str
    tops: dict
    annual: bool = False


CHARTS = [
    Chart(
        "Alabama fact sheet, June 1, 2026, initial",
        AL,
        "2026-06",
        {2: 2_644, 3: 3_331, 4: 4_019, 5: 4_706, 6: 5_394, 7: 6_081, 8: 6_769},
    ),
    Chart(
        "Alabama fact sheet, June 1, 2026, continuing",
        AL_ENROLLED,
        "2026-06",
        {2: 2_996, 3: 3_775, 4: 4_555, 5: 5_334, 6: 6_113, 7: 6_892, 8: 7_671},
    ),
    Chart(
        "Idaho Department of Health and Welfare, October 2025",
        ID,
        "2026-01",
        {2: 2_292, 3: 2_888, 4: 3_483, 5: 4_079, 6: 4_675, 7: 5_271, 8: 5_867},
    ),
    Chart(
        "Indiana FSSA, April 5, 2026",
        IN,
        "2026-05",
        {2: 2_435, 3: 3_074, 4: 3_713, 5: 4_352, 6: 4_991, 7: 5_630, 8: 6_269},
    ),
    Chart(
        "Indiana CCDF plan, March 31, 2024",
        IN,
        "2024-06",
        {1: 1_883, 2: 2_555, 3: 3_228, 4: 3_900, 5: 4_573},
    ),
    Chart(
        "Missouri DESE, July 1, 2026, traditional",
        MO,
        "2026-07",
        {
            1: 1_956,
            2: 2_644,
            3: 3_331,
            4: 4_019,
            5: 4_706,
            6: 5_394,
            7: 6_081,
            8: 6_769,
        },
    ),
    Chart(
        "Missouri DESE, July 1, 2026, Transitional Level 2",
        MO_ENROLLED,
        "2026-07",
        {1: 2_804, 2: 3_789, 3: 4_775, 4: 5_760, 5: 6_746, 6: 7_731, 7: 8_716},
    ),
    Chart(
        "West Virginia Appendix A, FY 2024",
        WV,
        "2026-01",
        {
            1: 2_322,
            2: 3_151,
            3: 3_981,
            4: 4_810,
            5: 5_639,
            6: 6_469,
            7: 7_298,
            8: 8_128,
            9: 8_957,
        },
    ),
    Chart(
        "Montana Sliding Fee Scale, July 1, 2025, Standard",
        MT,
        "2026-01",
        {2: 3_261, 3: 4_109, 4: 4_956, 5: 5_804, 6: 6_652, 7: 7_500, 8: 8_348},
    ),
    Chart(
        "Montana Sliding Fee Scale, July 1, 2025, Graduated",
        MT_ENROLLED,
        "2026-01",
        {2: 3_525, 3: 4_442, 4: 5_358, 5: 6_275, 6: 7_192, 7: 8_108, 8: 9_025},
    ),
    Chart(
        "Ohio Procedure Letter 21, Publicly Funded Child Care",
        OH,
        "2026-01",
        {2: 2_556, 3: 3_221, 4: 3_885, 5: 4_550, 6: 5_214, 7: 5_879, 8: 6_544},
    ),
    Chart(
        "Ohio Procedure Letter 45, Publicly Funded Child Care",
        OH,
        "2026-10",
        {2: 2_615, 3: 3_302, 4: 3_988, 5: 4_674, 6: 5_361, 7: 6_047, 8: 6_733},
    ),
    Chart(
        "Ohio Procedure Letter 21, Child Care Choice Voucher",
        OH_VOUCHER,
        "2026-01",
        {2: 3_525, 3: 4_442, 4: 5_359, 5: 6_275, 6: 7_192, 7: 8_109, 8: 9_025},
    ),
    Chart(
        "Ohio Procedure Letter 45, Child Care Choice Voucher",
        OH_VOUCHER,
        "2026-10",
        {2: 3_607, 3: 4_554, 4: 5_500, 5: 6_447, 6: 7_394, 7: 8_340, 8: 9_287},
    ),
    Chart(
        "Georgia Appendix A, October 5, 2026, initial",
        GA,
        "2026-10",
        dict(
            zip(
                range(1, 15),
                [
                    29_931,
                    39_141,
                    48_350,
                    57_559,
                    66_769,
                    75_978,
                    77_705,
                    79_432,
                    81_159,
                    82_885,
                    84_612,
                    86_339,
                    88_066,
                    89_793,
                ],
            )
        ),
        annual=True,
    ),
    Chart(
        "Georgia Appendix A, October 5, 2026, ongoing",
        GA_ENROLLED,
        "2026-10",
        dict(
            zip(
                range(1, 15),
                [
                    50_883,
                    66_539,
                    82_195,
                    97_851,
                    113_507,
                    129_163,
                    132_098,
                    135_034,
                    137_969,
                    140_905,
                    143_840,
                    146_776,
                    149_711,
                    152_647,
                ],
            )
        ),
        annual=True,
    ),
    Chart(
        "Georgia Appendix A, October 5, 2026, very low income",
        GA_VERY_LOW,
        "2026-10",
        dict(
            zip(
                range(1, 15),
                [
                    7_980,
                    10_820,
                    13_660,
                    16_500,
                    19_340,
                    22_180,
                    25_020,
                    27_860,
                    30_700,
                    33_540,
                    36_380,
                    39_220,
                    42_060,
                    44_900,
                ],
            )
        ),
        annual=True,
    ),
]

NEVADA_CHARTS = [
    Chart(
        "Nevada transmittal, October 1, 2026, intake",
        NV,
        "2026-10",
        {
            1: 1_866,
            2: 2_440,
            3: 3_014,
            4: 3_588,
            5: 4_163,
            6: 4_737,
            7: 4_844,
            8: 4_952,
            9: 5_060,
        },
    ),
    Chart(
        "Nevada transmittal, October 1, 2026, renewal",
        NV_ENROLLED,
        "2026-10",
        {
            1: 2_230,
            2: 2_916,
            3: 3_602,
            4: 4_289,
            5: 4_975,
            6: 5_661,
            7: 5_790,
            8: 5_918,
            9: 6_047,
        },
    ),
]


def monthly(annual_amount):
    """An annual amount as monthly income, rounded down to the cent.

    The model stores income as float32, which near $150,000 a year resolves only
    to about 1.6 cents. Rounding the at-limit family down a cent keeps it at or
    below the annual limit after the model multiplies by 12.
    """
    return math.floor(annual_amount * 100 / 12) / 100


@pytest.mark.parametrize("chart", CHARTS, ids=lambda chart: chart.source)
def test_family_at_the_posted_top_passes_and_one_dollar_over_fails(chart):
    families = []
    for size, top in chart.tops.items():
        if chart.annual:
            families += [(size, monthly(top)), (size, (top + 1) / 12)]
        else:
            families += [(size, top), (size, top + 1)]
    result = passes(chart.program, chart.month, families)
    assert result.tolist() == [True, False] * len(chart.tops)


@pytest.mark.parametrize("chart", NEVADA_CHARTS, ids=lambda chart: chart.source)
def test_nevada_tests_the_unrounded_share_within_a_dollar_of_the_chart(chart):
    families = []
    for size, top in chart.tops.items():
        families += [(size, top - 1), (size, top + 1)]
    result = passes(chart.program, chart.month, families)
    assert result.tolist() == [True, False] * len(chart.tops)


# HHS poverty guidelines for the contiguous states, as (first person, each additional).
GUIDELINES = {
    2022: (13_590, 4_720),
    2023: (14_580, 5_140),
    2024: (15_060, 5_380),
    2025: (15_650, 5_500),
    2026: (15_960, 5_680),
}


def guideline(year, size):
    first, additional = GUIDELINES[year]
    return first + additional * (size - 1)


def nearest_dollar(amount):
    """Half a dollar goes up, as Alabama, Indiana, Missouri, West Virginia and Montana print."""
    return math.floor(round(amount, 2) + 0.5)


def next_dollar(amount):
    """Any cents go up, as Idaho and Ohio print."""
    return math.ceil(round(amount, 2))


@dataclass(frozen=True)
class Rule:
    program: Program
    month: str
    guideline_year: int
    rate: float
    rounding: Callable

    def top(self, size):
        return self.rounding(guideline(self.guideline_year, size) * self.rate / 12)


RULES = [
    # Alabama's fact sheets apply the prior year's guideline.
    Rule(AL, "2026-01", 2025, 1.8, nearest_dollar),
    Rule(AL, "2026-05", 2025, 1.8, nearest_dollar),
    Rule(AL, "2026-06", 2025, 1.5, nearest_dollar),
    Rule(AL_ENROLLED, "2026-01", 2025, 2, nearest_dollar),
    Rule(AL_ENROLLED, "2026-06", 2025, 1.7, nearest_dollar),
    # Idaho's rule set 130% until April 6, 2023, and 175% from then. The department
    # reopened at 130% on January 13, 2025, and kept the 2024 guideline until its
    # October 2025 table.
    Rule(ID, "2022-06", 2022, 1.3, next_dollar),
    Rule(ID, "2023-06", 2023, 1.75, next_dollar),
    Rule(ID, "2025-02", 2024, 1.3, next_dollar),
    Rule(ID, "2025-09", 2024, 1.3, next_dollar),
    Rule(ID, "2025-10", 2025, 1.3, next_dollar),
    Rule(ID, "2026-06", 2025, 1.3, next_dollar),
    # Indiana's charts move partway through each year.
    Rule(IN, "2024-06", 2024, 1.5, nearest_dollar),
    Rule(IN, "2025-03", 2024, 1.5, nearest_dollar),
    Rule(IN, "2025-06", 2025, 1.5, nearest_dollar),
    Rule(IN, "2026-01", 2025, 1.5, nearest_dollar),
    Rule(IN, "2026-04", 2025, 1.5, nearest_dollar),
    Rule(IN, "2026-05", 2026, 1.35, nearest_dollar),
    # Missouri holds the 2025 guideline through 2026.
    Rule(MO, "2025-11", 2025, 1.5, nearest_dollar),
    Rule(MO, "2026-01", 2025, 1.5, nearest_dollar),
    Rule(MO, "2026-07", 2025, 1.5, nearest_dollar),
    Rule(MO_ENROLLED, "2026-06", 2025, 2.42, nearest_dollar),
    Rule(MO_ENROLLED, "2026-07", 2025, 2.15, nearest_dollar),
    # West Virginia's Appendix A still prints the 2024 guideline.
    Rule(WV, "2024-06", 2024, 1.85, nearest_dollar),
    Rule(WV, "2025-03", 2024, 1.85, nearest_dollar),
    Rule(WV, "2026-03", 2024, 1.85, nearest_dollar),
    # Montana's scale moves each July.
    Rule(MT, "2024-03", 2024, 1.85, nearest_dollar),
    Rule(MT, "2025-03", 2024, 1.85, nearest_dollar),
    Rule(MT, "2025-07", 2025, 1.85, nearest_dollar),
    Rule(MT, "2026-03", 2025, 1.85, nearest_dollar),
    Rule(MT_ENROLLED, "2025-07", 2025, 2, nearest_dollar),
    Rule(MT_ENROLLED, "2026-03", 2025, 2, nearest_dollar),
    # Ohio moves each October.
    Rule(OH, "2026-01", 2025, 1.45, next_dollar),
    Rule(OH, "2026-09", 2025, 1.45, next_dollar),
    Rule(OH, "2026-10", 2026, 1.45, next_dollar),
]

SMALL_FAMILIES = st.lists(
    st.tuples(
        st.integers(min_value=1, max_value=6),
        st.integers(min_value=0, max_value=12_000),
    ),
    min_size=20,
    max_size=20,
)


@pytest.mark.parametrize(
    "rule",
    RULES,
    ids=lambda rule: (
        f"{rule.program.state}-{rule.month}"
        + ("-enrolled" if rule.program.enrolled else "")
    ),
)
def test_limit_equals_rate_times_dated_guideline(rule):
    @settings(max_examples=2, deadline=None)
    @given(families=SMALL_FAMILIES)
    def check(families):
        # Each family also sits at its top and one dollar over, the two cases a
        # random income almost never lands on.
        sizes = sorted({size for size, _ in families})
        edges = [
            (size, income)
            for size in sizes
            for income in (rule.top(size), rule.top(size) + 1)
        ]
        cases = families + edges
        result = passes(rule.program, rule.month, cases)
        expected = [income <= rule.top(size) for size, income in cases]
        assert result.tolist() == expected

    check()


# Nevada's four-person state median income, by the October that starts each table.
NEVADA_SMI = {
    "2017-10": 69_361,
    "2018-10": 71_593,
    "2021-10": 82_509,
    "2023-10": 89_325,
    "2024-10": 96_026,
    "2026-10": 105_027,
}
SMI_SIZE_FACTOR = {1: 0.52, 2: 0.68, 3: 0.84, 4: 1.0, 5: 1.16, 6: 1.32}

NEVADA_RULES = [
    (NV, "2018-09", "2017-10", 0.85),
    (NV, "2018-10", "2018-10", 0.41),
    (NV, "2022-06", "2021-10", 0.41),
    (NV, "2022-07", "2021-10", 0.85),
    (NV, "2024-09", "2023-10", 0.85),
    (NV, "2024-10", "2024-10", 0.41),
    (NV_ENROLLED, "2024-09", "2023-10", 0.85),
    (NV_ENROLLED, "2024-10", "2024-10", 0.49),
    (NV, "2026-10", "2026-10", 0.41),
    (NV_ENROLLED, "2026-10", "2026-10", 0.49),
]


@pytest.mark.parametrize(
    "program, month, table, rate",
    NEVADA_RULES,
    ids=lambda value: value.eligible if isinstance(value, Program) else str(value),
)
def test_nevada_limit_equals_rate_times_dated_median_income(
    program, month, table, rate
):
    sizes = list(SMI_SIZE_FACTOR)
    tops = {
        size: NEVADA_SMI[table] * SMI_SIZE_FACTOR[size] * rate / 12 for size in sizes
    }
    families = []
    for size in sizes:
        families += [(size, tops[size] - 1), (size, tops[size] + 1)]
    result = passes(program, month, families)
    assert result.tolist() == [True, False] * len(sizes)


ENROLLMENT_PAIRS = [
    (AL, AL_ENROLLED, "2026-06"),
    (AL, AL_ENROLLED, "2026-01"),
    (
        ID,
        Program(
            "ID",
            "id_iccp_income_eligible",
            "id_iccp_countable_income",
            "id_iccp_enrolled",
            True,
        ),
        "2026-01",
    ),
    (
        IN,
        Program(
            "IN",
            "in_ccdf_income_eligible",
            "in_ccdf_countable_income",
            "is_in_ccdf_enrolled",
            True,
        ),
        "2026-05",
    ),
    (MO, MO_ENROLLED, "2026-07"),
    (MT, MT_ENROLLED, "2026-03"),
    (NV, NV_ENROLLED, "2024-10"),
    (NV, NV_ENROLLED, "2022-07"),
    (
        OH,
        Program(
            "OH",
            "oh_ccap_income_eligible",
            "oh_ccap_countable_income",
            "oh_ccap_enrolled",
            True,
        ),
        "2026-10",
    ),
    (GA, GA_ENROLLED, "2026-01"),
    (GA, GA_ENROLLED, "2026-10"),
]


@pytest.mark.parametrize(
    "new, enrolled, month",
    ENROLLMENT_PAIRS,
    ids=lambda value: value.state if isinstance(value, Program) else str(value),
)
def test_new_applicant_who_passes_also_passes_when_enrolled(new, enrolled, month):
    @settings(max_examples=2, deadline=None)
    @given(families=SMALL_FAMILIES)
    def check(families):
        passes_new = passes(new, month, families)
        passes_enrolled = passes(enrolled, month, families)
        assert not (passes_new & ~passes_enrolled).any()

    check()


OHIO_MONTHS = ["2025-11", "2026-01", "2026-10", "2026-11"]


def ohio_family_results(month, cases, charges=None, homeless=None):
    """Run Ohio for families whose children are 2 and in center care.

    Each child's provider charges charges[index] a year ($24,000 unless given), and
    homeless[index] marks a homeless household.
    """
    year = int(month[:4])

    def person(index, slot):
        if slot == 0:
            return {}
        return {
            "age": {year: 2},
            "childcare_hours_per_week": {year: 40},
            "oh_ccap_provider_type": {month: "CENTER"},
            "pre_subsidy_childcare_expenses": {
                year: charges[index] if charges else 24_000
            },
        }

    def household(index):
        return {"is_homeless": {year: homeless[index]}} if homeless else {}

    simulation = simulate(
        "OH",
        month,
        cases,
        "oh_ccap_countable_income",
        person=person,
        household=household,
    )
    return {
        variable: simulation.calculate(variable, month)
        for variable in [
            "oh_ccap",
            "oh_ccvp",
            "oh_ccap_income_eligible",
            "oh_ccvp_eligible",
        ]
    }


@pytest.mark.parametrize("month", OHIO_MONTHS)
def test_ohio_voucher_stays_apart_from_publicly_funded_child_care(month):
    # Each child's provider charges $300 a month, under every voucher rate, or
    # $2,000, over them. Homeless families qualify for Publicly Funded Child Care
    # without its income test.
    families = [
        (size, income, annual_charge, homeless)
        for size in (2, 3, 4)
        for income in range(1_500, 9_500, 250)
        for annual_charge in (3_600, 24_000)
        for homeless in (False, True)
    ]
    results = ohio_family_results(
        month,
        [(size, income) for size, income, _, _ in families],
        charges=[annual_charge for _, _, annual_charge, _ in families],
        homeless=[homeless for _, _, _, homeless in families],
    )
    voucher = results["oh_ccvp"]
    publicly_funded = results["oh_ccap"]
    charge = np.array(
        [(size - 1) * annual_charge / 12 for size, _, annual_charge, _ in families]
    )
    homeless = np.array([homeless for _, _, _, homeless in families])
    # Exclusive: a family drawing the voucher draws nothing from the other program.
    assert not ((voucher > 0) & (publicly_funded > 0)).any()
    # The voucher never pays more than the family's charge...
    assert (voucher <= charge + 0.01).all()
    # ...and the charge sets the payment for some families, so the bound binds.
    assert ((voucher > 0) & (np.abs(voucher - charge) < 0.01)).any()
    # Homeless families draw Publicly Funded Child Care at any income, so none draws
    # the voucher, and some over that program's intake limit draw it.
    assert not (voucher[homeless] > 0).any()
    over_intake_limit = ~results["oh_ccap_income_eligible"].astype(bool)
    assert ((publicly_funded > 0) & homeless & over_intake_limit).any()
    # The voucher pays in some months of this range, so the checks above bind.
    assert (voucher > 0).any()
    # Only families over the intake limit qualify.
    assert not (
        results["oh_ccvp_eligible"].astype(bool)
        & results["oh_ccap_income_eligible"].astype(bool)
    ).any()


@pytest.mark.parametrize("month", ["2026-01", "2026-10"])
def test_ohio_income_tests_together_are_monotonic(month):
    incomes = list(range(0, 12_000, 150))
    cases = [(3, income) for income in incomes]
    results = ohio_family_results(month, cases)
    either = results["oh_ccap_income_eligible"].astype(bool) | results[
        "oh_ccvp_eligible"
    ].astype(bool)
    # Once a family fails both tests, every higher income fails both.
    assert (np.diff(either.astype(int)) <= 0).all()


def test_ohio_voucher_test_alone_is_not_monotonic_by_design():
    # Intended violation, minimized: the same family fails the voucher at $3,221 (it
    # belongs to Publicly Funded Child Care) and passes at $3,222.
    results = ohio_family_results("2026-01", [(3, 3_221), (3, 3_222)])
    assert results["oh_ccvp_eligible"].astype(bool).tolist() == [False, True]


def test_nevada_copay_stays_within_seven_percent_of_income():
    month = "2024-06"
    cases = [
        (size, income)
        for size in (1, 2, 3, 4, 5, 8, 14)
        for income in range(0, 9_000, 300)
    ]
    simulation = simulate("NV", month, cases, "nv_ccdp_countable_income")
    copay = simulation.calculate("nv_ccdp_copay", month)
    income = np.array([income for _, income in cases], dtype=float)
    assert (copay <= income * 0.07 + 0.01).all()
    # The schedule charges something in this range, so the bound binds.
    assert (copay > 0).any()


def test_nevada_copay_uses_the_fourteen_person_column_above_fourteen():
    month = "2024-06"
    cases = [
        (size, income) for income in range(0, 12_000, 400) for size in (14, 15, 18)
    ]
    simulation = simulate("NV", month, cases, "nv_ccdp_countable_income")
    copay = simulation.calculate("nv_ccdp_copay", month).reshape(-1, 3)
    # The copay depends on income and the column, so equal incomes give equal copays.
    assert (copay[:, 1] == copay[:, 0]).all()
    assert (copay[:, 2] == copay[:, 0]).all()


GEORGIA_FLAGS = st.fixed_dictionaries(
    {
        "size": st.integers(min_value=2, max_value=5),
        "income": st.integers(min_value=0, max_value=8_000),
        "hours": st.sampled_from([0, 20, 40]),
        "enrolled": st.booleans(),
        "pre_k": st.booleans(),
        "domestic_violence": st.booleans(),
    }
)


def georgia_results(month, families, **overrides):
    year = int(month[:4])
    enrolled = overrides.get("enrolled")
    pre_k = overrides.get("pre_k")

    def spm(index):
        family = families[index]
        return {
            "ga_caps_enrolled": {
                month: family["enrolled"] if enrolled is None else enrolled
            },
            "ga_caps_domestic_violence": {month: family["domestic_violence"]},
        }

    def person(index, slot):
        family = families[index]
        if slot == 0:
            return {"weekly_hours_worked_before_lsr": {year: family["hours"]}}
        return {
            "ga_caps_pre_k_enrolled": {
                month: family["pre_k"] if pre_k is None else pre_k
            }
        }

    simulation = simulate(
        "GA",
        month,
        [(family["size"], family["income"]) for family in families],
        "ga_caps_countable_income",
        spm=spm,
        person=person,
    )
    return {
        variable: simulation.calculate(variable, month).astype(bool)
        for variable in [
            "ga_caps_eligible",
            "ga_caps_income_eligible",
            "ga_caps_activity_eligible",
            "ga_caps_priority_group_eligible",
            "ga_caps_enrolled",
        ]
    }


@pytest.mark.parametrize(
    "month", ["2015-06", "2022-11", "2024-08", "2026-01", "2026-10"]
)
def test_georgia_eligibility_is_the_product_of_its_tests(month):
    @settings(max_examples=2, deadline=None)
    @given(families=st.lists(GEORGIA_FLAGS, min_size=20, max_size=20))
    def check(families):
        results = georgia_results(month, families)
        # Every family has a citizen child under 13 and assets under the limit, so
        # those two conjuncts hold for all of them.
        expected = (
            results["ga_caps_income_eligible"]
            & results["ga_caps_activity_eligible"]
            & (results["ga_caps_priority_group_eligible"] | results["ga_caps_enrolled"])
        )
        assert (results["ga_caps_eligible"] == expected).all()

    check()


def test_georgia_priority_group_never_removes_eligibility():
    @settings(max_examples=2, deadline=None)
    @given(families=st.lists(GEORGIA_FLAGS, min_size=20, max_size=20))
    def check(families):
        without = georgia_results("2026-10", families, enrolled=False, pre_k=False)
        with_group = georgia_results("2026-10", families, enrolled=False, pre_k=True)
        assert not (without["ga_caps_eligible"] & ~with_group["ga_caps_eligible"]).any()
        assert with_group["ga_caps_priority_group_eligible"].all()

    check()


def test_georgia_enrollment_replaces_the_priority_group():
    @settings(max_examples=2, deadline=None)
    @given(families=st.lists(GEORGIA_FLAGS, min_size=20, max_size=20))
    def check(families):
        results = georgia_results("2026-10", families, enrolled=True, pre_k=False)
        expected = (
            results["ga_caps_income_eligible"] & results["ga_caps_activity_eligible"]
        )
        assert (results["ga_caps_eligible"] == expected).all()

    check()


FORTY_THOUSAND_A_YEAR = 40_000 / 12

FAMILY_OF_THREE_AT_40000 = [
    # Each row gives the result the state's chart gives for three people at $40,000.
    (AL, "2026-01", True),  # Fact sheet, January 2026: up to $3,998.
    (AL, "2026-06", False),  # Fact sheet, June 2026: up to $3,331.
    (ID, "2026-01", False),  # Department table: up to $2,888.
    (IN, "2026-01", False),  # 150% of the 2025 guideline: up to $3,331.
    (IN, "2026-05", False),  # FSSA chart, April 5, 2026: up to $3,074.
    (MO, "2026-01", False),  # DESE chart: up to $3,331.
    (WV, "2026-01", True),  # Appendix A: up to $3,981.
    (MT, "2026-01", True),  # Sliding Fee Scale: up to $4,109.
    (NV, "2026-01", False),  # Transmittal CC PT 06-25, 41% of median income.
    (OH, "2026-01", False),  # Procedure Letter 21: up to $3,221.
    (OH_VOUCHER, "2026-01", True),  # Procedure Letter 21: voucher up to $4,442.
    (GA, "2026-01", False),  # 40% of median income: $37,208 a year.
    (GA, "2026-10", True),  # Appendix A: $48,350 a year.
]


@pytest.mark.parametrize(
    "program, month, expected",
    FAMILY_OF_THREE_AT_40000,
    ids=lambda value: value.eligible if isinstance(value, Program) else str(value),
)
def test_family_of_three_earning_40000(program, month, expected):
    result = passes(program, month, [(3, FORTY_THOUSAND_A_YEAR)])
    assert result.tolist() == [expected]

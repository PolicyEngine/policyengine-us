"""Invariants of the child care income limits that states post.

The state YAML files pin each posted chart: every printed family size at its top
passes and a dollar more fails. These tests check properties across many incomes and
families, one simulation per case, which single YAML households can't draw:

1. Rules: for every date in RULES and NEVADA_RULES and for any income, a family passes
   exactly when its income is at or below the rate times that date's guideline or
   median income, rounded as the state's chart rounds. In Indiana and West Virginia
   the limit stops at 85% of the state median income, which binds only for large
   families, so those rules draw families of up to 20 and 11 people. This also makes
   each income test monotonic in income. Each rule states the limit apart from the
   formulas, so it acts as a second implementation.
2. Enrolled families: a family that passes as a new applicant passes as an enrolled
   family at the same income, in every state with separate limits.
3. Ohio: the voucher pays only families over the Publicly Funded Child Care limit,
   never pays more than the charge, and leaves the two programs exclusive, including
   for homeless families, whom Publicly Funded Child Care serves without its income
   test. Together the two income tests stay monotonic. The voucher's own test breaks
   monotonicity on purpose, since a family under the intake limit belongs to
   Publicly Funded Child Care.
4. Nevada: while the April to September 2024 percent-of-income schedule applied, no
   family owed more than 7% of income, and sizes above 14 use the 14-person column.
5. Georgia: the program test equals its conjuncts, a priority group never removes
   eligibility, and enrollment replaces the priority group.

Hypothesis draws families from a fixed seed, so every run checks the same ones. The
properties also check fixed families: each size at its limit, and a grid of Georgia
families, some failing only one test.
"""

import itertools
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
IN_ENROLLED = Program(
    "IN",
    "in_ccdf_income_eligible",
    "in_ccdf_countable_income",
    "is_in_ccdf_enrolled",
    True,
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
MD = Program(
    "MD", "md_ccs_income_eligible", "md_ccs_countable_income", "md_ccs_enrolled"
)
MD_ENROLLED = Program(
    "MD",
    "md_ccs_income_eligible",
    "md_ccs_countable_income",
    "md_ccs_enrolled",
    True,
)


# HHS poverty guidelines for the contiguous states, as (first person, each additional).
GUIDELINES = {
    2018: (12_140, 4_320),
    2019: (12_490, 4_420),
    2020: (12_760, 4_480),
    2021: (12_880, 4_540),
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
    """Half a dollar goes up, as Alabama, Indiana, Missouri, West Virginia, Montana and
    Nevada print."""
    return math.floor(round(amount, 2) + 0.5)


def next_dollar(amount):
    """Any cents go up, as Idaho, Ohio and Indiana's 85% limits print."""
    return math.ceil(round(amount, 2))


def median_share(size):
    """A family's share of the four-person state median income (45 CFR 96.85(b)):
    52% for one person, 16 points more for each person through six, and 3 points for
    each person after that."""
    return 0.52 + 0.16 * (min(size, 6) - 1) + 0.03 * max(size - 6, 0)


@dataclass(frozen=True)
class Rule:
    program: Program
    month: str
    # A rule without a guideline year tests the median income limit alone.
    guideline_year: Optional[int]
    rate: Optional[float] = None
    rounding: Optional[Callable] = None
    # Indiana's and West Virginia's charts stop at 85% of a four-person state median
    # income table, adjusted for family size and rounded as each chart prints.
    median: Optional[int] = None
    median_rounding: Callable = nearest_dollar
    max_size: int = 6

    def top(self, size):
        limits = []
        if self.guideline_year is not None:
            limits.append(
                self.rounding(guideline(self.guideline_year, size) * self.rate / 12)
            )
        if self.median is not None:
            limits.append(
                self.median_rounding(self.median * median_share(size) * 0.85 / 12)
            )
        return min(limits)


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
    # Indiana's charts move partway through each year. Each caps families at 85% of
    # the four-person median that starts the October before its guideline year,
    # rounded up.
    Rule(IN, "2024-06", 2024, 1.5, nearest_dollar, 95_373, next_dollar, 20),
    Rule(IN, "2025-03", 2024, 1.5, nearest_dollar, 95_373, next_dollar, 20),
    Rule(IN, "2025-06", 2025, 1.5, nearest_dollar, 103_324, next_dollar, 20),
    Rule(IN, "2026-01", 2025, 1.5, nearest_dollar, 103_324, next_dollar, 20),
    Rule(IN, "2026-04", 2025, 1.5, nearest_dollar, 103_324, next_dollar, 20),
    Rule(IN, "2026-05", 2026, 1.35, nearest_dollar, 107_555, next_dollar, 20),
    Rule(
        IN_ENROLLED,
        "2026-01",
        None,
        median=103_324,
        median_rounding=next_dollar,
        max_size=20,
    ),
    Rule(
        IN_ENROLLED,
        "2026-05",
        None,
        median=107_555,
        median_rounding=next_dollar,
        max_size=20,
    ),
    # Missouri holds the 2025 guideline through 2026.
    Rule(MO, "2025-11", 2025, 1.5, nearest_dollar),
    Rule(MO, "2026-01", 2025, 1.5, nearest_dollar),
    Rule(MO, "2026-07", 2025, 1.5, nearest_dollar),
    Rule(MO_ENROLLED, "2026-06", 2025, 2.42, nearest_dollar),
    Rule(MO_ENROLLED, "2026-07", 2025, 2.15, nearest_dollar),
    # West Virginia's Appendix A still prints the 2024 guideline, and from October 2024
    # stops at 85% of that October's four-person median.
    Rule(WV, "2024-06", 2024, 1.85, nearest_dollar),
    Rule(WV, "2024-10", 2024, 1.85, nearest_dollar, 90_661, max_size=11),
    Rule(WV, "2025-03", 2024, 1.85, nearest_dollar, 90_661, max_size=11),
    Rule(WV, "2026-03", 2024, 1.85, nearest_dollar, 90_661, max_size=11),
    Rule(WV, "2026-10", 2024, 1.85, nearest_dollar, 90_661, max_size=11),
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
    # From October 2018 through June 2022 most new applicants in Nevada faced 130% of
    # the guideline, which Nevada took up each October.
    Rule(NV, "2018-10", 2018, 1.3, nearest_dollar),
    Rule(NV, "2019-09", 2018, 1.3, nearest_dollar),
    Rule(NV, "2019-10", 2019, 1.3, nearest_dollar),
    Rule(NV, "2020-10", 2020, 1.3, nearest_dollar),
    Rule(NV, "2022-06", 2021, 1.3, nearest_dollar),
]


def families_up_to(max_size, max_income):
    """Twenty (size, monthly income) families."""
    return st.lists(
        st.tuples(
            st.integers(min_value=1, max_value=max_size),
            st.integers(min_value=0, max_value=max_income),
        ),
        min_size=20,
        max_size=20,
    )


SMALL_FAMILIES = families_up_to(6, 12_000)


@pytest.mark.parametrize(
    "rule",
    RULES,
    ids=lambda rule: (
        f"{rule.program.state}-{rule.month}"
        + ("-enrolled" if rule.program.enrolled else "")
    ),
)
def test_limit_equals_rate_times_dated_guideline(rule):
    families_drawn = (
        SMALL_FAMILIES if rule.max_size == 6 else families_up_to(rule.max_size, 16_000)
    )

    @settings(max_examples=2, deadline=None, derandomize=True)
    @given(families=families_drawn)
    def check(families):
        # Each family also sits at its top and one dollar over, the two cases a
        # random income almost never lands on, and so does the largest size, where
        # a median income cap binds.
        sizes = sorted({size for size, _ in families} | {rule.max_size})
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
    "2022-10": 85_150,
    "2023-10": 89_325,
    "2024-10": 96_026,
    "2026-10": 105_027,
}
SMI_SIZE_FACTOR = {1: 0.52, 2: 0.68, 3: 0.84, 4: 1.0, 5: 1.16, 6: 1.32}

NEVADA_RULES = [
    (NV, "2018-09", "2017-10", 0.85),
    # From October 2018 through June 2022 enrolled families kept 85% of the median,
    # while most new applicants faced the guideline (RULES).
    (NV_ENROLLED, "2019-06", "2018-10", 0.85),
    # The FFY 2022-2024 plan dates its 85% limits to July 1, 2022, on the table that
    # starts October 1, 2022.
    (NV, "2022-07", "2022-10", 0.85),
    (NV, "2022-09", "2022-10", 0.85),
    (NV, "2022-10", "2022-10", 0.85),
    (NV, "2024-09", "2023-10", 0.85),
    (NV_ENROLLED, "2024-09", "2023-10", 0.85),
    (NV, "2024-10", "2024-10", 0.41),
    (NV_ENROLLED, "2024-10", "2024-10", 0.49),
    (NV, "2026-10", "2026-10", 0.41),
    (NV_ENROLLED, "2026-10", "2026-10", 0.49),
]


def nevada_top(table, size, rate, month):
    """The highest whole-dollar monthly income that passes.

    From October 2024 the charts print each limit as the nearest dollar. Earlier
    limits keep their cents, and MS 316 rounds income to the nearest dollar, so the
    highest passing income is the limit rounded down.
    """
    limit = NEVADA_SMI[table] * SMI_SIZE_FACTOR[size] * rate / 12
    if month >= "2024-10":
        return nearest_dollar(limit)
    return math.floor(round(limit, 2))


@pytest.mark.parametrize(
    "program, month, table, rate",
    NEVADA_RULES,
    ids=lambda value: value.eligible if isinstance(value, Program) else str(value),
)
def test_nevada_limit_equals_rate_times_dated_median_income(
    program, month, table, rate
):
    sizes = list(SMI_SIZE_FACTOR)
    families = []
    for size in sizes:
        top = nevada_top(table, size, rate, month)
        families += [(size, top), (size, top + 1)]
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
    (IN, IN_ENROLLED, "2026-05"),
    (MO, MO_ENROLLED, "2026-07"),
    (MT, MT_ENROLLED, "2026-03"),
    (NV, NV_ENROLLED, "2024-10"),
    (NV, NV_ENROLLED, "2022-07"),
    (NV, NV_ENROLLED, "2019-06"),
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
    # Maryland's continuation scale moved to the federal fiscal 2025 median eight
    # months before the initial scale did.
    (MD, MD_ENROLLED, "2024-05"),
    (MD, MD_ENROLLED, "2024-11"),
    (MD, MD_ENROLLED, "2026-03"),
]


def highest_passing_incomes(program, month, high=15_000):
    """The highest monthly income at which a family of each size from 1 to 6 passes.

    Scans $100 steps up to `high`, then each dollar after the last step that passes.
    """
    sizes = range(1, 7)
    steps = range(0, high + 1, 100)
    coarse = passes(
        program, month, [(size, income) for size in sizes for income in steps]
    ).reshape(len(sizes), len(steps))
    starts = {
        size: steps[np.flatnonzero(row)[-1]]
        for size, row in zip(sizes, coarse)
        if row.any()
    }
    if not starts:
        return {}
    fine = passes(
        program,
        month,
        [
            (size, start + extra)
            for size, start in starts.items()
            for extra in range(100)
        ],
    ).reshape(len(starts), 100)
    return {
        size: start + int(np.flatnonzero(row)[-1])
        for (size, start), row in zip(starts.items(), fine)
    }


@pytest.mark.parametrize(
    "new, enrolled, month",
    ENROLLMENT_PAIRS,
    ids=lambda value: value.state if isinstance(value, Program) else str(value),
)
def test_new_applicant_who_passes_also_passes_when_enrolled(new, enrolled, month):
    # A family at the highest income that passes as a new applicant must pass when
    # enrolled. If the enrolled test is monotonic in income, passing there means
    # passing at every lower income too.
    tops = highest_passing_incomes(new, month)
    assert sorted(tops) == [1, 2, 3, 4, 5, 6]
    assert passes(enrolled, month, list(tops.items())).all(), tops

    @settings(max_examples=2, deadline=None, derandomize=True)
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


# Every combination of the drawn flags at seven incomes. The tests below check that
# the grid holds families on each side of every test they cover.
GEORGIA_GRID = [
    {
        "size": size,
        "income": income,
        "hours": hours,
        "enrolled": enrolled,
        "pre_k": pre_k,
        "domestic_violence": domestic_violence,
    }
    for size, income, hours, enrolled, pre_k, domestic_violence in itertools.product(
        [2, 3, 5],
        [100, 1_000, 2_000, 3_000, 4_500, 6_000, 7_500],
        [0, 20, 40],
        [False, True],
        [False, True],
        [False, True],
    )
]


def check_georgia_product(month, families):
    results = georgia_results(month, families)
    # Every family has a citizen child under 13 and assets under the limit, so
    # those two conjuncts hold for all of them.
    expected = (
        results["ga_caps_income_eligible"]
        & results["ga_caps_activity_eligible"]
        & (results["ga_caps_priority_group_eligible"] | results["ga_caps_enrolled"])
    )
    assert (results["ga_caps_eligible"] == expected).all()
    return results


@pytest.mark.parametrize(
    "month", ["2015-06", "2022-11", "2024-08", "2026-01", "2026-10"]
)
def test_georgia_eligibility_is_the_product_of_its_tests(month):
    results = check_georgia_product(month, GEORGIA_GRID)
    income = results["ga_caps_income_eligible"]
    activity = results["ga_caps_activity_eligible"]
    group = results["ga_caps_priority_group_eligible"]
    enrolled = results["ga_caps_enrolled"]
    # Some grid family fails each test while passing the others, and some enrolled
    # family passes outside every priority group, so dropping any term changes a
    # result. Georgia has required new applicants to belong to a priority group since
    # August 2016.
    assert (~income & activity & (group | enrolled)).any()
    assert (income & ~activity & (group | enrolled)).any()
    if month >= "2016-08":
        assert (income & activity & ~group & ~enrolled).any()
        assert (income & activity & ~group & enrolled).any()

    @settings(max_examples=2, deadline=None, derandomize=True)
    @given(families=st.lists(GEORGIA_FLAGS, min_size=20, max_size=20))
    def check(families):
        check_georgia_product(month, families)

    check()


def check_priority_group_never_removes_eligibility(families):
    without = georgia_results("2026-10", families, enrolled=False, pre_k=False)
    with_group = georgia_results("2026-10", families, enrolled=False, pre_k=True)
    assert not (without["ga_caps_eligible"] & ~with_group["ga_caps_eligible"]).any()
    assert with_group["ga_caps_priority_group_eligible"].all()
    return without, with_group


def test_georgia_priority_group_never_removes_eligibility():
    without, with_group = check_priority_group_never_removes_eligibility(GEORGIA_GRID)
    # Pre-K admits some grid families that no other group admits.
    assert (~without["ga_caps_eligible"] & with_group["ga_caps_eligible"]).any()

    @settings(max_examples=2, deadline=None, derandomize=True)
    @given(families=st.lists(GEORGIA_FLAGS, min_size=20, max_size=20))
    def check(families):
        check_priority_group_never_removes_eligibility(families)

    check()


def check_enrollment_replaces_the_priority_group(families):
    results = georgia_results("2026-10", families, enrolled=True, pre_k=False)
    expected = results["ga_caps_income_eligible"] & results["ga_caps_activity_eligible"]
    assert (results["ga_caps_eligible"] == expected).all()
    return results


def test_georgia_enrollment_replaces_the_priority_group():
    results = check_enrollment_replaces_the_priority_group(GEORGIA_GRID)
    # Some enrolled grid families pass outside every priority group.
    assert (
        results["ga_caps_eligible"] & ~results["ga_caps_priority_group_eligible"]
    ).any()

    @settings(max_examples=2, deadline=None, derandomize=True)
    @given(families=st.lists(GEORGIA_FLAGS, min_size=20, max_size=20))
    def check(families):
        check_enrollment_replaces_the_priority_group(families)

    check()

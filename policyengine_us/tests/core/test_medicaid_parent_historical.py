"""Vary household size and income, and compare unchanged Medicaid routes.

YAML covers the state examples and every table row. Hypothesis checks income
and household-size monotonicity and compares unaffected states and years through
the Simulation API. Each example reuses the read-only country system and owns
its simulation cache. The Makefile collects this file in the existing core group.
"""

from math import ceil

import numpy as np
from hypothesis import HealthCheck, example, given, settings, strategies as st

from policyengine_us import Simulation
from policyengine_us.model_api import StateCode


# Tennessee SPA TN-14-0005, AFDC Income Standards, section H.
TN_MONTHLY = (
    1018,
    1329,
    1611,
    1867,
    2102,
    2320,
    2524,
    2718,
    2903,
    3084,
    3259,
    3431,
    3601,
    3770,
    3935,
    4098,
    4257,
    4411,
    4557,
    4693,
)
# Utah DAR 43706, R414-303-4, Table 1.
UT_MONTHLY = (
    438,
    544,
    678,
    797,
    912,
    1012,
    1072,
    1132,
    1196,
    1257,
    1320,
    1382,
    1443,
    1505,
    1569,
    1630,
)
# DMAS M04 Appendix 3: July 2017, July 2018, and July 2019.
# Annual formulas use the schedule in force on January 1.
VA_MONTHLY = {
    2018: (
        (245, 373, 474, 575, 678, 764, 862, 965, 101),
        (320, 459, 577, 690, 811, 914, 1024, 1143, 114),
        (483, 646, 791, 928, 1097, 1220, 1358, 1501, 139),
    ),
    2019: (
        (250, 381, 484, 587, 692, 780, 880, 985, 104),
        (327, 469, 589, 704, 828, 933, 1045, 1166, 117),
        (493, 659, 807, 947, 1119, 1245, 1386, 1532, 142),
    ),
    2020: (
        (257, 392, 498, 604, 712, 802, 905, 1013, 107),
        (337, 483, 606, 724, 852, 960, 1075, 1199, 121),
        (507, 678, 830, 974, 1151, 1280, 1425, 1575, 146),
    ),
}
FPG = {2018: (12140, 4320), 2019: (12490, 4420), 2020: (12760, 4480)}
# Mississippi Medicaid Eligibility Policy Manual, Appendix A-3, COE-075.
# The combined monthly ceilings already include the five-percent disregard.
# Annual comparisons use each year's March table, not January/February law.
MS_MONTHLY = {
    2017: (
        277,
        374,
        469,
        565,
        661,
        756,
        852,
        947,
        1043,
        1138,
        1233,
        1329,
        1424,
        1520,
        1615,
        1711,
        1806,
        1901,
        1997,
        2092,
    ),
    2018: (
        278,
        375,
        471,
        567,
        664,
        760,
        856,
        952,
        1048,
        1144,
        1240,
        1336,
        1432,
        1528,
        1624,
        1720,
        1816,
        1912,
        2008,
        2104,
    ),
    2019: (
        279,
        377,
        473,
        569,
        667,
        763,
        860,
        956,
        1052,
        1149,
        1245,
        1342,
        1438,
        1535,
        1631,
        1727,
        1824,
        1920,
        2017,
        2113,
    ),
    2020: (
        280,
        378,
        475,
        571,
        669,
        766,
        862,
        959,
        1056,
        1152,
        1249,
        1346,
        1442,
        1539,
        1636,
        1732,
        1829,
        1926,
        2022,
        2119,
    ),
    2021: (
        281,
        379,
        476,
        572,
        670,
        767,
        864,
        961,
        1058,
        1155,
        1252,
        1349,
        1446,
        1543,
        1640,
        1736,
        1833,
        1930,
        2027,
        2124,
    ),
    2024: (
        290,
        391,
        492,
        592,
        693,
        794,
        894,
        995,
        1095,
        1196,
        1296,
        1396,
        1497,
        1597,
        1698,
        1798,
        1898,
        1999,
        2099,
        2200,
    ),
    2025: (
        292,
        394,
        495,
        596,
        698,
        799,
        900,
        1001,
        1102,
        1203,
        1303,
        1404,
        1505,
        1606,
        1707,
        1808,
        1909,
        2010,
        2111,
        2212,
    ),
    2026: (
        294,
        396,
        498,
        600,
        702,
        804,
        906,
        1007,
        1109,
        1211,
        1312,
        1414,
        1516,
        1617,
        1719,
        1821,
        1922,
        2024,
        2126,
        2227,
    ),
}
# HHS prior poverty guidelines: contiguous states, first and additional person.
MS_FPG = {
    2017: (12_060, 4_180),
    2018: (12_140, 4_320),
    2019: (12_490, 4_420),
    2020: (12_760, 4_480),
    2021: (12_880, 4_540),
    2024: (15_060, 5_380),
    2025: (15_650, 5_500),
    2026: (15_960, 5_680),
}

# Wyoming Medicaid SFY2018 report p95 and SFY2025 report p103.
# Family Care monthly standards before the five-point MAGI disregard.
WY_MONTHLY = (529, 737, 873, 999)

GROUPS = ("GROUP_I", "GROUP_II", "GROUP_III")


def make_simulation(year, cases):
    situation = {
        entity: {}
        for entity in (
            "people",
            "tax_units",
            "spm_units",
            "families",
            "marital_units",
            "households",
        )
    }
    for index, (state, size, group, income) in enumerate(cases):
        name = f"person_{index}"
        situation["people"][name] = {
            "age": {year: 30},
            "medicaid_household_size": {year: size},
            "medicaid_income_level": {year: income},
        }
        for entity in ("tax_units", "spm_units", "families", "marital_units"):
            situation[entity][name] = {"members": [name]}
        situation["households"][name] = {
            "members": [name],
            "state_code": {year: state},
            "va_medicaid_lifc_locality_group": {year: group},
        }
    return Simulation(situation=situation)


def expected_limit(year, state, size, group):
    first, additional = FPG[year]
    guideline = first + (size - 1) * additional
    if state == "TN":
        monthly = TN_MONTHLY[min(size, 20) - 1]
    elif state == "UT":
        if year < 2020:
            return 0.60
        monthly = UT_MONTHLY[min(size, 16) - 1] + max(size - 16, 0) * 62
    else:
        table = VA_MONTHLY[year][GROUPS.index(group)]
        monthly = table[min(size, 8) - 1] + max(size - 8, 0) * table[8]
    return monthly * 12 / guideline + 0.05


def expected_effective_limit(year, state, size, group):
    first, additional = FPG[year]
    guideline = first + (size - 1) * additional
    raw_limit = expected_limit(year, state, size, group)
    # Preserve main's cent stabilization and whole-dollar monthly ceiling.
    monthly_limit = ceil(round(guideline * raw_limit / 12, 2))
    return monthly_limit * 12 / guideline


@settings(
    max_examples=16,
    deadline=None,
    derandomize=True,
    suppress_health_check=[HealthCheck.too_slow],
)
@example(year=2020, size=17, gap=0.0001)
@example(year=2018, size=21, gap=0.0001)
@given(
    year=st.sampled_from((2018, 2019, 2020)),
    size=st.integers(min_value=1, max_value=32),
    gap=st.integers(min_value=1, max_value=1000).map(lambda value: value / 10_000),
)
def test_historical_limits_bound_income_and_preserve_size_schedules(year, size, gap):
    cases = []
    expected = []
    for state, group in (("TN", "GROUP_I"), ("UT", "GROUP_I")) + tuple(
        ("VA", group) for group in GROUPS
    ):
        limit = expected_limit(year, state, size, group)
        assert limit > 0
        effective_limit = expected_effective_limit(year, state, size, group)
        for income in (max(0, effective_limit - gap), effective_limit + gap):
            cases.append((state, size, group, income))
            expected.append(limit)
        cases.append((state, size + 1, group, 0))
        expected.append(expected_limit(year, state, size + 1, group))
    simulation = make_simulation(year, cases)
    actual = simulation.calculate("medicaid_parent_income_limit", year)
    np.testing.assert_allclose(actual, expected, rtol=1e-6)
    first, additional = FPG[year]
    guideline = first + (size - 1) * additional
    next_guideline = guideline + additional
    current_allowance = (actual[::3] - 0.05) * guideline
    next_allowance = (actual[2::3] - 0.05) * next_guideline
    # Allow five cents when converting the computed FPG ratios back to dollars.
    assert np.all(next_allowance + 0.05 >= current_allowance)
    current_effective = np.ceil(np.round(actual[::3] * guideline / 12, 2)) * 12
    next_effective = np.ceil(np.round(actual[2::3] * next_guideline / 12, 2)) * 12
    assert np.all(next_effective >= current_effective)
    np.testing.assert_array_equal(
        simulation.calculate("is_parent_for_medicaid_fc", year), [True, False, True] * 5
    )


@settings(max_examples=12, deadline=None, derandomize=True)
@example(year=2015, size=3)
@example(year=2017, size=3)
@example(year=2021, size=3)
@example(year=2024, size=3)
@example(year=2026, size=3)
@example(year=2025, size=3)
@given(
    year=st.sampled_from((2015, 2017, 2018, 2019, 2020, 2021, 2024, 2025, 2026)),
    size=st.integers(min_value=1, max_value=24),
)
def test_parent_limits_outside_historical_correction_equal_existing_routes(year, size):
    states = [
        state.name
        for state in StateCode
        if state.name not in ("GU", "MP", "PW", "PR", "VI", "AA", "AE", "AP")
    ]
    historical = 2018 <= year <= 2020
    if historical:
        states = [state for state in states if state not in ("UT", "TN", "VA")]
    cases = [(state, size, "GROUP_II", 0) for state in states]
    if not historical:
        cases.extend(("VA", size, group, 0) for group in ("GROUP_I", "GROUP_III"))
    simulation = make_simulation(year, cases)
    parameters = simulation.tax_benefit_system.parameters(f"{year}-01-01")
    national = parameters.gov.hhs.medicaid.eligibility.categories.parent.income_limit
    expected = np.array([national[state] for state, _, _, _ in cases])
    if year in MS_MONTHLY and 1 <= size <= 20:
        first, additional = MS_FPG[year]
        guideline = first + (size - 1) * additional
        expected[states.index("MS")] = MS_MONTHLY[year][size - 1] * 12 / guideline
    if year in MS_FPG and 1 <= size <= 4:
        first, additional = MS_FPG[year]
        guideline = first + (size - 1) * additional
        expected[states.index("WY")] = WY_MONTHLY[size - 1] * 12 / guideline + 0.05
    if year < 2018:
        # Keep Utah's existing 0.49 input before the historical correction.
        expected[states.index("UT")] = 0.49
    mo_limit = simulation.calculate("mo_mhf_parent_income_limit", year)
    for index, state in enumerate(states):
        if state == "MO":
            expected[index] = mo_limit[index]
    if parameters.gov.states.fl.dcf.medicaid.parent.in_effect:
        # Florida's dollar-standard route replaces the national ratio while
        # its indicator is on; the people here have no children, so Texas's
        # one-parent route never applies.
        fl_limit = simulation.calculate("fl_medicaid_parent_income_limit", year)
        expected[states.index("FL")] = fl_limit[states.index("FL")]
    if not historical:
        # Read the unchanged July 2025 schedule independently of compatibility entries.
        va = simulation.tax_benefit_system.parameters(
            "2025-07-01"
        ).gov.states.va.dmas.medicaid.lifc.income_limit
        capped_size = min(size, va.max_household_size)
        guideline = (
            parameters.gov.hhs.fpg.first_person["CONTIGUOUS_US"]
            + (size - 1) * parameters.gov.hhs.fpg.additional_person["CONTIGUOUS_US"]
        )
        indices = (states.index("VA"), len(states), len(states) + 1)
        direct_expected = []
        for index, group in zip(indices, ("group2", "group1", "group3")):
            table = getattr(va, group)
            annual = (
                table.main[str(capped_size)]
                + max(size - capped_size, 0) * table.additional
            )
            direct_expected.append(annual / guideline)
            if year >= 2026:
                expected[index] = annual / guideline
        np.testing.assert_allclose(
            simulation.calculate("va_medicaid_lifc_income_limit", year)[list(indices)],
            direct_expected,
            rtol=1e-6,
        )
    np.testing.assert_allclose(
        simulation.calculate("medicaid_parent_income_limit", year), expected, rtol=1e-6
    )

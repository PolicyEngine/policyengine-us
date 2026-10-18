"""Property tests: Kentucky's dependent care credit is 20% of the federal
section 21 credit under Kentucky's conformed Internal Revenue Code.

KRS 141.067: "The credit shall be twenty percent (20%) of the federal credit
allowed under Section 21 of the Internal Revenue Code." KRS 141.010(21) fixes
that Code at a reference date: December 31, 2024 for 2025 (2025 Ky. Acts ch.
98, sec. 30) and December 31, 2025 from 2026 (2026 Ky. Acts ch. 161, sec. 6).
The One Big Beautiful Bill Act, enacted July 4, 2025, amended section 21 for
tax years beginning after 2025, so Kentucky adopts that change from 2026.

For each Kentucky tax unit, with C the federal credit allowed (cdcc, after the
IRC 26 liability cap), P the same credit on the pre-OBBBA rate schedule
(pre_obbba_cdcc), K = ky_cdcc_potential and k = ky_cdcc:

1. K = 0.2 * C in 2025, 2026 and 2027. Before 2026 Kentucky's Code predates
   the Act, but the Act does not change section 21 for those years.
2. In years the Act does not change section 21 (2021 and 2025 here, including
   the refundable 2021 credit), each pre-OBBBA mirror equals its live variable.
3. From 2026, C >= P: the Act's rate is at least the pre-OBBBA rate at every
   AGI, so adopting it never lowers Kentucky's credit.
4. The federal potential credit equals a reference written from IRC 21(a)(2)
   (and, from 2026, the Act's amended schedule) times the relevant expenses.
5. 0 <= k <= K.
6. Under a reform that turns Kentucky's OBBBA conformity off, K = 0.2 * P
   from 2026, and K is unchanged in 2025 (checked on the grid only, since the
   reformed system costs about 0.55 GiB and 7 seconds to build).
7. The OBBBA marker that the pre-OBBBA mirrors read switches on in exactly the
   years the live rate schedule departs from the frozen pre-OBBBA one.

Each Simulation holds every year at once, so a batch costs one Simulation.
The model computes in single precision, so comparisons allow one cent or eight
float32 spacings at the largest amount, whichever is larger.
"""

from math import ceil

import numpy as np
import pytest
from policyengine_core.reforms import Reform

from policyengine_us import CountryTaxBenefitSystem, Simulation

hypothesis = pytest.importorskip("hypothesis")
st = pytest.importorskip("hypothesis.strategies")

MATCH = 0.2
CONFORMITY = "gov.states.ky.tax.income.irc_conformity.obbba"
YEARS = [2021, 2025, 2026, 2027]
MATCH_YEARS = [2025, 2026, 2027]
NO_OBBBA_CHANGE_YEARS = [2021, 2025]
OBBBA_YEARS = [2026, 2027]
REFORM_YEARS = [2025, 2026, 2027]

OUTPUTS = [
    "adjusted_gross_income",
    "cdcc_filing_status_eligible",
    "cdcc_relevant_expenses",
    "cdcc_potential",
    "cdcc",
    "capped_cdcc",
    "pre_obbba_cdcc_potential",
    "pre_obbba_cdcc",
    "pre_obbba_capped_cdcc",
    "ky_cdcc_potential",
    "ky_cdcc",
]
PAIRS = [
    ("pre_obbba_cdcc_potential", "cdcc_potential"),
    ("pre_obbba_cdcc", "cdcc"),
    ("pre_obbba_capped_cdcc", "capped_cdcc"),
]


@pytest.fixture(scope="module")
def decoupled_system():
    # Built once for the module and released at its end, so the reformed
    # parameter tree does not stay resident for the rest of the test process.
    reform = Reform.from_dict({CONFORMITY: {"2018-01-01.2100-12-31": False}}, "us")
    yield CountryTaxBenefitSystem(reform=reform)


def tolerance(*amounts):
    scale = np.float32(max(np.max(np.abs(a)) for a in amounts))
    return max(0.01, 8 * float(np.spacing(scale)))


def situation(units, years):
    """One Kentucky tax unit per household: a head, a spouse if married, and
    children of the given ages, with the same inputs in every year."""
    people, tax_units, households = {}, {}, {}

    def each_year(value):
        return {year: value for year in years}

    for i, unit in enumerate(units):
        head = f"head{i}"
        members = [head]
        people[head] = {
            "age": each_year(35),
            "employment_income": each_year(unit["wages"]),
        }
        if unit["married"]:
            spouse = f"spouse{i}"
            members.append(spouse)
            people[spouse] = {
                "age": each_year(35),
                "employment_income": each_year(unit["spouse_wages"]),
            }
        for j, age in enumerate(unit["child_ages"]):
            child = f"child{i}_{j}"
            members.append(child)
            people[child] = {"age": each_year(age)}
        tax_units[f"t{i}"] = {
            "members": members,
            "tax_unit_childcare_expenses": each_year(unit["expenses"]),
            "premium_tax_credit": each_year(0),
        }
        households[f"h{i}"] = {"members": members, "state_code": each_year("KY")}
    return {"people": people, "tax_units": tax_units, "households": households}


def calculate(units, years, outputs, **system):
    sim = Simulation(situation=situation(units, years), **system)
    return {
        year: {name: sim.calculate(name, year) for name in outputs} for year in years
    }


def reference_rate(agi, joint, year):
    """IRC 21(a)(2): 35% less one point per $2,000 (or part) of AGI over
    $15,000, floored at 20%. From 2026 the Act raises that to 50% floored at
    35%, then subtracts one point per $2,000 ($4,000 joint) of AGI over
    $75,000 ($150,000 joint), floored at 20%."""
    first = ceil(max(0, agi - 15_000) / 2_000) / 100
    if year < 2026:
        return max(0.20, 0.35 - first)
    start, step = (150_000, 4_000) if joint else (75_000, 2_000)
    second = ceil(max(0, agi - start) / step) / 100
    return max(0.20, max(0.35, 0.50 - first) - second)


def check(units):
    result = calculate(units, YEARS, OUTPUTS)
    for year in YEARS:
        r = result[year]
        tol = tolerance(r["cdcc_potential"], r["pre_obbba_cdcc_potential"])
        k, big_k = r["ky_cdcc"], r["ky_cdcc_potential"]
        c, p = r["cdcc"], r["pre_obbba_cdcc"]
        # 1. Kentucky matches 20% of the live federal credit allowed.
        if year in MATCH_YEARS:
            np.testing.assert_allclose(big_k, MATCH * c, atol=tol)
        # 2. The pre-OBBBA mirrors equal the live credits where the Act does
        # not change section 21.
        if year in NO_OBBBA_CHANGE_YEARS:
            for mirror, live in PAIRS:
                np.testing.assert_allclose(r[mirror], r[live], atol=tol)
        # 3. The Act never lowers the federal credit, before or after the cap.
        if year in OBBBA_YEARS:
            assert (c >= p - tol).all()
            assert (r["cdcc_potential"] >= r["pre_obbba_cdcc_potential"] - tol).all()
        # 4. The potential credit follows the statute's rate schedule. 2021's
        # American Rescue Plan Act schedule is outside this reference.
        if year != 2021:
            joint = np.array([u["married"] for u in units])
            rate = np.array(
                [
                    reference_rate(float(agi), married, year)
                    for agi, married in zip(r["adjusted_gross_income"], joint)
                ]
            )
            expected = (
                r["cdcc_filing_status_eligible"] * r["cdcc_relevant_expenses"] * rate
            )
            np.testing.assert_allclose(r["cdcc_potential"], expected, atol=tol)
        # 5. The liability-limited credit never exceeds its potential.
        assert (k >= -tol).all()
        assert (k <= big_k + tol).all()
    return result


def check_decoupled(units, baseline, system):
    # 6. With Kentucky's OBBBA conformity off, Kentucky reads the pre-OBBBA
    # credit once the Act changes section 21, and nothing changes before.
    decoupled = calculate(
        units, REFORM_YEARS, ["ky_cdcc_potential"], tax_benefit_system=system
    )
    for year in REFORM_YEARS:
        r = baseline[year]
        tol = tolerance(r["cdcc_potential"])
        big_k = decoupled[year]["ky_cdcc_potential"]
        if year in OBBBA_YEARS:
            np.testing.assert_allclose(big_k, MATCH * r["pre_obbba_cdcc"], atol=tol)
            # Conforming never lowers Kentucky's credit.
            assert (r["ky_cdcc_potential"] >= big_k - tol).all()
        else:
            np.testing.assert_allclose(big_k, r["ky_cdcc_potential"], atol=tol)


def unit(married, wages, spouse_wages, child_ages, expenses):
    return {
        "married": married,
        "wages": wages,
        "spouse_wages": spouse_wages,
        "child_ages": child_ages,
        "expenses": expenses,
    }


# Boundaries of both phase-downs, either side of each, the cap on expenses,
# a non-qualifying 13-year-old, no expenses, and a unit whose federal credit
# is cut by liability.
GRID = [
    # Unmarried: first phase-down from $15,000, second from $75,000.
    unit(False, 15_000, 0, [4], 3_000),
    unit(False, 15_001, 0, [4], 3_000),
    unit(False, 50_000, 0, [5], 1_000),
    unit(False, 75_000, 0, [2, 9], 8_000),
    unit(False, 75_001, 0, [2, 9], 8_000),
    unit(False, 103_000, 0, [2, 9], 6_000),
    unit(False, 103_001, 0, [2, 9], 6_000),
    unit(False, 60_000, 0, [13], 4_000),
    unit(False, 40_000, 0, [3], 0),
    # Married filing jointly: second phase-down from $150,000 by $4,000.
    unit(True, 25_000, 25_000, [5, 7], 6_000),
    unit(True, 75_000, 75_000, [1, 4, 6], 9_000),
    unit(True, 75_000, 75_001, [1, 4, 6], 9_000),
    unit(True, 80_000, 80_000, [3, 6], 6_000),
    unit(True, 105_000, 105_000, [3, 6], 6_000),
    unit(True, 105_000, 105_001, [3, 6], 6_000),
    # Lower earner's income limits the expenses (IRC 21(d)(1)).
    unit(True, 90_000, 1_500, [3], 3_000),
]


def test_grid_matches_20_percent_of_federal_credit(decoupled_system):
    result = check(GRID)
    check_decoupled(GRID, result, decoupled_system)
    # The grid has 2026 units where the Act raises the credit, units where
    # both schedules give the same positive credit, and units whose federal
    # credit the liability cap cuts.
    r = result[2026]
    differs = r["cdcc"] > r["pre_obbba_cdcc"] + 0.01
    same = np.isclose(r["cdcc"], r["pre_obbba_cdcc"])
    capped = r["cdcc"] < r["cdcc_potential"] - 0.01
    assert differs.any() and (same & (r["cdcc"] > 0)).any() and capped.any()


def test_obbba_marker_matches_rate_schedule():
    # 7. The mirrors read amended_structure.applies as the years the Act
    # changes section 21. It must switch on with the Act's rate changes.
    from policyengine_us.system import system

    parameters = system.parameters
    frozen = parameters.gov.irs.credits.cdcc("2025-01-01").phase_out
    for year in range(2022, 2036):
        live = parameters.gov.irs.credits.cdcc(f"{year}-01-01").phase_out
        departs = (live.max, live.min) != (frozen.max, frozen.min)
        assert bool(live.amended_structure.applies) == departs, year


unit_strategy = st.builds(
    unit,
    st.booleans(),
    st.one_of(st.just(0), st.integers(1, 260_000)),
    st.one_of(st.just(0), st.integers(1, 160_000)),
    st.lists(st.integers(0, 14), max_size=3),
    st.one_of(st.just(0), st.integers(1, 12_000)),
)


@hypothesis.settings(
    max_examples=10,
    deadline=None,
    suppress_health_check=[
        hypothesis.HealthCheck.too_slow,
        hypothesis.HealthCheck.data_too_large,
    ],
)
@hypothesis.given(st.lists(unit_strategy, min_size=1, max_size=20))
def test_random_units_match_20_percent_of_federal_credit(units):
    check(units)

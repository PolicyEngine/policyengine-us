"""Invariants of Idaho's retirement benefits deduction on military retired pay.

Idaho Code 63-3022A(1)(b), as amended by 2025 House Bills 40 and 479 with
effect from January 1, 2025, counts retirement benefits the United States pays
to a retired member of the military services, or to the member's unremarried
widow or widower, who:

  (i) is classified as disabled;
  (ii) has attained the age of 62 by the end of the tax year; or
  (iii) was employed during the tax year and received sufficient income from
        such employment to be required to file a federal return under
        26 U.S.C. 6012(a)(1).

Before 2025 the benefits had the age test of 63-3022A(1)(a): age 65, or age 62
and classified as disabled. In every year they share the deduction's cap,
63-3022A(2) ($48,216 single and $72,324 joint for 2025, Form 39R line 8a, and
nothing on a separate return), which the Social Security and Railroad
Retirement benefits of the taxpayer and spouse reduce, 63-3022A(3).

The reference rules below restate the law from published amounts, not from
the model's parameters. `test_grid` runs one simulation over 2024 to 2026 for
every filing status; ages on both sides of 62 and 65; disability and
blindness; wages or business profit a dollar under, at and over each year's
filing threshold; and military retired pay, Social Security and a public
pension:

1. Differential: on a return whose only gross income is the retiree's wages
   or business profit, the employment test holds exactly when
   tax_unit_is_required_to_file does and the retiree has such income, in
   2025 and 2026. Both also match the published thresholds: section 6012(f)
   for 2025 (more than the standard deduction, which adds amounts for age and
   blindness) and section 6012(a)(1)(A) and (B) for 2026 (at least the basic
   standard deduction plus amounts for age alone).
2. Eligibility: military retired pay counts for exactly the people the
   statute's tests admit, restated here, in every year.
3. Cap and offset: in 2025 the deduction equals the lesser of the counted
   benefits and the published cap less the head's and spouse's Social
   Security benefits, and never falls below zero.
4. Monotonicity: more military retired pay never lowers the deduction and
   never raises it by more than the added pay. For a recipient the tests
   don't admit, it doesn't change the deduction.

`test_drawn_units` checks properties 2 to 4 on batches of units Hypothesis
draws, with any mix of these inputs and business losses.
"""

from itertools import product

import numpy as np
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation

YEARS = (2024, 2025, 2026)
STATUSES = ("SINGLE", "HEAD_OF_HOUSEHOLD", "SURVIVING_SPOUSE", "SEPARATE", "JOINT")
UNMARRIED = ("SINGLE", "HEAD_OF_HOUSEHOLD")

# Basic standard deduction and the additional standard deduction for each of
# age 65 and blindness. 2025: Chart A of the 2025 Form 1040 instructions,
# https://www.irs.gov/pub/irs-prior/i1040gi--2025.pdf. 2026: Rev. Proc.
# 2025-32, sec. 4.14, https://www.irs.gov/pub/irs-drop/rp-25-32.pdf#page=18
BASIC = {
    2025: {
        "SINGLE": 15_750,
        "HEAD_OF_HOUSEHOLD": 23_625,
        "SURVIVING_SPOUSE": 31_500,
        "SEPARATE": 15_750,
        "JOINT": 31_500,
    },
    2026: {
        "SINGLE": 16_100,
        "HEAD_OF_HOUSEHOLD": 24_150,
        "SURVIVING_SPOUSE": 32_200,
        "SEPARATE": 16_100,
        "JOINT": 32_200,
    },
}
ADDITIONAL = {
    2025: {status: 2_000 if status in UNMARRIED else 1_600 for status in STATUSES},
    2026: {status: 2_050 if status in UNMARRIED else 1_650 for status in STATUSES},
}
# Form 39R line 8a for 2025: $48,216 single, $72,324 joint. 63-3022A(2)(b)
# and (c) give unmarried taxpayers and unremarried widows and widowers the
# single amount; (2)(e) gives a married taxpayer filing separately nothing.
# https://tax.idaho.gov/wp-content/uploads/forms/EIN00046/EIN00046_03-02-2026.pdf#page=45
CAP_2025 = {
    "SINGLE": 48_216,
    "HEAD_OF_HOUSEHOLD": 48_216,
    "SURVIVING_SPOUSE": 48_216,
    "SEPARATE": 0,
    "JOINT": 72_324,
}


def employment_test(year, status, income, aged_count, blind_count):
    """63-3022A(1)(b)(iii) with the published filing thresholds."""
    if year < 2025 or income <= 0:
        return False
    if status == "SEPARATE":
        # Any gross income requires a separate return, in both years.
        return True
    if year == 2025:
        # Section 6012(f): gross income over the standard deduction.
        threshold = BASIC[year][status] + ADDITIONAL[year][status] * (
            aged_count + blind_count
        )
        return income > threshold
    # Section 6012(a)(1)(A) and (B): blindness doesn't raise the threshold.
    threshold = BASIC[year][status] + ADDITIONAL[year][status] * aged_count
    return income >= threshold


def general_age_test(age, disabled):
    """63-3022A(1)(a): age 65, or age 62 and classified as disabled."""
    return age >= 65 or (disabled and age >= 62)


def military_test(year, age, disabled, employed):
    """Whether military retired pay counts toward the deduction."""
    if year < 2025:
        return general_age_test(age, disabled)
    return disabled or age >= 62 or employed


def simulate(units):
    """One simulation of independent Idaho tax units.

    Each unit is {"filing_status": name, "adults": [inputs, ...]}; the first
    adult is the retiree. Inputs are the same in every year.
    """
    people, tax_units, households = {}, {}, {}
    groups = {"marital_units": {}, "spm_units": {}, "families": {}}
    for index, unit in enumerate(units):
        members = [f"adult_{index}_{n}" for n in range(len(unit["adults"]))]
        for name, inputs in zip(members, unit["adults"]):
            people[name] = {
                variable: {year: value for year in YEARS}
                for variable, value in inputs.items()
            }
        tax_units[f"tax_unit_{index}"] = {
            "members": members,
            "filing_status": {year: unit["filing_status"] for year in YEARS},
        }
        households[f"household_{index}"] = {
            "members": members,
            "state_code": {year: "ID" for year in YEARS},
        }
        for name in ("marital_units", "spm_units", "families"):
            groups[name][f"{name}_{index}"] = {"members": members}
    return Simulation(
        situation={
            "people": people,
            "tax_units": tax_units,
            "households": households,
            **groups,
        }
    )


def adult(age, disabled=False, blind=False, wages=0, profit=0, military=0, ss=0):
    return {
        "age": age,
        "is_disabled": disabled,
        "is_blind": blind,
        "employment_income": wages,
        "self_employment_income": profit,
        "military_retirement_pay": military,
        "social_security_retirement": ss,
    }


def unit(status, retiree, spouse_age=None, pension=0):
    adults = [dict(retiree, public_pension_income=pension)]
    if status == "JOINT":
        adults.append(adult(spouse_age))
    return {"filing_status": status, "adults": adults}


def first_rows(units):
    sizes = [len(u["adults"]) for u in units]
    return np.cumsum([0] + sizes[:-1])


def results(simulation, units, year):
    """Person results for the retiree, or every adult, and tax unit results."""
    rows = first_rows(units)

    def calculate(variable):
        return np.asarray(simulation.calculate(variable, year))

    relevant = calculate("id_retirement_benefits_deduction_relevant_income")
    return {
        "employment": calculate(
            "id_retirement_benefits_deduction_military_employment_eligible"
        )[rows],
        "military": calculate(
            "id_retirement_benefits_deduction_military_eligible_person"
        ),
        "relevant": np.add.reduceat(relevant, rows),
        "deduction": calculate("id_retirement_benefits_deduction"),
        "required": calculate("tax_unit_is_required_to_file"),
    }


def reference_counted(year, u, employed):
    """Benefits the statute counts toward the deduction, restated."""
    retiree = u["adults"][0]
    counted = 0
    if military_test(year, retiree["age"], retiree["is_disabled"], employed):
        counted += retiree["military_retirement_pay"]
    if general_age_test(retiree["age"], retiree["is_disabled"]):
        counted += retiree["public_pension_income"]
    return counted


def unit_employment_reference(year, u):
    retiree = u["adults"][0]
    income = max(retiree["employment_income"], 0) + max(
        retiree["self_employment_income"], 0
    )
    aged = sum(a["age"] >= 65 for a in u["adults"])
    blind = sum(a["is_blind"] for a in u["adults"])
    return employment_test(year, u["filing_status"], income, aged, blind)


def check_units(simulation, units, check_cap=True):
    """Properties 2 to 4 for every unit and year."""
    rows = first_rows(units)
    for year in YEARS:
        r = results(simulation, units, year)
        employed = [unit_employment_reference(year, u) for u in units]
        np.testing.assert_array_equal(r["employment"], employed, err_msg=str(year))
        # Property 2, for every adult: the spouse has no income of their own.
        expected_military = []
        for u, e in zip(units, employed):
            for n, a in enumerate(u["adults"]):
                own_employment = e if n == 0 else False
                expected_military.append(
                    military_test(year, a["age"], a["is_disabled"], own_employment)
                )
        np.testing.assert_array_equal(
            r["military"], expected_military, err_msg=str(year)
        )
        counted = np.array(
            [reference_counted(year, u, e) for u, e in zip(units, employed)]
        )
        np.testing.assert_allclose(r["relevant"], counted, err_msg=str(year))
        assert (r["deduction"] >= 0).all()
        assert (r["deduction"] <= counted + 1e-6).all()
        if year == 2025 and check_cap:
            ss = np.array(
                [
                    sum(a["social_security_retirement"] for a in u["adults"])
                    for u in units
                ]
            )
            cap = np.array([CAP_2025[u["filing_status"]] for u in units])
            expected = np.minimum(counted, np.maximum(cap - ss, 0))
            np.testing.assert_allclose(r["deduction"], expected, err_msg="2025 cap")
    return rows


AGES = (45, 61, 62, 64, 65, 67)
MILITARY = (0, 30_000, 60_000)


def grid_units():
    """Units for properties 2 to 4, in groups that differ only in military pay."""
    units, groups = [], []
    shapes = product(
        STATUSES, AGES, (False, True), (0, 10_000, 60_000), (0, 20_000), (0, 20_000)
    )
    for status, age, disabled, wages, ss, pension in shapes:
        group = []
        for military in MILITARY:
            retiree = adult(
                age, disabled=disabled, wages=wages, military=military, ss=ss
            )
            group.append(len(units))
            units.append(unit(status, retiree, spouse_age=43, pension=pension))
        groups.append(group)
    return units, groups


def differential_units():
    """Returns whose only gross income is the retiree's wages or profit."""
    units = []
    for status, age, spouse_age, blind, kind in product(
        STATUSES, (45, 61), (43, 66), (False, True), ("wages", "profit")
    ):
        if status != "JOINT" and spouse_age == 66:
            continue
        aged = int(status == "JOINT" and spouse_age >= 65)
        amounts = {0, 1}
        for year in (2025, 2026):
            threshold = BASIC[year][status] + ADDITIONAL[year][status] * (
                aged + (blind if year == 2025 else 0)
            )
            amounts |= {threshold - 1, threshold, threshold + 1}
        for amount in sorted(amounts):
            retiree = adult(age, blind=blind, **{kind: amount})
            units.append(unit(status, retiree, spouse_age=spouse_age))
    return units


def test_grid():
    grid, groups = grid_units()
    differential = differential_units()
    units = grid + differential
    simulation = simulate(units)
    check_units(simulation, units)

    # Property 1, on the returns with only employment income.
    offset = len(grid)
    for year in (2025, 2026):
        r = results(simulation, units, year)
        for i, u in enumerate(differential):
            retiree = u["adults"][0]
            income = retiree["employment_income"] + retiree["self_employment_income"]
            required = bool(r["required"][offset + i]) and income > 0
            assert bool(r["employment"][offset + i]) == required, (year, u)
            assert required == unit_employment_reference(year, u), (year, u)

    # Property 4, across each group's military pay.
    for year in YEARS:
        r = results(simulation, units, year)
        employed = [unit_employment_reference(year, u) for u in units]
        for group in groups:
            deductions = r["deduction"][group]
            pay = np.array(MILITARY)
            assert (np.diff(deductions) >= -1e-6).all(), (year, units[group[0]])
            assert (np.diff(deductions) <= np.diff(pay) + 1e-6).all()
            retiree = units[group[0]]["adults"][0]
            if not military_test(
                year, retiree["age"], retiree["is_disabled"], employed[group[0]]
            ):
                assert np.ptp(deductions) == 0, (year, units[group[0]])


@st.composite
def drawn_unit(draw):
    status = draw(st.sampled_from(STATUSES))
    retiree = adult(
        draw(st.integers(30, 90)),
        disabled=draw(st.booleans()),
        blind=draw(st.booleans()),
        wages=draw(st.sampled_from([0, 5_000, 16_100, 32_200, 33_850, 90_000])),
        profit=draw(st.integers(-20_000, 60_000)),
        military=draw(st.integers(0, 90_000)),
        ss=draw(st.sampled_from([0, 12_000, 30_000, 80_000])),
    )
    spouse_age = draw(st.integers(30, 90))
    pension = draw(st.sampled_from([0, 20_000]))
    military_extra = draw(st.integers(1, 40_000))
    base = unit(status, retiree, spouse_age=spouse_age, pension=pension)
    more = unit(
        status,
        dict(
            retiree,
            military_retirement_pay=retiree["military_retirement_pay"] + military_extra,
        ),
        spouse_age=spouse_age,
        pension=pension,
    )
    return base, more, military_extra


@settings(
    max_examples=5,
    deadline=None,
    derandomize=True,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large],
)
@given(drawn=st.lists(drawn_unit(), min_size=8, max_size=20))
def test_drawn_units(drawn):
    units = [u for base, more, _ in drawn for u in (base, more)]
    simulation = simulate(units)
    check_units(simulation, units)
    for year in YEARS:
        deductions = results(simulation, units, year)["deduction"]
        for i, (base, _, extra) in enumerate(drawn):
            low, high = deductions[2 * i], deductions[2 * i + 1]
            assert low - 1e-6 <= high <= low + extra + 1e-6, (year, base)

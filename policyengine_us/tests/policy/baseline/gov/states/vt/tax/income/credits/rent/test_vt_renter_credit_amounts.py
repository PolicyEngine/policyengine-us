"""Check Vermont's renter credit against the Department of Taxes' credit tables.

32 V.S.A. § 6066(b)(1) bases the renter credit on 10% of fair market rent, which
§ 6061(7)(C) defines as HUD's fair market rent for the claimant's area, or for
Franklin and Grand Isle the average of the fair market rents for the State. The
department publishes the whole-dollar credit amounts by county and household
size in each year's Renter Credit Website Calculator ("Base Credit Amounts"
sheet; the 2021-2023 renter credit reports print the same tables), and its
calculator applies the income phase-out to that whole-dollar amount:
ROUND(Base_Rebate_Amount * Percent_Rebate_Claimable, 0).

The tests compute vt_renter_credit for every county, household size 1-8 and
year 2021-2025 (12 months rented, not shared, not subsidized) and check:
- below the extremely low-income limit, the credit equals the table;
- at every other income, the credit equals the department's formula applied
  to the table, and it never rises with income.

PE rounds the final credit half to even and the department half up, so the
few incomes where the phased-out amount ends in exactly 50 cents are left out.
"""

from fractions import Fraction

import numpy as np
import pytest

from policyengine_us import Simulation
from policyengine_us.system import system

# Hypothesis is a dev extra; skip rather than fail collection without it.
hypothesis = pytest.importorskip("hypothesis")
st = pytest.importorskip("hypothesis.strategies")

YEARS = range(2021, 2026)
SIZES = range(1, 9)
LIMITS = system.parameters.gov.states.vt.tax.income.credits.renter.income_limit_ami

# Department credit amounts for household sizes 1-4; sizes 5-8 repeat size 4.
# 2021: 2021 Renter Credit Website Calculator (_8); 2022: 2022 calculator (_1);
# 2023-2025: each year's calculator. Read from the workbooks, not retyped.
DEPARTMENT_CREDIT_AMOUNTS = {
    2021: {
        "ADDISON_COUNTY_VT": (1_015, 1_270, 1_586, 1_722),
        "BENNINGTON_COUNTY_VT": (983, 1_128, 1_524, 1_530),
        "CALEDONIA_COUNTY_VT": (887, 1_010, 1_256, 1_717),
        "CHITTENDEN_COUNTY_VT": (1_518, 1_954, 2_430, 2_500),
        "ESSEX_COUNTY_VT": (700, 889, 1_182, 1_231),
        "FRANKLIN_COUNTY_VT": (972, 1_200, 1_549, 1_703),
        "GRAND_ISLE_COUNTY_VT": (972, 1_200, 1_549, 1_703),
        "LAMOILLE_COUNTY_VT": (952, 1_219, 1_517, 1_654),
        "ORANGE_COUNTY_VT": (894, 1_178, 1_500, 1_622),
        "ORLEANS_COUNTY_VT": (826, 941, 1_279, 1_466),
        "RUTLAND_COUNTY_VT": (935, 1_102, 1_502, 1_654),
        "WASHINGTON_COUNTY_VT": (989, 1_303, 1_630, 1_838),
        "WINDHAM_COUNTY_VT": (958, 1_192, 1_482, 1_616),
        "WINDSOR_COUNTY_VT": (1_004, 1_208, 1_699, 1_729),
    },
    2022: {
        "ADDISON_COUNTY_VT": (1_054, 1_340, 1_715, 1_818),
        "BENNINGTON_COUNTY_VT": (986, 1_222, 1_604, 1_656),
        "CALEDONIA_COUNTY_VT": (924, 1_052, 1_301, 1_801),
        "CHITTENDEN_COUNTY_VT": (1_396, 1_800, 2_225, 2_441),
        "ESSEX_COUNTY_VT": (785, 937, 1_238, 1_302),
        "FRANKLIN_COUNTY_VT": (1_006, 1_242, 1_602, 1_773),
        "GRAND_ISLE_COUNTY_VT": (1_006, 1_242, 1_602, 1_773),
        "LAMOILLE_COUNTY_VT": (967, 1_273, 1_612, 1_727),
        "ORANGE_COUNTY_VT": (952, 1_252, 1_565, 1_723),
        "ORLEANS_COUNTY_VT": (896, 1_021, 1_358, 1_493),
        "RUTLAND_COUNTY_VT": (1_001, 1_177, 1_613, 1_944),
        "WASHINGTON_COUNTY_VT": (1_043, 1_373, 1_745, 1_861),
        "WINDHAM_COUNTY_VT": (1_048, 1_307, 1_615, 1_772),
        "WINDSOR_COUNTY_VT": (1_069, 1_253, 1_745, 1_788),
    },
    2023: {
        "ADDISON_COUNTY_VT": (1_136, 1_430, 1_859, 1_921),
        "BENNINGTON_COUNTY_VT": (1_063, 1_344, 1_746, 1_894),
        "CALEDONIA_COUNTY_VT": (1_014, 1_145, 1_400, 1_950),
        "CHITTENDEN_COUNTY_VT": (1_486, 1_938, 2_378, 2_500),
        "ESSEX_COUNTY_VT": (895, 1_012, 1_372, 1_403),
        "FRANKLIN_COUNTY_VT": (1_103, 1_358, 1_749, 1_904),
        "GRAND_ISLE_COUNTY_VT": (1_103, 1_358, 1_749, 1_904),
        "LAMOILLE_COUNTY_VT": (1_056, 1_390, 1_853, 1_867),
        "ORANGE_COUNTY_VT": (1_028, 1_350, 1_712, 1_813),
        "ORLEANS_COUNTY_VT": (1_013, 1_144, 1_489, 1_582),
        "RUTLAND_COUNTY_VT": (1_093, 1_306, 1_728, 2_190),
        "WASHINGTON_COUNTY_VT": (1_144, 1_506, 1_901, 2_028),
        "WINDHAM_COUNTY_VT": (1_134, 1_380, 1_711, 1_854),
        "WINDSOR_COUNTY_VT": (1_178, 1_355, 1_843, 1_850),
    },
    2024: {
        "ADDISON_COUNTY_VT": (1_274, 1_598, 2_089, 2_129),
        "BENNINGTON_COUNTY_VT": (1_207, 1_489, 1_970, 2_315),
        "CALEDONIA_COUNTY_VT": (1_106, 1_282, 1_668, 1_988),
        "CHITTENDEN_COUNTY_VT": (1_729, 2_264, 2_500, 2_500),
        "ESSEX_COUNTY_VT": (1_001, 1_123, 1_561, 1_583),
        "FRANKLIN_COUNTY_VT": (1_254, 1_540, 1_996, 2_160),
        "GRAND_ISLE_COUNTY_VT": (1_254, 1_540, 1_996, 2_160),
        "LAMOILLE_COUNTY_VT": (1_180, 1_549, 2_056, 2_063),
        "ORANGE_COUNTY_VT": (1_204, 1_493, 1_921, 2_005),
        "ORLEANS_COUNTY_VT": (1_156, 1_297, 1_681, 1_829),
        "RUTLAND_COUNTY_VT": (1_196, 1_469, 1_873, 2_405),
        "WASHINGTON_COUNTY_VT": (1_327, 1_744, 2_198, 2_370),
        "WINDHAM_COUNTY_VT": (1_309, 1_608, 1_986, 2_142),
        "WINDSOR_COUNTY_VT": (1_363, 1_560, 2_070, 2_077),
    },
    2025: {
        "ADDISON_COUNTY_VT": (1_324, 1_692, 2_112, 2_394),
        "BENNINGTON_COUNTY_VT": (1_283, 1_470, 2_051, 2_383),
        "CALEDONIA_COUNTY_VT": (1_091, 1_310, 1_765, 1_873),
        "CHITTENDEN_COUNTY_VT": (1_771, 2_323, 2_500, 2_500),
        "ESSEX_COUNTY_VT": (1_025, 1_135, 1_591, 1_621),
        "FRANKLIN_COUNTY_VT": (1_269, 1_558, 2_025, 2_195),
        "GRAND_ISLE_COUNTY_VT": (1_269, 1_558, 2_025, 2_195),
        "LAMOILLE_COUNTY_VT": (1_169, 1_534, 2_064, 2_071),
        "ORANGE_COUNTY_VT": (1_241, 1_511, 1_976, 2_072),
        "ORLEANS_COUNTY_VT": (1_146, 1_319, 1_717, 1_894),
        "RUTLAND_COUNTY_VT": (1_198, 1_508, 1_861, 2_330),
        "WASHINGTON_COUNTY_VT": (1_298, 1_703, 2_116, 2_372),
        "WINDHAM_COUNTY_VT": (1_334, 1_625, 2_022, 2_154),
        "WINDSOR_COUNTY_VT": (1_352, 1_561, 2_030, 2_088),
    },
}
COUNTIES = sorted(DEPARTMENT_CREDIT_AMOUNTS[2025])


def _department_amount(year, county, size):
    return DEPARTMENT_CREDIT_AMOUNTS[year][county][min(size, 4) - 1]


def _limits(year, county, size):
    instant = f"{year}-01-01"
    full = LIMITS.thirty_percent.children[str(size)].children[county](instant)
    partial = LIMITS.fifty_percent.children[str(size)].children[county](instant)
    return int(full), int(partial)


def _department_credit(amount, income, full, partial):
    """The calculator's credit, in exact arithmetic, before its final ROUND."""
    if income > partial:
        return Fraction(0)
    if income <= full:
        return Fraction(amount)
    return Fraction(amount) * Fraction(partial - income, partial - full)


def _calculate(year, households):
    """vt_renter_credit for single-person households given as
    (county, tax unit size, renter credit income)."""
    people, tax_units, spm_units, households_out = {}, {}, {}, {}
    for i, (county, size, income) in enumerate(households):
        people[f"person_{i}"] = {"age": {year: 40}, "rent": {year: 0}}
        tax_units[f"tax_unit_{i}"] = {
            "members": [f"person_{i}"],
            "tax_unit_size": {year: size},
            "vt_renter_credit_income": {year: income},
            "rent_is_shared_with_another_tax_unit": {year: False},
        }
        spm_units[f"spm_unit_{i}"] = {
            "members": [f"person_{i}"],
            "housing_assistance": {year: 0},
        }
        households_out[f"household_{i}"] = {
            "members": [f"person_{i}"],
            "state_code": {year: "VT"},
            "county": {year: county},
        }
    simulation = Simulation(
        situation={
            "people": people,
            "tax_units": tax_units,
            "spm_units": spm_units,
            "households": households_out,
        }
    )
    return np.asarray(simulation.calculate("vt_renter_credit", year))


def test_table_covers_every_county_size_and_year():
    assert sorted(DEPARTMENT_CREDIT_AMOUNTS) == list(YEARS)
    for year in YEARS:
        assert sorted(DEPARTMENT_CREDIT_AMOUNTS[year]) == COUNTIES
        assert len(COUNTIES) == 14
        # Franklin and Grand Isle share the state average.
        assert (
            DEPARTMENT_CREDIT_AMOUNTS[year]["FRANKLIN_COUNTY_VT"]
            == DEPARTMENT_CREDIT_AMOUNTS[year]["GRAND_ISLE_COUNTY_VT"]
        )


@pytest.mark.parametrize("year", YEARS)
def test_full_credit_equals_department_table(year):
    households = [(county, size, 0) for county in COUNTIES for size in SIZES]
    credits = _calculate(year, households)
    mismatches = [
        (county, size, credit, _department_amount(year, county, size))
        for (county, size, _), credit in zip(households, credits)
        if credit != _department_amount(year, county, size)
    ]
    assert mismatches == []


def _incomes(full, partial):
    """Both limits, a dollar either side, and 19 incomes in between. The $37
    offset keeps the inner incomes off simple fractions of the phase-out band,
    which would make many phased-out amounts end in exactly 50 cents."""
    step = Fraction(partial - full, 20)
    inside = [int(full + k * step) + 37 for k in range(1, 20)]
    return [full - 1, full, full + 1, *inside, partial - 1, partial, partial + 1]


@pytest.mark.parametrize("year", YEARS)
def test_partial_credit_follows_department_formula(year):
    households, expected = [], []
    ties = 0
    for county in COUNTIES:
        for size in SIZES:
            amount = _department_amount(year, county, size)
            full, partial = _limits(year, county, size)
            for income in _incomes(full, partial):
                credit = _department_credit(amount, income, full, partial)
                if credit - int(credit) == Fraction(1, 2):
                    ties += 1
                    continue
                households.append((county, size, income))
                expected.append(int(credit + Fraction(1, 2)))
    credits = _calculate(year, households)
    mismatches = [
        (household, credit, want)
        for household, credit, want in zip(households, credits, expected)
        if credit != want
    ]
    assert mismatches == []
    # Exact 50-cent ties are rare; a grid made mostly of them tests nothing.
    assert ties < len(households) // 100
    # The credit never rises with income for a given county and size.
    by_unit = {}
    for (county, size, income), credit in zip(households, credits):
        by_unit.setdefault((county, size), []).append((income, credit))
    for points in by_unit.values():
        amounts = [credit for _, credit in sorted(points)]
        assert all(a >= b for a, b in zip(amounts, amounts[1:]))


@hypothesis.settings(max_examples=20, deadline=None)
@hypothesis.given(
    year=st.sampled_from(list(YEARS)),
    draws=st.lists(
        st.tuples(
            st.sampled_from(COUNTIES),
            st.integers(min_value=1, max_value=8),
            st.floats(min_value=0, max_value=1.2),
        ),
        min_size=1,
        max_size=40,
    ),
)
def test_random_incomes_follow_department_formula(year, draws):
    households, expected = [], []
    for county, size, share in draws:
        full, partial = _limits(year, county, size)
        income = int(share * partial)
        credit = _department_credit(
            _department_amount(year, county, size), income, full, partial
        )
        if credit - int(credit) == Fraction(1, 2):
            continue
        households.append((county, size, income))
        expected.append(int(credit + Fraction(1, 2)))
    hypothesis.assume(households)
    assert list(_calculate(year, households)) == expected

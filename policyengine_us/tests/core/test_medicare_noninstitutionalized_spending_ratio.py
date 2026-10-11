"""The ratio that scales Medicare spending per enrollee to enrollees outside
nursing homes.

``calibration.gov.hhs.medicare.per_capita_cost`` averages Medicare spending
over every enrollee, including nursing home residents, whom the household
survey data do not sample. ``noninstitutionalized_spending_ratio`` is
spending per enrollee who is not a long-stay nursing home resident over
spending per enrollee, from MedPAC's 2022 fee-for-service Part A and B
spending ($31,200 for long-stay residents, about $11,300 for others; June
2025 report, chapter 5, file page 9) and the long-stay share of beneficiaries
(1.7 percent; October 2024 slides, file page 5):

    ratio = 1 / (1 + share x (long-stay spending / other spending - 1))

``medicare_gross_cost``, ``medicare_cost`` and ``qmb_cost_sharing`` multiply
``per_capita_cost`` by it; ``cbo_medicare_benefit`` multiplies spending less
the Part D low-income subsidy by it, then subtracts premium income per
enrollee.

Invariants:

1. Transcription: the stored value is the formula applied to MedPAC's
   published figures, rounded to three decimals.
2. Bounds and constancy: the ratio is strictly between 0 and 1 and is the
   same on every date from 2013, the first year of ``per_capita_cost``.
3. Sensitivity: the alternatives documented in the parameter file bracket
   the stored value: fee-for-service enrollment shares (62 percent of
   long-stay residents, 53 percent of others) give a lower ratio, and pricing
   Medicare Advantage at the CMS-HCC risk score ratio (2.12 / 1.01) gives a
   higher one.
4. Definition order: excluding every resident of a Medicare Current
   Beneficiary Survey long-term care facility, which includes assisted living,
   gives a lower ratio in every year of the published 2006-2013 tables
   (community-only over all-beneficiary benefit payments per capita), so the
   nursing home ratio is the smaller of the two corrections.
5. Consumers (Hypothesis, differential): for any year, any premiums and a
   ratio set by a reform (0.5, 0.8, 0.95 or 1), each consumer equals a
   reference implementation;
   gross spending is proportional to the ratio; ``medicare_cost`` and
   ``cbo_medicare_benefit`` lie in [0, ``medicare_gross_cost``] and never fall
   when the ratio rises; with the ratio at 1 every consumer reproduces the
   unscaled formulas. A person not enrolled gets zero.
"""

from functools import lru_cache

import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st
from policyengine_core.parameters.operations.get_parameter import get_parameter
from policyengine_core.reforms import Reform

from policyengine_us import Simulation
from policyengine_us.system import CountryTaxBenefitSystem, system

MEDICARE = "calibration.gov.hhs.medicare"
RATIO = f"{MEDICARE}.noninstitutionalized_spending_ratio"
FIRST_YEAR, END_YEAR = 2013, 2100

# MedPAC, June 2025 Report to the Congress, chapter 5 (file pages 8, 9 and
# 13), and October 2024 meeting slides (file page 5).
LONG_STAY_SPENDING, OTHER_SPENDING = 31_200, 11_300
LONG_STAY_SHARE = 0.017
LONG_STAY_FFS_SHARE, OTHER_FFS_SHARE = 0.62, 0.53
LONG_STAY_RISK_SCORE, OTHER_RISK_SCORE = 2.12, 1.01

# MCBS Characteristics and Perceptions of the Medicare Population, all
# beneficiaries: Table 1.1 beneficiaries (thousands) and Table 4.1 benefit
# payments ($ millions), total and community only.
MCBS = {
    2006: (43_867, 41_599, 305_066, 267_344),
    2007: (45_046, 42_867, 307_372, 271_509),
    2008: (46_100, 43_906, 320_032, 282_887),
    2009: (47_371, 45_053, 335_081, 289_843),
    2010: (48_454, 46_270, 365_098, 322_150),
    2011: (50_186, 47_969, 374_252, 330_907),
    2012: (51_723, 49_816, 338_395, 299_144),
    2013: (53_574, 51_568, 352_943, 312_626),
}


def _ratio(share, relative):
    return 1 / (1 + share * (relative - 1))


def _read(name, date):
    return get_parameter(system.parameters, name)(date)


def _stored(year):
    return _read(RATIO, f"{year}-01-01")


def test_value_is_the_medpac_formula():
    expected = _ratio(LONG_STAY_SHARE, LONG_STAY_SPENDING / OTHER_SPENDING)
    assert _stored(2022) == round(expected, 3) == 0.971


@given(st.integers(FIRST_YEAR, END_YEAR + 100), st.integers(1, 12))
def test_ratio_is_a_constant_share_below_one(year, month):
    value = _read(RATIO, f"{year}-{month:02d}-01")
    assert 0 < value < 1
    assert value == _stored(2022)


def test_documented_alternatives_bracket_the_value():
    relative = LONG_STAY_SPENDING / OTHER_SPENDING
    ffs_share = (
        LONG_STAY_SHARE
        * LONG_STAY_FFS_SHARE
        / (
            LONG_STAY_SHARE * LONG_STAY_FFS_SHARE
            + (1 - LONG_STAY_SHARE) * OTHER_FFS_SHARE
        )
    )
    ffs_ratio = _ratio(ffs_share, relative)
    # Price Medicare Advantage enrollees at the risk score ratio, with other
    # beneficiaries' spending the same in both programs.
    groups = {
        "long_stay_ffs": (LONG_STAY_SHARE * LONG_STAY_FFS_SHARE, relative),
        "long_stay_ma": (
            LONG_STAY_SHARE * (1 - LONG_STAY_FFS_SHARE),
            LONG_STAY_RISK_SCORE / OTHER_RISK_SCORE,
        ),
        "other": (1 - LONG_STAY_SHARE, 1),
    }
    average = sum(count * cost for count, cost in groups.values())
    mixed_ratio = 1 / average
    assert round(ffs_ratio, 3) == 0.966
    assert round(mixed_ratio, 3) == 0.975
    assert ffs_ratio < _stored(2022) < mixed_ratio


@pytest.mark.parametrize("year", MCBS)
def test_mcbs_facility_definition_gives_a_larger_gap(year):
    total_people, community_people, total_pay, community_pay = MCBS[year]
    mcbs_ratio = (community_pay / community_people) / (total_pay / total_people)
    assert 0.9 < mcbs_ratio < _stored(2022)


# Reformed systems take seconds to build, so the property tests draw the
# ratio from a few values and build each system once.
RATIOS = (0.5, 0.8, 0.95, 1)


@lru_cache(maxsize=None)
def _system(ratio):
    if ratio is None:
        return system
    reform = Reform.from_dict(
        {RATIO: {f"{FIRST_YEAR}-01-01.{END_YEAR}-12-31": ratio}},
        country_id="us",
    )
    return CountryTaxBenefitSystem(reform=reform)


def _simulation(year, people, ratio=None):
    names = list(people)
    return Simulation(
        tax_benefit_system=_system(ratio),
        situation={
            "people": people,
            "tax_units": {f"tax_unit_{name}": {"members": [name]} for name in names},
            "spm_units": {"spm_unit": {"members": names}},
            "families": {"family": {"members": names}},
            "marital_units": {
                f"marital_unit_{name}": {"members": [name]} for name in names
            },
            "households": {"household": {"members": names, "state_code": {year: "CA"}}},
        },
    )


def _person(year, enrolled, part_a=0, part_b=0):
    return {
        "age": {year: 70},
        "is_medicare_eligible": {year: True},
        "medicare_enrolled": {year: enrolled},
        "base_part_a_premium": {year: part_a},
        "gross_medicare_part_b_premium": {year: part_b},
        "income_adjusted_part_d_premium_surcharge": {year: 0},
        "msp_category": {f"{year}-01": "QMB"},
    }


def _reference(year, ratio, part_a, part_b):
    p = system.parameters(f"{year}-01-01").calibration.gov.hhs.medicare
    spending = p.per_capita_cost
    premiums = p.premium_income_per_enrollee
    part_d = p.part_d.enrollment_share * p.part_d.premiums_per_enrollee
    rate = system.parameters(
        f"{year}-01-01"
    ).gov.hhs.medicare.savings_programs.qmb.cost_sharing_rate
    return {
        "medicare_gross_cost": spending * ratio,
        "medicare_cost": max(spending * ratio - part_a - part_b - part_d, 0),
        "cbo_medicare_benefit": max(
            (spending - p.part_d_low_income_subsidy_per_enrollee) * ratio
            - (premiums.part_a + premiums.part_b + premiums.part_d),
            0,
        ),
        "qmb_cost_sharing": spending * ratio / 12 * rate,
    }


def _calculate(simulation, year):
    return {
        name: simulation.calculate(
            name, f"{year}-01" if name == "qmb_cost_sharing" else year
        )
        for name in (
            "medicare_gross_cost",
            "medicare_cost",
            "cbo_medicare_benefit",
            "qmb_cost_sharing",
        )
    }


premiums = st.floats(0, 30_000, allow_nan=False)


@settings(max_examples=12, deadline=None, suppress_health_check=[HealthCheck.too_slow])
@given(
    st.integers(2015, END_YEAR),
    st.sampled_from(RATIOS),
    st.sampled_from(RATIOS),
    st.floats(0, 12_000, allow_nan=False),
    premiums,
)
def test_consumers_match_reference_for_any_ratio(year, one, other, part_a, part_b):
    low, high = sorted((one, other))
    results = {}
    for value in (low, high):
        simulation = _simulation(
            year,
            {
                "enrolled": _person(year, True, part_a, part_b),
                "not_enrolled": _person(year, False),
            },
            ratio=value,
        )
        results[value] = _calculate(simulation, year)
        reference = _reference(year, value, part_a, part_b)
        for name, values in results[value].items():
            # Variables are float32, so compare to single precision.
            assert values[0] == pytest.approx(reference[name], rel=1e-6, abs=0.01)
            if name != "qmb_cost_sharing":
                assert values[1] == 0
        gross = results[value]["medicare_gross_cost"][0]
        for name in ("medicare_cost", "cbo_medicare_benefit"):
            assert 0 <= results[value][name][0] <= gross
    for name in results[low]:
        assert results[low][name][0] <= results[high][name][0] + 0.01


@settings(max_examples=5, deadline=None, suppress_health_check=[HealthCheck.too_slow])
@given(st.integers(2015, END_YEAR), premiums)
def test_ratio_of_one_reproduces_unscaled_formulas(year, part_b):
    unscaled = _calculate(
        _simulation(year, {"enrolled": _person(year, True, 0, part_b)}, ratio=1),
        year,
    )
    baseline = _calculate(
        _simulation(year, {"enrolled": _person(year, True, 0, part_b)}), year
    )
    p = system.parameters(f"{year}-01-01").calibration.gov.hhs.medicare
    assert unscaled["medicare_gross_cost"][0] == pytest.approx(
        p.per_capita_cost, rel=1e-6
    )
    # Gross spending scales exactly with the ratio.
    assert baseline["medicare_gross_cost"][0] == pytest.approx(
        unscaled["medicare_gross_cost"][0] * _stored(year), rel=1e-6
    )
    assert baseline["qmb_cost_sharing"][0] == pytest.approx(
        unscaled["qmb_cost_sharing"][0] * _stored(year), rel=1e-6
    )

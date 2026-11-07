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

These tests read parameters only. Tests elsewhere cover the consumers at the
stored ratio: the YAML tests of ``medicare_gross_cost``, ``medicare_cost``,
``cbo_medicare_benefit`` and ``qmb_cost_sharing``, and the reference
implementations in test_medicare_per_capita_cost.py,
test_medicare_cost_part_d_premium.py and test_cbo_medicare_benefit_series.py,
which multiply by this parameter.

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
4. Definition order: excluding everyone living in a Medicare Current
   Beneficiary Survey long-term care facility, which includes assisted living
   and retirement homes, gives a lower ratio in every year of the published
   2006-2013 tables (community-only over all-beneficiary benefit payments per
   capita), so the nursing home ratio is the smaller of the two corrections.
5. Differential: CBO's 2006 figures, from a different method and source,
   imply a ratio per recipient and per survey reporter within 0.01 of the
   stored value.
"""

import pytest
from hypothesis import given
from hypothesis import strategies as st
from policyengine_core.parameters.operations.get_parameter import get_parameter

from policyengine_us.system import system

RATIO = "calibration.gov.hhs.medicare.noninstitutionalized_spending_ratio"
FIRST_YEAR, END_YEAR = 2013, 2100

# MedPAC, June 2025 Report to the Congress, chapter 5 (file pages 8, 9 and
# 13), and October 2024 meeting slides (file page 5).
LONG_STAY_SPENDING, OTHER_SPENDING = 31_200, 11_300
LONG_STAY_SHARE = 0.017
LONG_STAY_FFS_SHARE, OTHER_FFS_SHARE = 0.62, 0.53
LONG_STAY_RISK_SCORE, OTHER_RISK_SCORE = 2.12, 1.01

# MCBS Characteristics and Perceptions of the Medicare Population, each
# year's edition
# (https://www.cms.gov/research-statistics-data-and-systems/research/mcbs/
# downloads/<year>_characteristics_and_perceptions.zip), all beneficiaries:
# Table 1.1 beneficiaries (thousands) and Table 4.1 benefit payments ($
# millions), total and community only.
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

# CBO 2006, in billions of dollars. Working Paper 2018-07: 93 percent of
# enrollees reported Medicare in the survey and 6 percent of recipients were
# institutionalized (file pages 45-46); Medicare benefits other than the
# low-income subsidy after CBO's adjustments, $352.4, and the subsidy, $10.3
# (file page 51). CBO (2013), The Distribution of Federal Spending and Taxes
# in 2006: $32 of Medicare spending for people in long-term care institutions
# (file page 53). 2007 Medicare Trustees Report, Table II.B1: 2006 benefits,
# $402.0, and Part A premiums, $2.6, which CBO subtracts (file page 52).
CBO_REPORTING_RATE, CBO_INSTITUTIONALIZED_SHARE = 0.93, 0.06
CBO_ADJUSTED_BENEFITS, CBO_LOW_INCOME_SUBSIDY = 352.4, 10.3
CBO_INSTITUTIONAL_SPENDING = 32
TRUSTEES_BENEFITS, TRUSTEES_PART_A_PREMIUMS = 402.0, 2.6


def _ratio(share, relative):
    return 1 / (1 + share * (relative - 1))


def _stored(date):
    return get_parameter(system.parameters, RATIO)(date)


def test_value_is_the_medpac_formula():
    expected = _ratio(LONG_STAY_SHARE, LONG_STAY_SPENDING / OTHER_SPENDING)
    assert _stored("2022-01-01") == round(expected, 3) == 0.971


@given(st.integers(FIRST_YEAR, END_YEAR + 100), st.integers(1, 12))
def test_ratio_is_a_constant_share_below_one(year, month):
    value = _stored(f"{year}-{month:02d}-01")
    assert 0 < value < 1
    assert value == _stored("2022-01-01")


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
    assert ffs_ratio < _stored("2022-01-01") < mixed_ratio


@pytest.mark.parametrize("year", MCBS)
def test_mcbs_facility_definition_gives_a_larger_gap(year):
    total_people, community_people, total_pay, community_pay = MCBS[year]
    mcbs_ratio = (community_pay / community_people) / (total_pay / total_people)
    # The stored ratio starts in 2013, so compare every year to its value.
    assert 0.9 < mcbs_ratio < _stored("2022-01-01")


def test_cbo_2006_figures_imply_a_similar_ratio():
    benefits = TRUSTEES_BENEFITS - TRUSTEES_PART_A_PREMIUMS - CBO_LOW_INCOME_SUBSIDY
    assert benefits == pytest.approx(389.1)
    per_recipient = (1 - CBO_INSTITUTIONAL_SPENDING / benefits) / (
        1 - CBO_INSTITUTIONALIZED_SHARE
    )
    per_reporter = CBO_ADJUSTED_BENEFITS / benefits / CBO_REPORTING_RATE
    assert round(per_recipient, 3) == 0.976
    assert round(per_reporter, 3) == 0.974
    for implied in (per_recipient, per_reporter):
        assert implied == pytest.approx(_stored("2013-01-01"), abs=0.01)

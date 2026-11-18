"""The CMS employer-sponsored insurance (ESI) premium per enrollee series that
employer plan premium inputs uprate by.

CMS's National Health Expenditure projections (Table 17, 2025-2034 release)
report ESI spending, ESI enrollment and ESI spending per enrollee for 2013 to
2034. ESI spending is premiums paid by employers and employees (NHEA
methodology paper, file page 29), so spending per enrollee is the premium per
covered person. The parameter holds that row; from 2035 its growth glides
from the 2033-2034 rate to the Medicare Trustees' long-range per capita health
spending rates (``tests/core/test_long_range_health_growth.py``).

These tests read only the parameter tree. Engine uprating of the inputs (a
household simulation and dataset extension) is covered in
``tests/microsimulation/test_esi_premium_microsim_uprating.py``.

Invariants:

1. Transcription: every value is Table 17's published dollar figure, and is
   consistent with the same table's ESI spending over ESI enrollment within
   rounding.
2. Employer share: CMS projects employer contributions (Table 16) as a flat
   share of ESI spending, so employer contributions per ESI enrollee grow with
   the index. That is why one index serves the employer and employee shares.
3. Bounds and order: the index is positive in every year and strictly
   increasing, as CMS's series is in every year from 2013 to 2034; the
   extension keeps both through 2100.
4. Extension rule: growth in 2035 starts from 13,124 / 12,559 and reaches
   the Trustees' 4.3 percent in 2050 and 4.1 percent in 2100.
"""

import pytest
from hypothesis import given
from hypothesis import strategies as st
from policyengine_core.parameters.operations.get_parameter import get_parameter

from policyengine_us.system import system

ESI = "calibration.gov.hhs.cms.esi_premium_per_enrollee"
PREMIUM_INPUTS = (
    "employer_sponsored_insurance_premiums",
    "pre_tax_health_insurance_premiums",
)
FIRST_YEAR, LAST_PROJECTED_YEAR, END_YEAR = 2013, 2034, 2100
YEARS = range(FIRST_YEAR, LAST_PROJECTED_YEAR + 1)

# CMS NHE projections tables, Table 17, "Employer-sponsored Insurance" rows
# (https://www.cms.gov/files/zip/nhe-projections-tables.zip, Last-Modified
# 2026-09-03, sha256 264f8226...cd70).
ESI_SPENDING_PER_ENROLLEE = dict(
    zip(
        YEARS,
        (
            *(4_901, 4_980, 5_113, 5_354, 5_500, 5_783, 5_955, 6_049, 6_456),
            *(6_877, 7_595, 8_000, 8_616, 9_181, 9_627, 10_093, 10_533),
            *(11_001, 11_469, 11_986, 12_559, 13_124),
        ),
    )
)
ESI_SPENDING_BILLIONS = dict(
    zip(
        YEARS,
        (
            *(829.1, 845.4, 880.5, 926.8, 965.7, 1013.1, 1050.3, 1052.7),
            *(1120.9, 1203.9, 1333.5, 1429.1, 1549.8, 1650.5, 1732.9),
            *(1820.4, 1896.9, 1978.0, 2058.6, 2148.4, 2246.7, 2343.1),
        ),
    )
)
ESI_ENROLLMENT_MILLIONS = dict(
    zip(
        YEARS,
        (
            *(169.2, 169.8, 172.2, 173.1, 175.6, 175.2, 176.4, 174.0),
            *(173.6, 175.1, 175.6, 178.6, 179.9, 179.8, 180.0, 180.4),
            *(180.1, 179.8, 179.5, 179.2, 178.9, 178.5),
        ),
    )
)
# Table 16, employer contributions to private health insurance premiums by
# private business, the federal government and state and local governments.
EMPLOYER_CONTRIBUTIONS_BILLIONS = {
    2024: 753 + 47 + 247,
    2026: 865 + 56 + 288,
    2034: 1_207 + 82 + 429,
}


def _index(year):
    return get_parameter(system.parameters, ESI)(f"{year}-01-01")


@pytest.mark.parametrize("year", YEARS)
def test_index_is_table_17_spending_per_enrollee(year):
    assert _index(year) == ESI_SPENDING_PER_ENROLLEE[year]


@pytest.mark.parametrize("year", YEARS)
def test_published_values_match_spending_over_enrollment(year):
    """Checks the transcribed rows against each other, so one mistyped
    spending, enrollment or per-enrollee figure fails."""
    spending = ESI_SPENDING_BILLIONS[year]
    enrollment = ESI_ENROLLMENT_MILLIONS[year]
    # Both components are rounded to one decimal and the published value to
    # the dollar.
    low = 1_000 * (spending - 0.05) / (enrollment + 0.05) - 0.5
    high = 1_000 * (spending + 0.05) / (enrollment - 0.05) + 0.5
    assert low <= ESI_SPENDING_PER_ENROLLEE[year] <= high


@pytest.mark.parametrize("start, end", [(2024, 2034), (2026, 2034)])
def test_employer_contributions_per_enrollee_grow_with_the_index(start, end):
    def per_enrollee(year):
        return EMPLOYER_CONTRIBUTIONS_BILLIONS[year] / ESI_ENROLLMENT_MILLIONS[year]

    years = end - start
    employer_growth = (per_enrollee(end) / per_enrollee(start)) ** (1 / years)
    index_growth = (_index(end) / _index(start)) ** (1 / years)
    assert employer_growth == pytest.approx(index_growth, abs=0.001)
    # The employer share of ESI premiums stays within 73.2% to 73.4%.
    for year in (start, end):
        share = EMPLOYER_CONTRIBUTIONS_BILLIONS[year] / ESI_SPENDING_BILLIONS[year]
        assert 0.732 <= share <= 0.734


@given(
    st.integers(FIRST_YEAR, END_YEAR - 1),
    st.integers(1, END_YEAR - FIRST_YEAR),
)
def test_index_is_positive_and_strictly_increasing(year, gap):
    later = min(year + gap, END_YEAR)
    assert 0 < _index(year) < _index(later)


@given(st.integers(LAST_PROJECTED_YEAR + 1, END_YEAR))
def test_extension_glides_from_the_last_projected_growth_rate(year):
    last_growth = _index(LAST_PROJECTED_YEAR) / _index(LAST_PROJECTED_YEAR - 1) - 1
    assert last_growth == pytest.approx(13_124 / 12_559 - 1, rel=1e-12)
    if year <= 2050:
        share = (year - LAST_PROJECTED_YEAR) / (2050 - LAST_PROJECTED_YEAR)
        expected = last_growth + share * (0.043 - last_growth)
    else:
        expected = 0.043 + (year - 2050) / 50 * (0.041 - 0.043)
    assert _index(year) / _index(year - 1) - 1 == pytest.approx(expected, rel=1e-12)


@pytest.mark.parametrize("variable", PREMIUM_INPUTS)
def test_premium_inputs_uprate_by_the_esi_index(variable):
    assert system.variables[variable].uprating == ESI

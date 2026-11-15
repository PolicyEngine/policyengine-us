"""Each state's Medicaid adult income limit must equal its expansion FMAP
income limit or differ from it by at least the MAGI disregard.

`medicaid_federal_share` compares the two parameters. When a state's adult
income limit exceeds its expansion FMAP income limit, the formula infers a
higher optional adult group (42 CFR 435.218) and stops the expansion FMAP at
the limit less the disregard. When the adult limit falls short, the formula
treats the state as a partial expansion and gives every adult the regular
FMAP. A small mismatch between the two files therefore moves adults to the
regular FMAP with no change in coverage: Indiana's adult limit at 1.38 or
1.3965 against its 1.39 expansion FMAP income limit through 2020, or the two
files switching Indiana to 1.38 in different years.
"""

import pytest

from policyengine_us.system import system

YEARS = range(2015, 2031)

COST_SHARE = system.parameters.gov.hhs.medicaid.cost_share
GROUP_LIMIT = COST_SHARE.expansion_fmap_income_limit
DISREGARD = COST_SHARE.expansion_fmap_income_disregard
ADULT_LIMIT = (
    system.parameters.gov.hhs.medicaid.eligibility.categories.adult.income_limit
)


def test_adult_and_expansion_fmap_limits_cover_the_same_states():
    assert set(GROUP_LIMIT.children) == set(ADULT_LIMIT.children)


@pytest.mark.parametrize("year", YEARS)
def test_adult_limit_is_not_a_near_miss_of_the_expansion_fmap_limit(year):
    instant = f"{year}-01-01"
    disregard = DISREGARD(instant)
    near_misses = {}
    for state, group_parameter in GROUP_LIMIT.children.items():
        group_limit = group_parameter(instant)
        adult_limit = ADULT_LIMIT.children[state](instant)
        gap = abs(round(adult_limit - group_limit, 6))
        if 0 < gap < disregard:
            near_misses[state] = (adult_limit, group_limit)
    assert not near_misses, (
        f"In {year}, these states' adult income limits (first value) differ "
        "from their expansion FMAP income limits (second value) by less than "
        f"the {disregard} disregard: {near_misses}"
    )

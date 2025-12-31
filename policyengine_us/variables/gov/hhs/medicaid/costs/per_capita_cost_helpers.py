"""Helper functions for calculating per capita Medicaid costs.

This module provides shared logic for calculating per capita costs that is
used by:
- medicaid_cost_if_enrolled (for federal Medicaid)
- or_healthier_oregon_cost_if_enrolled (for Oregon Healthier Oregon)
- Other state Medicaid-like programs
"""

from policyengine_us.model_api import *


def calculate_per_capita_cost(
    person, period, parameters, group, MedicaidGroup
):
    """Calculate per capita Medicaid cost for a given eligibility group.

    Args:
        person: The person entity
        period: The calculation period
        parameters: The parameters object
        group: Array of MedicaidGroup values for each person
        MedicaidGroup: The MedicaidGroup enum class

    Returns:
        Array of per capita costs for each person based on their group
    """
    state = person.household("state_code", period)

    p = parameters(period).calibration.gov.hhs.medicaid

    # Get spending by eligibility group and state
    aged_spend = p.spending.by_eligibility_group.aged[state]
    disabled_spend = p.spending.by_eligibility_group.disabled[state]
    child_spend = p.spending.by_eligibility_group.child[state]
    expansion_adult_spend = p.spending.by_eligibility_group.expansion_adults[
        state
    ]
    non_expansion_adult_spend = (
        p.spending.by_eligibility_group.non_expansion_adults[state]
    )

    # Get enrollment by eligibility group and state
    aged_enroll = p.enrollment.aged[state]
    disabled_enroll = p.enrollment.disabled[state]
    child_enroll = p.enrollment.child[state]
    expansion_adult_enroll = p.enrollment.expansion_adults[state]
    non_expansion_adult_enroll = p.enrollment.non_expansion_adults[state]

    # Combine aged and disabled for AGED_DISABLED group
    aged_disabled_spend = aged_spend + disabled_spend
    aged_disabled_enroll = aged_enroll + disabled_enroll

    # Determine group membership
    is_aged_disabled = group == MedicaidGroup.AGED_DISABLED
    is_child = group == MedicaidGroup.CHILD
    is_expansion_adult = group == MedicaidGroup.EXPANSION_ADULT
    is_non_expansion_adult = group == MedicaidGroup.NON_EXPANSION_ADULT

    # Select spending based on group
    spend = select(
        [
            is_aged_disabled,
            is_child,
            is_expansion_adult,
            is_non_expansion_adult,
        ],
        [
            aged_disabled_spend,
            child_spend,
            expansion_adult_spend,
            non_expansion_adult_spend,
        ],
        default=0,
    )

    # Select enrollment based on group
    enroll = select(
        [
            is_aged_disabled,
            is_child,
            is_expansion_adult,
            is_non_expansion_adult,
        ],
        [
            aged_disabled_enroll,
            child_enroll,
            expansion_adult_enroll,
            non_expansion_adult_enroll,
        ],
        default=0,
    )

    # Calculate per capita cost
    # Use national average as fallback when enrollment is zero
    per_capita = p.totals.per_capita[group].copy()
    mask = enroll > 0
    per_capita[mask] = spend[mask] / enroll[mask]

    return per_capita

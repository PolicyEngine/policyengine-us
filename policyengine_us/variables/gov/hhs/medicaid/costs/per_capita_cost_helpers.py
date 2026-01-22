"""Helper functions for calculating per capita Medicaid costs.

This module provides shared logic for calculating per capita costs that is
used by:
- medicaid_cost_if_enrolled (for federal Medicaid)
- or_healthier_oregon_cost_if_enrolled (for Oregon Healthier Oregon)
- wa_apple_health_cost_if_enrolled (for Washington Apple Health)
- Other state Medicaid-like programs
"""

from policyengine_us.model_api import *


def calculate_per_capita_cost(
    person,
    period,
    parameters,
    group,
    MedicaidGroup,
    groups=None,
    state=None,
):
    """Calculate per capita Medicaid cost for given eligibility groups.

    Supports flexible group configurations - states can use all 4 groups
    or a subset (e.g., Washington uses only CHILD and EXPANSION_ADULT).

    Args:
        person: The person entity
        period: The calculation period
        parameters: The parameters object
        group: Array of MedicaidGroup values for each person
        MedicaidGroup: The MedicaidGroup enum class
        groups: List of MedicaidGroup values to handle. If None, uses all 4:
                [AGED_DISABLED, CHILD, EXPANSION_ADULT, NON_EXPANSION_ADULT].
                For states with fewer groups, pass only the relevant ones,
                e.g., [MedicaidGroup.CHILD, MedicaidGroup.EXPANSION_ADULT]
        state: State code for state-specific data lookup. If None, uses
               the person's household state code.

    Returns:
        Array of per capita costs for each person based on their group.
        Uses state-specific spending/enrollment when available, falling
        back to national average when state enrollment is zero.
    """
    if state is None:
        state = person.household("state_code", period)

    if groups is None:
        groups = [
            MedicaidGroup.AGED_DISABLED,
            MedicaidGroup.CHILD,
            MedicaidGroup.EXPANSION_ADULT,
            MedicaidGroup.NON_EXPANSION_ADULT,
        ]

    p = parameters(period).calibration.gov.hhs.medicaid

    conditions = []
    spend_values = []
    enroll_values = []

    for g in groups:
        if g == MedicaidGroup.AGED_DISABLED:
            # Combine aged and disabled data for AGED_DISABLED group
            spend = (
                p.spending.by_eligibility_group.aged[state]
                + p.spending.by_eligibility_group.disabled[state]
            )
            enroll = p.enrollment.aged[state] + p.enrollment.disabled[state]
        elif g == MedicaidGroup.CHILD:
            spend = p.spending.by_eligibility_group.child[state]
            enroll = p.enrollment.child[state]
        elif g == MedicaidGroup.EXPANSION_ADULT:
            spend = p.spending.by_eligibility_group.expansion_adults[state]
            enroll = p.enrollment.expansion_adults[state]
        elif g == MedicaidGroup.NON_EXPANSION_ADULT:
            spend = p.spending.by_eligibility_group.non_expansion_adults[state]
            enroll = p.enrollment.non_expansion_adults[state]
        else:
            # Skip unknown groups (e.g., NONE)
            continue

        conditions.append(group == g)
        spend_values.append(spend)
        enroll_values.append(enroll)

    spend = select(conditions, spend_values, default=0)
    enroll = select(conditions, enroll_values, default=0)

    # Calculate per capita cost
    # Use national average as fallback when state enrollment is zero
    # Return 0 for NONE group (not eligible for any program)
    is_none = group == MedicaidGroup.NONE
    per_capita = p.totals.per_capita[group].copy()
    mask = (enroll > 0) & ~is_none
    per_capita[mask] = spend[mask] / enroll[mask]
    per_capita[is_none] = 0

    return per_capita

from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.medicaid.costs.medicaid_group import (
    MedicaidGroup,
)


class wa_apple_health_cost_if_enrolled(Variable):
    value_type = float
    entity = Person
    label = "Per capita Washington Apple Health cost by eligibility group"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.WA
    reference = [
        "https://www.hca.wa.gov/about-hca/programs-and-initiatives/apple-health-medicaid/apple-health-expansion",
    ]
    documentation = """
    Calculates the per-capita cost of Washington Apple Health coverage based
    on the person's eligibility group (Kids or Expansion). Uses Washington
    state Medicaid cost data by eligibility category.

    Note: Apple Health Expansion is 100% state-funded (~$150M in 2025-2027
    biennial budget), while Apple Health for Kids uses a mix of state and
    federal funds depending on the child's citizenship/immigration status.
    """

    def formula(person, period, parameters):
        group = person("wa_apple_health_group", period)

        p = parameters(period).calibration.gov.hhs.medicaid

        is_child = group == MedicaidGroup.CHILD
        is_expansion_adult = group == MedicaidGroup.EXPANSION_ADULT

        # Use Washington state Medicaid cost data
        child_spend = p.spending.by_eligibility_group.child["WA"]
        expansion_adult_spend = (
            p.spending.by_eligibility_group.expansion_adults["WA"]
        )

        child_enroll = p.enrollment.child["WA"]
        expansion_adult_enroll = p.enrollment.expansion_adults["WA"]

        spend = select(
            [is_child, is_expansion_adult],
            [child_spend, expansion_adult_spend],
            default=0,
        )

        enroll = select(
            [is_child, is_expansion_adult],
            [child_enroll, expansion_adult_enroll],
            default=0,
        )

        # Calculate per-capita cost, avoiding divide-by-zero
        return np.where(enroll > 0, spend / enroll, 0)

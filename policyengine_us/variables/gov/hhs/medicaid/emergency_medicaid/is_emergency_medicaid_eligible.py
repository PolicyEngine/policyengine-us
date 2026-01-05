from policyengine_us.model_api import *


class is_emergency_medicaid_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Eligible for Emergency Medicaid"
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/42/1396b#v_2",
        "https://www.law.cornell.edu/cfr/text/42/435.406",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.hhs.medicaid.emergency_medicaid

        has_emergency_condition = person(
            "has_emergency_medical_condition", period
        )
        medicaid_category = person("medicaid_category", period)
        meets_medicaid_requirements = (
            medicaid_category != medicaid_category.possible_values.NONE
        )
        immigration_status_eligible = person(
            "is_medicaid_immigration_status_eligible", period
        )

        return (
            p.enabled
            & has_emergency_condition
            & meets_medicaid_requirements
            & ~immigration_status_eligible
        )

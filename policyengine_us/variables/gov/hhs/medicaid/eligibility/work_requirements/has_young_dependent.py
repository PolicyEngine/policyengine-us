from policyengine_us.model_api import *


class has_young_dependent(Variable):
    value_type = bool
    entity = Person
    label = "Is taking care of a child 13 years or younger"
    definition_period = MONTH
    reference = "https://www.congress.gov/bill/119th-congress/house-bill/1/text"

    def formula(person, period, parameters):
        age = person("age", period.this_year)
        is_dependent = person("is_tax_unit_dependent", period.this_year)

        dependent_age_limit = parameters(
            period
        ).gov.hhs.medicaid.eligibility.work_requirements.dependent_age_limit
        child_age_eligible = age <= dependent_age_limit
        has_eligible_dependent_child = person.tax_unit.any(
            is_dependent & child_age_eligible
        )

        return has_eligible_dependent_child

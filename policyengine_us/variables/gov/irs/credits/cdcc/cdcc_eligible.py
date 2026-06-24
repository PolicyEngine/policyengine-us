from policyengine_us.model_api import *


class is_cdcc_eligible(Variable):
    value_type = bool
    entity = Person
    label = "CDCC-eligible"
    definition_period = YEAR
    reference = "https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title26-section21&num=0&edition=prelim"

    def formula(person, period, parameters):
        age = person("age", period)
        is_dependent = person("is_tax_unit_dependent", period)
        # Subsection A.
        max_age = parameters(period).gov.irs.credits.cdcc.eligibility.child_age
        qualifies_by_age = is_dependent & (age < max_age)
        # Subsection B (dependent) and C (spouse).
        disabled = person("is_incapable_of_self_care", period)
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        has_spouse = person.tax_unit.sum(head_or_spouse) > 1
        qualifies_by_disability = disabled & (
            is_dependent | (head_or_spouse & has_spouse)
        )
        return qualifies_by_age | qualifies_by_disability

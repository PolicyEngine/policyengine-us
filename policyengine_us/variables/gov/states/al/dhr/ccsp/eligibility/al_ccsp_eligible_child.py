from policyengine_us.model_api import *


class al_ccsp_eligible_child(Variable):
    value_type = bool
    entity = Person
    label = "Eligible child for Alabama CCSP"
    definition_period = MONTH
    defined_for = StateCode.AL
    reference = "https://dhr.alabama.gov/wp-content/uploads/2023/04/2025-2027-CCDF-State-Plan-with-Approval-Letter.pdf#page=20"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.al.dhr.ccsp.age
        age = person("age", period.this_year)
        is_disabled = person("is_disabled", period.this_year)
        age_eligible = where(
            is_disabled,
            age < p.disabled_child_limit,
            age < p.child_limit,
        )
        immigration_eligible = person(
            "is_ccdf_immigration_eligible_child", period.this_year
        )
        is_dependent = person("is_tax_unit_dependent", period.this_year)
        return age_eligible & immigration_eligible & is_dependent

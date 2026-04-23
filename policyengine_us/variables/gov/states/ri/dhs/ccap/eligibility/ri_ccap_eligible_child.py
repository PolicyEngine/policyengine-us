from policyengine_us.model_api import *


class ri_ccap_eligible_child(Variable):
    value_type = bool
    entity = Person
    label = "Eligible child for Rhode Island CCAP"
    definition_period = MONTH
    defined_for = StateCode.RI
    reference = "https://rules.sos.ri.gov/regulations/part/218-20-00-4#4.3.1"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ri.dhs.ccap.age_threshold
        age = person("age", period.this_year)
        is_disabled = person("is_disabled", period.this_year)
        age_eligible = where(is_disabled, age <= p.disabled_child, age < p.child)
        is_dependent = person("is_tax_unit_dependent", period.this_year)
        immigration_eligible = person(
            "is_ccdf_immigration_eligible_child", period.this_year
        )
        return age_eligible & is_dependent & immigration_eligible

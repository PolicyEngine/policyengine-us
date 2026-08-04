from policyengine_us.model_api import *


class id_iccp_eligible_child(Variable):
    value_type = bool
    entity = Person
    definition_period = MONTH
    label = "Child eligible for the Idaho Child Care Program"
    defined_for = StateCode.ID
    reference = "https://adminrules.idaho.gov/rules/current/16/160612.pdf#page=12"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.id.dhw.iccp.age_threshold
        age = person("age", period.this_year)
        is_disabled = person("is_disabled", period.this_year)
        age_eligible = (age < p.child) | (is_disabled & (age < p.disabled_child))
        immigration_eligible = person(
            "is_ccdf_immigration_eligible_child", period.this_year
        )
        return age_eligible & immigration_eligible

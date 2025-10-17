from policyengine_us.model_api import *


class tx_ccs_eligible_child(Variable):
    value_type = bool
    entity = Person
    label = "Texas CCS eligible child"
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/regulations/texas/40-Tex-Admin-Code-SS-809-41"
    defined_for = StateCode.TX

    def formula(person, period, parameters):
        p = parameters(period).gov.states.tx.twc.ccs.age_threshold
        age = person("age", period.this_year)
        is_disabled = person("is_disabled", period)
        age_limit = where(is_disabled, p.disabled_child, p.child)
        age_eligible = age < age_limit
        is_dependent = person("is_tax_unit_dependent", period)
        immigration_status_eligible = person(
            "is_citizen_or_legal_immigrant", period
        )
        return age_eligible & is_dependent & immigration_status_eligible

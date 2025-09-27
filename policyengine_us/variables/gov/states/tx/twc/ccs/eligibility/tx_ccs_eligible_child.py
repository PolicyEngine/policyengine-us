from policyengine_us.model_api import *


class tx_ccs_eligible_child(Variable):
    value_type = bool
    entity = Person
    label = "Texas CCS eligible child"
    definition_period = MONTH
    reference = "http://txrules.elaws.us/rule/title40_chapter809_sec.809.41"
    defined_for = StateCode.TX

    def formula(person, period, parameters):
        p = parameters(period).gov.states.tx.twc.ccs.age_threshold
        age = person("age", period.this_year)
        is_disabled = person("is_disabled", period)
        age_limit = where(is_disabled, p.disabled_child, p.child)

        return age < age_limit

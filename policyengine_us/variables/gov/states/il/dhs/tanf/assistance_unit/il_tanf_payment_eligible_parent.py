from policyengine_us.model_api import *


class il_tanf_payment_eligible_parent(Variable):
    value_type = bool
    entity = Person
    definition_period = MONTH
    label = "Eligible parent for Illinois Temporary Assistance for Needy Families (TANF) payment"
    reference = "https://www.law.cornell.edu/regulations/illinois/Ill-Admin-Code-tit-89-SS-112.60"
    defined_for = StateCode.IL

    def formula(person, period, parameters):
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        immigration_status_eligible = person("il_tanf_immigration_status_eligible_person", period)
        ssi = person("ssi", period)
        receives_ssi = ssi > 0

        return ~receives_ssi & is_head_or_spouse & immigration_status_eligible

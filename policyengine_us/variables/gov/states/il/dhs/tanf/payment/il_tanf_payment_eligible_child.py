from policyengine_us.model_api import *


class il_tanf_payment_eligible_child(Variable):
    value_type = bool
    entity = Person
    definition_period = MONTH
    label = "Eligible child for Illinois Temporary Assistance for Needy Families (TANF) payment"
    reference = "https://www.law.cornell.edu/regulations/illinois/Ill-Admin-Code-tit-89-SS-112.60"
    defined_for = StateCode.IL

    def formula(person, period, parameters):
        eligible_child = person("il_tanf_eligible_child", period)
        ssi = person("ssi", period)
        receive_ssi = ssi > 0

        return ~receive_ssi & eligible_child

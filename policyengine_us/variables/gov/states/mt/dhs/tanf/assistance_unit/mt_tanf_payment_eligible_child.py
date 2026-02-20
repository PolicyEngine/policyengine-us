from policyengine_us.model_api import *


class mt_tanf_payment_eligible_child(Variable):
    value_type = bool
    entity = Person
    definition_period = MONTH
    label = "Eligible child for Montana Temporary Assistance for Needy Families (TANF) payment"
    reference = "https://www.law.cornell.edu/regulations/montana/Mont-Admin-r-37.78.208"
    defined_for = StateCode.MT

    def formula(person, period, parameters):
        eligible_child = person("mt_tanf_eligible_child", period)
        eligible_requirements = person(
            "mt_tanf_payment_eligible_requirements", period
        )
        return eligible_child & eligible_requirements

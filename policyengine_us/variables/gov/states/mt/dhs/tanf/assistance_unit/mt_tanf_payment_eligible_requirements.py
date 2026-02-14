from policyengine_us.model_api import *


class mt_tanf_payment_eligible_requirements(Variable):
    value_type = bool
    entity = Person
    definition_period = MONTH
    label = "Eligible requirements for Montana Temporary Assistance for Needy Families (TANF) payment"
    reference = (
        "https://www.law.cornell.edu/regulations/montana/Mont-Admin-r-37.78.206",
        "https://www.law.cornell.edu/regulations/montana/Mont-Admin-r-37.78.220",
    )
    defined_for = StateCode.MT

    def formula(person, period, parameters):
        immigration_status_eligible = person(
            "mt_tanf_immigration_status_eligible_person", period
        )
        ssi = person("ssi", period)
        receives_ssi = ssi > 0
        is_in_foster_care = person("is_in_foster_care", period)

        return ~receives_ssi & ~is_in_foster_care & immigration_status_eligible

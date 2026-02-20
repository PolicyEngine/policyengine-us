from policyengine_us.model_api import *


class mt_tanf_payment_eligible_parent(Variable):
    value_type = bool
    entity = Person
    definition_period = MONTH
    label = "Eligible parent for Montana Temporary Assistance for Needy Families (TANF) payment"
    reference = "https://www.law.cornell.edu/regulations/montana/Mont-Admin-r-37.78.208"
    defined_for = StateCode.MT

    def formula(person, period, parameters):
        is_head_or_spouse = person(
            "is_tax_unit_head_or_spouse", period.this_year
        )
        eligible_requirements = person(
            "mt_tanf_payment_eligible_requirements", period
        )

        return is_head_or_spouse & eligible_requirements

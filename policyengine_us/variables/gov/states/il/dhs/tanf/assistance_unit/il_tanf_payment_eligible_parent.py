from policyengine_us.model_api import *


class il_tanf_payment_eligible_parent(Variable):
    value_type = bool
    entity = Person
    definition_period = MONTH
    label = "Eligible parent for Illinois Temporary Assistance for Needy Families (TANF) payment"
    reference = "https://www.law.cornell.edu/regulations/illinois/Ill-Admin-Code-tit-89-SS-112.300"
    defined_for = StateCode.IL

    def formula(person, period, parameters):
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        eligible_requirements = person(
            "il_tanf_payment_eligible_requirements", period
        )

        return is_head_or_spouse & eligible_requirements

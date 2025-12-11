from policyengine_us.model_api import *


class il_mpe_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Illinois Medicaid Presumptive Eligibility eligible"
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/regulations/illinois/Ill-Admin-Code-tit-89-SS-120.66"
    defined_for = StateCode.IL

    def formula(person, period, parameters):
        is_pregnant = person("is_pregnant", period.this_year)
        income_eligible = person("il_mpe_income_eligible", period)
        return is_pregnant & income_eligible

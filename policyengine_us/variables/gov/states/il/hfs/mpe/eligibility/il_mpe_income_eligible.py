from policyengine_us.model_api import *


class il_mpe_income_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Illinois MPE income eligible"
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/regulations/illinois/Ill-Admin-Code-tit-89-SS-120.66"
    defined_for = StateCode.IL

    def formula(person, period, parameters):
        p = parameters(period).gov.states.il.hfs.mpe.eligibility
        income_level = person("medicaid_income_level", period.this_year)
        return income_level <= p.income_limit

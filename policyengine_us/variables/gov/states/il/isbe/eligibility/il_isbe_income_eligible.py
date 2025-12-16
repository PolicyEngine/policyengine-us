from policyengine_us.model_api import *


class il_isbe_income_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Meets income requirements for Illinois ISBE programs"
    definition_period = YEAR
    documentation = (
        "Shared income eligibility check for Illinois State Board of Education "
        "early childhood programs (PI, PFA, PFAE). Income must be at or below "
        "400% of the Federal Poverty Level."
    )
    reference = "https://cecids.org/methodology/"
    defined_for = StateCode.IL

    def formula(person, period, parameters):
        spm_unit = person.spm_unit
        # Income must be at or below 400% FPL for ISBE programs.
        p = parameters(period).gov.states.il.isbe.eligibility.income
        fpg = spm_unit("spm_unit_fpg", period)
        income = spm_unit("il_isbe_countable_income", period)
        threshold = fpg * p.income_limit_rate
        return income <= threshold

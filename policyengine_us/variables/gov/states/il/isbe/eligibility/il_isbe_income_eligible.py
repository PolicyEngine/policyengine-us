from policyengine_us.model_api import *


class il_isbe_income_eligible(Variable):
    value_type = bool
    entity = Person
    label = (
        "Meets income requirements for Illinois ISBE early childhood programs"
    )
    definition_period = YEAR
    reference = (
        "https://www.isbe.net/pages/preschool-for-all.aspx",
        "https://law.onecle.com/illinois/105ilcs5/2-3.71.html",
    )
    defined_for = StateCode.IL

    def formula(person, period, parameters):
        # Income must be at or below 400% FPL for program eligibility.
        # 105 ILCS 5/2-3.71 establishes "4 times the poverty guidelines" as the
        # maximum income threshold for preschool program eligibility.
        p = parameters(period).gov.states.il.isbe.income
        spm_unit = person.spm_unit
        fpg = spm_unit("spm_unit_fpg", period)
        income = spm_unit("il_isbe_countable_income", period)
        threshold = fpg * p.income_limit_rate
        return income <= threshold

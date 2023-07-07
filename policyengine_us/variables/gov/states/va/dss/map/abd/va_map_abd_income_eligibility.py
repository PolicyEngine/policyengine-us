from policyengine_us.model_api import *


class va_map_abd_income_eligibility(Variable):
    value_type = bool
    entity = SPMUnit
    label = "VA MAP ABD income eligibility"
    definition_period = YEAR
    defined_for = StateCode.VA

    def formula(spm_unit, period, parameters):
        income = add(
            spm_unit,
            period,
            [
                "va_map_earned_income",
                "va_map_unearned_income",
            ]
        )

        p = parameters(period).gov.states.va.dss.map.abd
        person = spm_unit.members
        married = person("is_married", period)
        limit = p.income_limit_single
        if spm_unit.any(married):
            limit = p.income_limit_couple

        return income <= limit

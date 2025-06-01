from policyengine_us.model_api import *


class va_map_abd_income_limit(Variable):
    value_type = float
    entity = SPMUnit
    label = "VA MAP ABD income limit"
    definition_period = YEAR
    defined_for = StateCode.VA

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.va.dss.map.abd
        married = add(spm_unit, period, ["is_married"]) > 0
        return (
            where(married, p.income_limit_couple, p.income_limit_single)
            * MONTHS_IN_YEAR
        )

from policyengine_us.model_api import *


class va_map_famis_income_limit(Variable):
    value_type = float
    entity = SPMUnit
    label = "VA MAP FAMIS Plus income limit"
    definition_period = YEAR
    defined_for = StateCode.VA

    def formula(spm_unit, period, parameters):
        unit_size = spm_unit("spm_unit_size", period)
        ceiling = min_(unit_size, 8)
        additional = unit_size - ceiling
        p = parameters(period).gov.states.va.dss.map.famis_plus

        return (
            p.income_limit_main[ceiling]
            + additional * p.income_limit_additional
        )

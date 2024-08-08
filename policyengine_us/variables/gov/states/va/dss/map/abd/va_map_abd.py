from policyengine_us.model_api import *


class va_map_abd(Variable):
    value_type = float
    entity = SPMUnit
    label = "VA MAP ABD benefits"
    unit = USD
    definition_period = YEAR
    defined_for = "va_map_abd_eligibility"

    def formula(spm_unit, period, parameters):
        monthly_premium = parameters(
            period
        ).gov.states.va.dss.map.abd.monthly_premium
        return monthly_premium * MONTHS_IN_YEAR

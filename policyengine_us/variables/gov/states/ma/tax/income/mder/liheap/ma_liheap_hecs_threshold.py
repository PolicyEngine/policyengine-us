from policyengine_us.model_api import *


class ma_liheap_hecs_threshold(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    defined_for = StateCode.MA
    label = "Massachusetts HECS Eligibility"

    def formula(spm_unit, period, parameters):
        utility_type = spm_unit("utility_type", period)
        last_year_cost = spm_unit("last_year_energy_cost", period)

        p = parameters(period).gov.states.ma.mder.liheap
        threshold = p.ma_liheap_hecs_thresholds[utility_type]

        return last_year_cost > threshold

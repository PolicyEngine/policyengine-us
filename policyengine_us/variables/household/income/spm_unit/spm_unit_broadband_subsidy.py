from policyengine_us.model_api import *


class spm_unit_broadband_subsidy(Variable):
    value_type = float
    entity = SPMUnit
    label = "SPM unit broadband subsidy"
    definition_period = YEAR
    unit = USD

    def formula(spm_unit, period, parameters):
        if parameters(period).gov.simulation.reported_broadband_subsidy:
            return spm_unit("spm_unit_broadband_subsidy_reported", period)
        return add(spm_unit, period, ["ebb", "acp", "lifeline"])

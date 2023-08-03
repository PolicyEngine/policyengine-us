from policyengine_us.model_api import *


class spm_unit_wic(Variable):
    value_type = float
    entity = SPMUnit
    label = "SPM unit WIC"
    definition_period = YEAR
    unit = USD

    def formula(spm_unit, period, parameters):
        disabled_programs = parameters(period).simulation.disabled_programs
        if "spm_unit_wic" in disabled_programs:
            return spm_unit("spm_unit_wic_reported", period)
        return add(spm_unit, period, ["wic"])

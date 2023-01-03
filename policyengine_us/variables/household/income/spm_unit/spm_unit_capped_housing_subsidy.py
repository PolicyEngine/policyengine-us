from policyengine_us.model_api import *


class spm_unit_capped_housing_subsidy(Variable):
    value_type = float
    entity = SPMUnit
    label = "Housing subsidies"
    definition_period = YEAR
    unit = USD

    def formula(spm_unit, period, parameters):
        if parameters(period).gov.hud.abolition:
            return 0
        disabled_programs = parameters(period).simulation.disabled_programs
        if "spm_unit_capped_housing_subsidy" in disabled_programs:
            return spm_unit("spm_unit_capped_housing_subsidy_reported", period)
        return 0

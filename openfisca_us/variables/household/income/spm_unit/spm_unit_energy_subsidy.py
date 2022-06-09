from openfisca_us.model_api import *


class spm_unit_energy_subsidy(Variable):
    value_type = float
    entity = SPMUnit
    label = "SPM unit school energy subsidy"
    definition_period = YEAR
    unit = USD

    def formula(spm_unit, period, parameters):
        disabled_programs = parameters(period).simulation.disabled_programs
        if "spm_unit_energy_subsidy" in disabled_programs:
            return spm_unit("spm_unit_energy_subsidy_reported", period)
        return 0

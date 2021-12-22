from openfisca_us.model_api import *


class is_ebb_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Emergency Broadband Benefit"
    documentation = "Eligible for Emergency Broadband Benefit"
    definition_period = YEAR

    def formula(spm_unit, period, parameters):
        programs = parameters(period).fcc.ebb.categorical_eligibility

        return np.any([spm_unit(program, period) for program in programs])

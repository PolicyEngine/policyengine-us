from policyengine_us.model_api import *


class is_ebb_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Emergency Broadband Benefit"
    documentation = "Eligible for Emergency Broadband Benefit"
    definition_period = YEAR

    def formula(spm_unit, period, parameters):
        programs = parameters(period).gov.fcc.ebb.categorical_eligibility
        eligible = np.any([spm_unit(program, period) for program in programs])
        # In transition period to Affordable Connectivity Program, households
        # must already be enrolled to receive EBB.
        if parameters(period).gov.fcc.ebb.prior_enrollment_required:
            return eligible & spm_unit("enrolled_in_ebb", period)
        return eligible

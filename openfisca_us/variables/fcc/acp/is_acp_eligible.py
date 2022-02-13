from openfisca_us.model_api import *


class is_acp_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Affordable Connectivity Program"
    documentation = "Eligible for Affordable Connectivity Program"
    definition_period = YEAR

    def formula(spm_unit, period, parameters):
        programs = parameters(period).fcc.acp.categorical_eligibility
        categorically_eligible = np.any(
            [aggr(spm_unit, period, [program]) for program in programs], axis=0
        )
        fpg_ratio = spm_unit("fcc_fpg_ratio", period)
        fpg_limit = parameters(period).fcc.acp.fpg_limit
        fpg_eligible = fpg_ratio <= fpg_limit
        # Cannot be simultaneously enrolled in Emergency Broadband Benefit.
        ebb_enrolled = spm_unit("ebb", period) > 0
        return (categorically_eligible | fpg_eligible) & ~ebb_enrolled

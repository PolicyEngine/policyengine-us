from openfisca_us.model_api import *


class is_lifeline_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Lifeline"
    documentation = "Eligible for Lifeline phone or broadband subsidy"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/cfr/text/47/54.409"

    def formula(spm_unit, period, parameters):
        programs = parameters(period).fcc.lifeline.categorical_eligibility
        categorically_eligible = np.any(
            [spm_unit(program, period) for program in programs]
        )
        fpg_eligible = (
            spm_unit("fcc_fpg_ratio")
            <= parameters(period).fcc.lifeline.fpl_threshold
        )
        return categorically_eligible | fpg_eligible

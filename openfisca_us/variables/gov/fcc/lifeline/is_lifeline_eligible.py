from openfisca_us.model_api import *


class is_lifeline_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Lifeline"
    documentation = "Eligible for Lifeline phone or broadband subsidy"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/cfr/text/47/54.409"

    def formula(spm_unit, period, parameters):
        programs = parameters(period).gov.fcc.lifeline.categorical_eligibility
        categorically_eligible = add(spm_unit, period, programs) > 0
        fpg_ratio = spm_unit("fcc_fpg_ratio", period)
        fpg_limit = parameters(period).gov.fcc.lifeline.fpg_limit
        fpg_eligible = fpg_ratio <= fpg_limit
        return categorically_eligible | fpg_eligible

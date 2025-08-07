from policyengine_us.model_api import *


class is_lifeline_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Lifeline"
    documentation = "Eligible for Lifeline phone or broadband subsidy"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/cfr/text/47/54.409"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.fcc.lifeline
        household = spm_unit.household
        is_on_tribal_land = household("is_on_tribal_land", period)
        non_tribal_lifeline_programs = add(
            spm_unit, period, p.categorical_eligibility
        )
        tribal_lifeline_programs = add(
            spm_unit, period, p.tribal_categorical_eligibility
        )
        categorically_eligible = np.where(
            is_on_tribal_land,
            np.any(tribal_lifeline_programs),
            np.any(non_tribal_lifeline_programs),
        )
        fpg_ratio = spm_unit("fcc_fpg_ratio", period)
        fpg_limit = p.fpg_limit
        fpg_eligible = fpg_ratio <= fpg_limit
        return categorically_eligible | fpg_eligible

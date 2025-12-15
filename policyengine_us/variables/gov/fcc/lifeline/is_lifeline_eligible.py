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
            tribal_lifeline_programs > 0,
            non_tribal_lifeline_programs > 0,
        )
        # Use the new unified income eligibility variable
        income_eligible = spm_unit("is_lifeline_income_eligible", period)
        return categorically_eligible | income_eligible

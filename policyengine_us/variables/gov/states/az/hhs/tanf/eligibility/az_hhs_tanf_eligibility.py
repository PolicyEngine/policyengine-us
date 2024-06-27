from policyengine_us.model_api import *


class az_hhs_tanf_eligibility(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for the Arizona Cash Assistance"
    definition_period = MONTH
    reference = "https://des.az.gov/services/child-and-family/cash-assistance/cash-assistance-ca-income-eligibility-guidelines"
    defined_for = StateCode.AZ

    def formula(spm_unit, period, parameters):
        # Judge whether the countable income exceed the 100% of Ferderal Poverty Guideline
        household_size = spm_unit("spm_unit_size", period)
        monthly_fpg = spm_unit("spm_unit_fpg", period)
        monthly_countable_earned_income = spm_unit(
            "az_tanf_earned_income", period
        )
        fpg_eligibility = monthly_countable_earned_income <= monthly_fpg
        # Judge whether the countable income exceed the Cash Assistance Payment Standard
        p = parameters(
           period
        ).gov.states.az.hhs.tanf.eligibility.payment_standard
        shelter_cost = spm_unit("housing_cost", period)
        payment_standard_threshold = where(
            shelter_cost > 0, p.high[household_size], p.low[household_size]
        )
        payment_standard_eligibility = (
           monthly_countable_earned_income <= payment_standard_threshold
        )
        
        #The family is eligible for cash assistance only when the two criteria are fitted at the same time
        return fpg_eligibility & payment_standard_eligibility
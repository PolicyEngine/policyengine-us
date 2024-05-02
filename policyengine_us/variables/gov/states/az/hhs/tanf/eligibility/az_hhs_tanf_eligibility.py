from policyengine_us.model_api import *


class az_hhs_tanf_cash_assistance_eligibility(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Arizona Cash Assistance eligibility"
    definition_period = MONTH
    reference = "https://des.az.gov/services/child-and-family/cash-assistance/cash-assistance-ca-income-eligibility-guidelines"
    defined_for = StateCode.AZ

    def formula(spm_unit, period):
        # Judge whether the countable income exceed the 100% of Ferderal Poverty Guideline
        fpg = spm_unit("spm_unit_fpg", period)
        monthly_fpg = fpg / MONTHS_IN_YEAR
        monthly_countable_earned_income = spm_unit(
            "az_tanf_hhs_earned_income", period
        )
        fpg_eligibility = monthly_countable_earned_income <= monthly_fpg
        # Judge whether the countable income exceed the Cash Assistance Payment Standard
        payment_standard = spm_unit("az_payment_standard", period)
        payment_standard_eligibility = monthly_countable_earned_income <= payment_standard
        # The family is eligible for cash assistance only when the two criteria are fitted at the same time
        return fpg_eligibility and payment_standard_eligibility

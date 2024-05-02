from policyengine_us.model_api import *


class az_hhs_tanf_cash_assistance(Variable):
    value_type = float
    entity = SPMUnit
    label = "Arizona Cash Assistance Payment"
    definition_period = MONTH
    reference = (
        "https://az.db101.org/az/programs/income_support/tanf/program2.htm"
    )
    defined_for = StateCode.AZ

    def formula(spm_unit, period):

        eligibility = spm_unit("az_hhs_tanf_eligibility", period)
        payment_threshold = spm_unit("az_payment_standard", period)
        monthly_countable_earned_income = spm_unit(
            "az_tanf_hhs_earned_income", period
        )
        cash_assistance_benifit = max_(
            payment_threshold - monthly_countable_earned_income, 0
        )
        return cash_assistance_benifit if eligibility else 0

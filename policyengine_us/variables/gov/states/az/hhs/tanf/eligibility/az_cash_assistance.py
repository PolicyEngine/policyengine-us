from policyengine_us.model_api import *


class az_cash_assistance(Variable):
    value_type = float
    entity = SPMUnit
    label = "Arizona Cash Assistance Payment"
    definition_period = MONTH
    reference = (
        "https://az.db101.org/az/programs/income_support/tanf/program2.htm"
    )
    defined_for = "az_hhs_tanf_eligible"

    def formula(spm_unit, period, parameters):
        payment_standard_threshold = spm_unit(
            "az_payment_standard_threshold", period
        )
        monthly_countable_earned_income = spm_unit(
            "az_tanf_earned_income", period
        )
        return max_(
            payment_standard_threshold - monthly_countable_earned_income, 0
        )

from policyengine_us.model_api import *


class az_cash_assistance(Variable):
    value_type = float
    entity = SPMUnit
    label = "Arizona Cash Assistance Payment"
    definition_period = MONTH
    reference = (
        "https://az.db101.org/az/programs/income_support/tanf/program2.htm"
    )
    defined_for = "az_hhs_tanf_eligibility"

    def formula(spm_unit, period, parameters):
        monthly_fpg = spm_unit("spm_unit_fpg", period)
        p = parameters(
            period
        ).gov.states.az.hhs.tanf.eligibility.payment_standard
        monthly_countable_earned_income = spm_unit(
            "az_tanf_earned_income", period
        )
        shelter_cost = spm_unit("housing_cost", period)
        payment_threshold = where(shelter_cost > 0, np.floor(p.high*monthly_fpg), np.floor(p.low*monthly_fpg))
        return max_(
            payment_threshold - monthly_countable_earned_income, 0
        )

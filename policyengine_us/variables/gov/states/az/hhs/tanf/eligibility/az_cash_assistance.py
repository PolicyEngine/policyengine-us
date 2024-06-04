from policyengine_us.model_api import *


class az_cash_assistance(Variable):
    value_type = float
    entity = SPMUnit
    label = "Arizona Cash Assistance Payment"
    definition_period = MONTH
    reference = (
        "https://az.db101.org/az/programs/income_support/tanf/program2.htm"
    )
    defined_for = StateCode.AZ

    def formula(spm_unit, period, parameters):
        household_size = spm_unit("spm_unit_size", period)
        eligibility = spm_unit("az_hhs_tanf_eligibility", period)
        monthly_countable_earned_income = spm_unit(
            "az_tanf_hhs_earned_income", period
        )
        p = parameters(
            period
        ).gov.states.az.hhs.tanf.eligibility.payment_standard
        shelter_cost = spm_unit("housing_cost", period)
        payment_standard = where(shelter_cost > 0, p.high, p.low)
        payment_threshold = payment_standard[household_size][period]
        return max_(
            payment_threshold - monthly_countable_earned_income, 0
        )

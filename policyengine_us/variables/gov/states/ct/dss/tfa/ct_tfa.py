from policyengine_us.model_api import *


class ct_tfa(Variable):
    value_type = float
    entity = SPMUnit
    label = "Connecticut Temporary Family Assistance (TFA) benefit amount"
    unit = USD
    definition_period = MONTH
    reference = "https://portal.ct.gov/dss/-/media/departments-and-agencies/dss/economic-security/ct-tanf-state-plan-2024---2026---41524-amendment.pdf?rev=f9c7a2028b6e409689d213d1966d6818&hash=9DDB6100DBC3D983F7946E33D702B2C8#page=10"
    defined_for = "ct_tfa_eligible"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ct.dss.tfa.payment.high_earnings
        # Unearned income are counted dollar for dollar against TFA benefit amount
        # https://portal.ct.gov/dss/knowledge-base/articles/cash-assistance/temporary-family-assistance?language=en_US
        payment_standard = spm_unit("ct_tfa_payment_standard", period)
        countable_unearned_income = spm_unit(
            "ct_tfa_countable_unearned_income", period
        )
        benefit_amount = max_(payment_standard - countable_unearned_income, 0)
        # When gross earnings are between 171% and 230% of FPG, reduce the benefit by 20%
        gross_earnings = spm_unit("ct_tfa_gross_earnings", period)
        fpg = spm_unit("tanf_fpg", period)
        high_income = gross_earnings >= p.rate * fpg

        return where(
            high_income,
            benefit_amount * (1 - p.reduction_rate),
            benefit_amount,
        )

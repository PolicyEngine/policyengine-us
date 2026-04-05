from policyengine_us.model_api import *


class ct_tfa(Variable):
    value_type = float
    entity = SPMUnit
    label = "Connecticut Temporary Family Assistance (TFA) benefit amount"
    unit = USD
    definition_period = MONTH
    reference = "https://portal.ct.gov/dss/-/media/departments-and-agencies/dss/state-plans-and-federal-reports/tanf-state-plan/ct-tanf-state-plan-2024---2026---41524-amendment.pdf#page=10"
    defined_for = "ct_tfa_eligible"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ct.dss.tfa.payment
        # Unearned income are counted dollar for dollar against TFA benefit amount
        # https://portal.ct.gov/dss/knowledge-base/articles/cash-assistance/temporary-family-assistance?language=en_US
        payment_standard = spm_unit("ct_tfa_payment_standard", period)
        # Per CGS § 17b-104(d), families in subsidized housing have
        # a share of the payment standard attributed as income.
        receives_housing = spm_unit("receives_housing_assistance", period.this_year)
        adjusted_standard = where(
            receives_housing,
            payment_standard * p.housing_subsidy_rate,
            payment_standard,
        )
        countable_unearned_income = spm_unit("ct_tfa_countable_unearned_income", period)
        raw_benefit = max_(adjusted_standard - countable_unearned_income, 0)
        # Per CGS § 17b-112(d), high earners have their benefit reduced.
        if p.high_earnings.in_effect:
            gross_earnings = add(spm_unit, period, ["tanf_gross_earned_income"])
            fpg = spm_unit("tanf_fpg", period)
            high_income_threshold = p.high_earnings.rate * fpg
            high_income = gross_earnings >= high_income_threshold
            reduction_multiplier = 1 - p.high_earnings.reduction_rate
            return where(
                high_income,
                raw_benefit * reduction_multiplier,
                raw_benefit,
            )
        return raw_benefit

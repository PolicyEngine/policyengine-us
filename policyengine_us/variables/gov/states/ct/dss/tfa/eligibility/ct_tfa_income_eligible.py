from policyengine_us.model_api import *


class ct_tfa_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Connecticut Temporary Family Assistance (TFA) due to income"
    definition_period = MONTH
    reference = "https://portal.ct.gov/dss/-/media/departments-and-agencies/dss/state-plans-and-federal-reports/tanf-state-plan/ct-tanf-state-plan-2024---2026---41524-amendment.pdf#page=10"
    defined_for = StateCode.CT

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ct.dss.tfa.income.recipient
        is_tanf_enrolled = spm_unit("is_tanf_enrolled", period)
        # New applicant income check
        countable_income_at_application = spm_unit(
            "ct_tfa_countable_income_at_application", period
        )
        need_standard = spm_unit("ct_tfa_need_standard", period)
        income_eligible_at_application = (
            countable_income_at_application <= need_standard
        )
        # Existing recipient income check
        # Pre 2024, gross earning <= 100% fpg
        # Starting 2024, gross earning <= 230% FPL
        gross_earnings = add(spm_unit, period, ["tanf_gross_earned_income"])
        fpg = spm_unit("tanf_fpg", period)

        fpg_limit = p.income_limit_rate * fpg
        income_eligible_at_grant_calculation = gross_earnings <= fpg_limit
        return where(
            is_tanf_enrolled,
            income_eligible_at_grant_calculation,
            income_eligible_at_application,
        )

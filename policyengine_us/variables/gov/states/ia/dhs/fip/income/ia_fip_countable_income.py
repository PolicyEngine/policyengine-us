from policyengine_us.model_api import *


class ia_fip_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Iowa FIP countable income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.IA
    reference = (
        "https://www.legis.iowa.gov/docs/iac/chapter/01-07-2026.441.41.pdf"
    )

    def formula(spm_unit, period, parameters):
        gross_earned = spm_unit("ia_fip_gross_earned_income", period)
        gross_unearned = spm_unit("ia_fip_gross_unearned_income", period)
        p = parameters(period).gov.states.ia.dhs.fip.income
        earned_income_deduction = gross_earned * p.earned_income_deduction
        remaining_earned = gross_earned - earned_income_deduction
        work_incentive = remaining_earned * p.work_incentive_disregard
        countable_earned = remaining_earned - work_incentive
        return countable_earned + gross_unearned

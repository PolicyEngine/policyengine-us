from policyengine_us.model_api import *


class ia_fip_countable_earned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Iowa FIP countable earned income"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.IA
    reference = "https://www.legis.iowa.gov/docs/iac/chapter/01-07-2026.441.41.pdf#page=19"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ia.dhs.fip.income
        gross_earned = add(spm_unit, period, ["tanf_gross_earned_income"])
        earned_income_after_deduction = gross_earned * (
            1 - p.earned_income_deduction
        )
        return earned_income_after_deduction * (1 - p.work_incentive_disregard)

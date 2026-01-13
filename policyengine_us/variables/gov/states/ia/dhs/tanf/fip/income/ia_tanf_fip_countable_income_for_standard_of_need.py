from policyengine_us.model_api import *


class ia_tanf_fip_countable_income_for_standard_of_need(Variable):
    value_type = float
    entity = SPMUnit
    label = "Iowa FIP countable income for Standard of Need test"
    unit = USD
    definition_period = MONTH
    reference = "Iowa HHS FIP Budgeting Manual Chapter 4-F"
    documentation = "https://hhs.iowa.gov/media/3972/download?inline"
    defined_for = StateCode.IA

    def formula(spm_unit, period, parameters):
        # For Standard of Need test: Gross earned income - 20% deduction
        gross_earned = spm_unit("ia_tanf_fip_gross_earned_income", period)
        earned_deduction = spm_unit(
            "ia_tanf_fip_earned_income_deduction", period
        )

        return gross_earned - earned_deduction

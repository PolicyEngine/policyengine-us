from policyengine_us.model_api import *


class ia_tanf_fip_work_incentive_deduction(Variable):
    value_type = float
    entity = SPMUnit
    label = "Iowa FIP 50% work incentive deduction"
    unit = USD
    definition_period = MONTH
    reference = "Iowa HHS FIP Budgeting Manual Chapter 4-F"
    documentation = "https://hhs.iowa.gov/media/3972/download?inline"
    defined_for = StateCode.IA

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ia.dhs.tanf.fip

        # Work incentive deduction only applies if family passes Standard of Need test
        passes_standard_of_need = spm_unit(
            "ia_tanf_fip_standard_of_need_test", period
        )

        # Apply 50% deduction to earned income after the 20% deduction
        gross_earned = spm_unit("ia_tanf_fip_gross_earned_income", period)
        earned_deduction = spm_unit(
            "ia_tanf_fip_earned_income_deduction", period
        )
        after_20_percent = gross_earned - earned_deduction

        work_incentive = (
            after_20_percent * p.deductions.work_incentive_deduction_rate
        )

        return where(passes_standard_of_need, work_incentive, 0)

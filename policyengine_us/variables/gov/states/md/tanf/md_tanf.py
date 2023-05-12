from policyengine_us.model_api import *




class md_tanf(Variable):
    value_type = float
    entity = SPMUnit
    label = "Maryland TANF"
    unit = USD
    definition_period = YEAR
    defined_for = "md_tanf_eligible"


    def formula(spm_unit, period, parameters):
        grant_standard = spm_unit("md_tanf_maximun_benefit", period)
        earned_income = spm_unit(
            "md_tanf_countable_gross_earned_income", period
        )
        earned_income_deduction = spm_unit(
            "md_tanf_gross_earned_income_deduction", period
        )
        unearned_income = spm_unit(
            "md_tanf_countable_gross_unearned_income", period
        )
        unearned_income_deduction = spm_unit(
            "md_tanf_gross_unearned_income_deduction", period
        )
        income = add(
            spm_unit,
            period,
            earned_income - earned_income_deduction,
            unearned_income - unearned_income_deduction,
        )
        return max(grant_standard - income, 0)
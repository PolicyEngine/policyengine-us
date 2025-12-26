from policyengine_us.model_api import *


class ks_tanf_countable_earned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Kansas TANF countable earned income"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/kansas/K-A-R-30-4-110",
        "https://content.dcf.ks.gov/ees/keesm/current/keesm7110.htm",
        "https://content.dcf.ks.gov/ees/keesm/current/keesm7224.htm",
    )
    defined_for = StateCode.KS

    def formula(spm_unit, period, parameters):
        # Per K.A.R. 30-4-110, KEESM 7110, and KEESM 7224:
        # Sum person-level earned income after $90 and 60% deductions,
        # then subtract dependent care expenses.
        #
        # Per KEESM 7224: Dependent care is applied after $90 and 60% disregards.
        # There is NO cap on dependent care deduction in Kansas TANF.
        earned_after_deductions = add(
            spm_unit, period, ["ks_tanf_earned_income_after_deductions"]
        )
        dependent_care = spm_unit(
            "spm_unit_pre_subsidy_childcare_expenses", period
        )
        return max_(earned_after_deductions - dependent_care, 0)

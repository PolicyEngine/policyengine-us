from policyengine_us.model_api import *


class tx_tanf_countable_earned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Texas TANF countable earned income"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.hhs.texas.gov/handbooks/texas-works-handbook/a-1340-income-limits",
        "https://www.law.cornell.edu/regulations/texas/1-TAC-372-605",
    )
    defined_for = StateCode.TX

    def formula(spm_unit, period, parameters):
        # Sum person-level earned income after work expense and disregards
        earned_after_disregards = spm_unit(
            "tx_tanf_earned_income_after_disregard_person", period
        )

        # Apply dependent care deduction (per § 372.409 (a)(3))
        dependent_care_deduction = spm_unit(
            "tx_tanf_dependent_care_deduction", period
        )

        # Countable earned income after all deductions
        return max_(earned_after_disregards - dependent_care_deduction, 0)

from policyengine_us.model_api import *


class ma_eaedc_dependent_care_deduction_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for the Massachusetts EAEDC dependent care deduction"
    definition_period = MONTH
    defined_for = "ma_eaedc_eligible_caretaker_family"
    reference = "https://www.law.cornell.edu/regulations/massachusetts/106-CMR-704-275#(B)"

    def formula(spm_unit, period, parameters):
        # If earned income lower than standard assistance, then no dependent care expense deduction.
        gross_earned_income = add(spm_unit, period, ["ma_tcap_gross_earned_income", "ma_tcap_gross_unearned_income"])
        standard_assistance = spm_unit("ma_eaedc_standard_assistance", period)

        return gross_earned_income >= standard_assistance

from policyengine_us.model_api import *


class ma_eaedc_dependent_care_deduction(Variable):
    value_type = float
    entity = SPMUnit
    label = "Massachusetts EAEDC dependent care deduction"
    unit = USD
    definition_period = YEAR
    defined_for = "ma_eaedc_dependent_care_deduction_eligible"
    reference = "https://www.law.cornell.edu/regulations/massachusetts/106-CMR-704-275#(B)"

    def formula(spm_unit, period, parameters):
        total_amount = add(
            spm_unit, period, ["ma_eaedc_dependent_care_deduction_person"]
        )
        dependent_care_expense = add(spm_unit, period, ["care_expenses"])
        return min_(dependent_care_expense, total_amount)

from policyengine_us.model_api import *


class ma_tafdc_earned_income_after_deductions(Variable):
    value_type = float
    unit = USD
    entity = SPMUnit
    label = "Massachusetts Temporary Assistance for Families with Dependent Children (TAFDC) earned income after deductions"
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/regulations/massachusetts/106-CMR-704-280"
    )
    defined_for = StateCode.MA

    def formula(spm_unit, period, parameters):
        # The 50% disregard only applies the unit has received TAFDC in the past 4 months and
        # is re-applying due to temporary ineligibility
        gross_earned_income = add(
            spm_unit, period, ["ma_tcap_gross_earned_income"]
        )
        deductions = add(
            spm_unit,
            period,
            [
                "ma_tafdc_work_related_expense_deduction",
                "ma_tafdc_dependent_care_deduction",
            ],
        )
        return max_(gross_earned_income - deductions, 0)

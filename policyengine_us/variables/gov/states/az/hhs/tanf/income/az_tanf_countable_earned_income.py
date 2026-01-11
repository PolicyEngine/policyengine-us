from policyengine_us.model_api import *


class az_tanf_countable_earned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Arizona TANF countable earned income"
    unit = USD
    definition_period = MONTH
    reference = "https://dbmefaapolicy.azdes.gov/index.html#page/FAA5/CA_Benefit_Determination.html#wwpID0E0NQB0FA"
    defined_for = StateCode.AZ

    def formula(spm_unit, period, parameters):
        # Sum person-level earned income after $90 flat and 30% disregards
        after_disregards = add(
            spm_unit,
            period,
            ["az_tanf_earned_income_after_disregard_person"],
        )
        # Subtract dependent care deduction
        care_deduction = spm_unit("az_tanf_dependent_care_deduction", period)
        return max_(after_disregards - care_deduction, 0)

from policyengine_us.model_api import *


class is_presumption_of_abuse(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Is presumption of abuse"
    definition_period = MONTH
    reference = "https://www.cacb.uscourts.gov/sites/cacb/files/documents/forms/122A2.pdf#page=8"
    documentation = "Line 39-xx in form 122A-2"

    def formula(spm_unit, period, parameters):
        adjusted_monthly_income = spm_unit(
            "chapter_7_bankruptcy_adjust_monthly_income", period
        )
        total_deductions = spm_unit(
            "chapter_7_bankruptcy_total_deductions", period
        )
        monthly_disposable_income = adjusted_monthly_income - total_deductions
        monthly_disposable_income_60_months = (
            monthly_disposable_income * MONTHS_IN_YEAR * 5
        )
        return monthly_disposable_income_60_months > 15150
        # if monthly_disposable_income_60_months < 9075, false,
        # if monthly_disposable_income_60_months > 15150, true
        # if 9075 < monthly_disposable_income_60_months < 15150, go line 41
            ##

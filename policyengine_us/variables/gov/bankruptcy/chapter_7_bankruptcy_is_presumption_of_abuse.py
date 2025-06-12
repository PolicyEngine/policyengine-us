from policyengine_us.model_api import *


class chapter_7_bankruptcy_is_presumption_of_abuse(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Chapter 7 Bankruptcy is presumption of abuse"
    definition_period = MONTH
    reference = "https://www.cacb.uscourts.gov/sites/cacb/files/documents/forms/122A2.pdf#page=8"
    documentation = "Line 39-xx in form 122A-2"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.bankruptcy.presumption_abuse

        adjusted_monthly_income = spm_unit(
            "chapter_7_bankruptcy_adjusted_monthly_income", period
        )
        total_deductions = spm_unit(
            "chapter_7_bankruptcy_total_deductions", period
        )
        monthly_disposable_income = adjusted_monthly_income - total_deductions
        total_disposable_income = (
            monthly_disposable_income * MONTHS_IN_YEAR * 5
        )
        nonpriority_unsecured_debt = spm_unit(
            "chapter_7_bankruptcy_nonpriority_unsecured_debt", period
        )
        adjust_nonpriority_unsecured_debt = nonpriority_unsecured_debt * p.rate
        is_income_high = total_disposable_income > p.amount.higher
        is_income_in_between = (
            p.amount.lower < total_disposable_income < p.amount.higher
        )
        is_income_exceeding_debt = (
            total_disposable_income >= adjust_nonpriority_unsecured_debt
        )

        return is_income_high | (
            is_income_in_between & is_income_exceeding_debt
        )

from policyengine_us.model_api import *


class pa_tanf_countable_earned_income(Variable):
    value_type = float
    entity = Person
    label = "Pennsylvania TANF countable earned income"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.PA
    reference = "55 Pa. Code Section 183.94 - Eligibility for TANF earned income deductions"
    documentation = "Final countable earned income after all deductions and disregards, including the work expense deduction applied after the fifty percent disregard. This amount is used in TANF eligibility and benefit calculations. https://www.pacodeandbulletin.gov/Display/pacode?file=/secure/pacode/data/055/chapter183/s183.94.html"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.pa.dhs.tanf.earned_income

        # Start with income after 50% disregard
        income_after_disregard = person(
            "pa_tanf_earned_income_after_disregard", period
        )

        # Subtract work expense deduction ($200 for all working TANF families)
        work_expense = p.work_expense_deduction
        has_earnings = person("pa_tanf_gross_earned_income", period) > 0

        # Work expense deduction only applies if person has earned income
        deduction = where(has_earnings, work_expense, 0)

        # Final countable earned income (cannot be negative)
        return max_(income_after_disregard - deduction, 0)

from policyengine_us.model_api import *


class hi_dependent_care_benefits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Hawaii Dependent Care Benefits"
    defined_for = StateCode.HI
    unit = USD
    definition_period = YEAR
    reference = "https://files.hawaii.gov/tax/legal/hrs/hrs_235.pdf#page=40"

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.hi.tax.income.credits.cdcc.dependent_care_benefits
        dcb_amount = tax_unit("dependent_care_benefits", period)
        qualified_expense_amount = tax_unit(
            "tax_unit_childcare_expenses", period
        )
        # married persons must file a joint return to claim the credit
        # if single, the min will be his/her income
        capped_expenses = min_(dcb_amount, qualified_expense_amount)
        min_head_spouse_earned = tax_unit("hi_min_head_spouse_earned", period)
        earned_income_cap = min_(capped_expenses, min_head_spouse_earned)
        filing_status = tax_unit("filing_status", period)
        dcb_baseline = p.earned_income_cap[filing_status]
        deductible_benefit = min_(earned_income_cap, dcb_baseline)
        # excluded_benefit = 0 since we ignore line 12
        qualified_num = tax_unit("count_cdcc_eligible", period)
        expenses_amount = p.expense_floor.calc(qualified_num)
        net_expenses = max_(0, expenses_amount - deductible_benefit)
        return min_(net_expenses, qualified_expense_amount)

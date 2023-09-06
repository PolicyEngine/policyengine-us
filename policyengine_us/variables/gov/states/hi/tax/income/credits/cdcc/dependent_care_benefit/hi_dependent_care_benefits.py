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
        p = parameters(period).gov.states.hi.tax.income.credits.cdcc
        dcb_amount = tax_unit("dependent_care_benefits", period)
        qualified_expense_amount = tax_unit(
            "tax_unit_childcare_expenses", period
        )
        # married persons must fi le a joint return to claim the credit
        # if single, the min will be his/her income
        min_head_spouse_earned = tax_unit("hi_min_head_spouse_earned", period)
        min_benefit = min_(
            dcb_amount, qualified_expense_amount, min_head_spouse_earned
        )
        filing_status = tax_unit("filing_status", period)
        dcb_baseline = p.dependent_care_benefits[filing_status]
        deductible_benefit = min_(min_benefit, dcb_baseline)
        # excluded_benefit = 0 since we ignore line 12
        # taxable_benefit = max_(0, dcb_amount - excluded_benefit) #never use in further calculation
        qualified_num = tax_unit("count_cdcc_eligible", period)
        expenses_amount = select(
            [
                qualified_num <= 1,
                qualified_num > 1,
            ],
            [
                p.expense_cap.one_child,
                p.expense_cap.two_or_more_child,
            ],
        )
        net_expenses = max_(0, expenses_amount - deductible_benefit)
        return min_(net_expenses, qualified_expense_amount)

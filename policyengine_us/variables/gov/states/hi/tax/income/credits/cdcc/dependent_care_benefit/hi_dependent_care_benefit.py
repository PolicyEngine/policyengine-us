from policyengine_us.model_api import *


class hi_dcb(Variable):
    value_type = float
    entity = TaxUnit
    label = "Hawaii Dependent Care Benefits"
    defined_for = StateCode.HI
    unit = USD
    definition_period = YEAR
    reference = "https://files.hawaii.gov/tax/legal/hrs/hrs_235.pdf#page=40"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.hi.tax.income.credits.cdcc
        # line 2
        dcb_amount = tax_unit("hi_dcb_amount", period)
        # skip line 3,4, so line 5 = line 2
        # line 6
        qualified_expense_amount = tax_unit(
            "hi_qualified_expense_amount", period
        )
        # line 8
        # line 9
        # for student/disable cases, can't find latest instruction
        min_head_spouse_earned = tax_unit("min_head_spouse_earned", period)
        # line 10
        min_benefit = min_(
            dcb_amount, qualified_expense_amount, min_head_spouse_earned
        )
        # line 11
        filing_status = tax_unit("filing_status", period)
        status = filing_status.possible_values
        line11 = select(
            [
                filing_status == status.SEPARATE,
                filing_status != status.SEPARATE,
            ],
            [
                p.dependent_care_benefit.amount.separate,  # spouse income??
                p.dependent_care_benefit.amount.not_separate,
            ],
        )
        # skip line 12, then line 13 = line 5
        # line 14
        deductible_benefit = min_(dcb_amount, line11)
        # line 15
        excluded_benefit = max_(
            0, min_(min_benefit, line11) - deductible_benefit
        )
        # line 16
        taxable_benefit = max_(0, dcb_amount - excluded_benefit)
        # line 17
        qualified_num = tax_unit("count_cdcc_eligible", period)
        expenses_amount = select(
            [
                qualified_num == 1,
                qualified_num > 1,
            ],
            [
                p.amount.one_child_dependent,
                p.amount.two_or_more_child_dependent,
            ],
        )
        # line 18
        line18 = deductible_benefit + excluded_benefit
        # line 19
        line19 = expenses_amount - line18
        if line19 <= 0:
            print("You can not take this credit!")
            return
        # line 22
        return min_(line19, tax_unit("tax_unit_childcare_expenses", period))
